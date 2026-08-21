#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import LambdaLR
from transformers import GPT2Config, GPT2LMHeadModel, get_cosine_schedule_with_warmup

from false_friend_lab.config import load_config
from false_friend_lab.remap import (
    TargetLexicalRemapper,
    apply_causal_vocab_mask,
    initialize_alias_rows_identically,
)
from false_friend_lab.sampling import language_plan, make_language_rngs, make_plan_rng, sample_chunk


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def model_fingerprint(model: torch.nn.Module) -> str:
    h = hashlib.sha256()
    with torch.no_grad():
        for name, tensor in model.state_dict().items():
            h.update(name.encode("utf-8"))
            h.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def make_optimizer(model, cfg: dict):
    return AdamW(
        model.parameters(),
        lr=float(cfg["learning_rate"]),
        betas=tuple(cfg.get("betas", [0.9, 0.95])),
        weight_decay=float(cfg.get("weight_decay", 0.1)),
    )


def make_scheduler(optimizer, cfg: dict, max_updates: int):
    kind = cfg.get("lr_schedule", "cosine")
    warmup = int(cfg.get("warmup_updates", cfg.get("warmup_steps", 0)))
    if kind == "constant":
        if warmup:
            raise ValueError("constant schedule for causal path experiment requires warmup_updates=0")
        return LambdaLR(optimizer, lr_lambda=lambda _: 1.0)
    if kind == "cosine":
        return get_cosine_schedule_with_warmup(optimizer, warmup, max_updates)
    raise ValueError(f"unknown lr_schedule={kind}")


def sample_microbatch(streams, masks, remapper, langs, block, rngs, device):
    rows = []
    for lang in langs:
        ids, lexical = sample_chunk(streams[lang], masks[lang], block, rngs[lang])
        rows.append(remapper.map_ids(ids.tolist(), lang, lexical.tolist()))
    return torch.tensor(rows, dtype=torch.long, device=device)


def causal_lm_loss(model, batch: torch.Tensor, remapper: TargetLexicalRemapper) -> torch.Tensor:
    logits = model(input_ids=batch, use_cache=False).logits
    shift_logits = logits[:, :-1, :].contiguous()
    shift_labels = batch[:, 1:].contiguous()
    shift_logits = apply_causal_vocab_mask(shift_logits, shift_labels, remapper).float()
    return F.cross_entropy(
        shift_logits.view(-1, shift_logits.size(-1)),
        shift_labels.reshape(-1),
    )


def save_checkpoint(model, out: Path, update: int, meta: dict) -> None:
    ckpt = out / f"checkpoint-{update:07d}"
    ckpt.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(ckpt, safe_serialization=True)
    (ckpt / "run_meta.json").write_text(
        json.dumps({**meta, "update": update, "step": update}, indent=2), encoding="utf-8"
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--condition", choices=["shared", "split"], required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--schedule", default=None)
    p.add_argument("--output", default=None)
    args = p.parse_args()

    cfg = load_config(args.config)
    tcfg = cfg["train"]
    if not torch.cuda.is_available():
        raise RuntimeError("scientific training requires one CUDA GPU")
    if torch.cuda.device_count() != 1:
        raise RuntimeError(
            "expose exactly one GPU per run with CUDA_VISIBLE_DEVICES; independent runs are the parallelism unit"
        )
    device = torch.device("cuda:0")

    data_dir = Path(cfg["data"]["processed_dir"])
    meta = json.load(open(data_dir / "metadata.json", encoding="utf-8"))
    if int(meta.get("schema_version", 0)) < 3:
        raise RuntimeError("re-run scripts/prepare.py with audited schema v3")
    targets = pd.read_csv(data_dir / "targets.csv")
    target_ids = sorted(set(map(int, targets.compact_token_id)))
    remapper = TargetLexicalRemapper(int(meta["compact_vocab_size"]), target_ids, args.condition, "de")

    schedule = args.schedule or tcfg.get("schedule", "joint")
    phase = int(tcfg.get("phase_updates", 0))
    tail = int(tcfg.get("balanced_tail_updates", 0))
    max_updates = int(tcfg.get("max_updates", tcfg.get("max_steps", 0)))
    if max_updates <= 0:
        raise ValueError("max_updates must be positive")
    if schedule in {"en_then_de", "de_then_en"}:
        if max_updates != 2 * phase + tail:
            raise ValueError("path max_updates must equal 2*phase_updates + balanced_tail_updates")
        if tcfg.get("lr_schedule") != "constant" or int(tcfg.get("warmup_updates", 0)) != 0:
            raise ValueError("path comparison requires constant LR and zero warmup")
        if not bool(tcfg.get("reset_optimizer_at_balanced_tail", False)):
            raise ValueError("path comparison requires optimizer reset at common-tail boundary")

    out = Path(args.output or cfg["experiment"]["output_root"]) / args.condition / f"seed_{args.seed}" / schedule
    out.mkdir(parents=True, exist_ok=True)

    # Same seed means the entire step-0 shared/split model is identical.
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    mcfg = cfg["model"]
    model = GPT2LMHeadModel(
        GPT2Config(
            vocab_size=remapper.vocab_size,
            n_positions=int(mcfg["block_size"]),
            n_ctx=int(mcfg["block_size"]),
            n_embd=int(mcfg["n_embd"]),
            n_layer=int(mcfg["n_layer"]),
            n_head=int(mcfg["n_head"]),
            resid_pdrop=float(mcfg.get("dropout", 0.0)),
            embd_pdrop=float(mcfg.get("dropout", 0.0)),
            attn_pdrop=float(mcfg.get("dropout", 0.0)),
            bos_token_id=int(meta["eos_compact_id"]),
            eos_token_id=int(meta["eos_compact_id"]),
            tie_word_embeddings=True,
        )
    )
    initialize_alias_rows_identically(model, remapper)
    init_sha256 = model_fingerprint(model)
    model.to(device)
    if tcfg.get("gradient_checkpointing", False):
        model.gradient_checkpointing_enable()

    micro = int(tcfg.get("micro_batch_size", tcfg.get("per_device_batch_size", 8)))
    accum = int(tcfg.get("gradient_accumulation_steps", 1))
    if micro <= 0 or accum <= 0:
        raise ValueError("micro_batch_size and gradient_accumulation_steps must be positive")
    effective = micro * accum
    save_every = int(tcfg.get("save_every_updates", tcfg.get("save_every", 1000)))
    log_every = int(tcfg.get("log_every_updates", tcfg.get("log_every", 50)))
    if save_every <= 0 or log_every <= 0:
        raise ValueError("save/log intervals must be positive")
    optimizer = make_optimizer(model, tcfg)
    scheduler = make_scheduler(optimizer, tcfg, max_updates)
    grad_clip = float(tcfg.get("grad_clip", 1.0))
    block = int(mcfg["block_size"])

    streams = {lang: np.load(data_dir / f"train_{lang}.npy", mmap_mode="r") for lang in ("en", "de")}
    masks = {
        lang: np.load(data_dir / f"train_{lang}_lexical_mask.npy", mmap_mode="r")
        for lang in ("en", "de")
    }
    rngs = make_language_rngs(args.seed)
    plan_rng = make_plan_rng(args.seed)

    props = torch.cuda.get_device_properties(0)
    config_hash = hashlib.sha256(Path(args.config).read_bytes()).hexdigest()
    run_meta = {
        "condition": args.condition,
        "seed": args.seed,
        "schedule": schedule,
        "config": cfg,
        "config_hash": config_hash,
        "data_fingerprint": meta["data_fingerprint"],
        "data_schema_version": int(meta["schema_version"]),
        "base_vocab_size": int(meta["compact_vocab_size"]),
        "effective_vocab_size": remapper.vocab_size,
        "active_softmax_rows_per_position": int(meta["compact_vocab_size"]),
        "micro_batch_size": micro,
        "gradient_accumulation_steps": accum,
        "effective_batch_size": effective,
        "training_gpu_name": props.name,
        "training_gpu_total_memory": int(props.total_memory),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
        "git_commit": git_commit(),
        "init_sha256": init_sha256,
        "torch_version": torch.__version__,
        "cuda_version": torch.version.cuda,
        "alias_rows_copied_from_base_at_step0": True,
        "softmax_alias_policy": "shared=all_alias_masked; split=one-in-one-out only at exact DE target labels",
        "exact_lexical_mask_only": True,
    }
    (out / "run_meta.json").write_text(json.dumps(run_meta, indent=2), encoding="utf-8")
    save_checkpoint(model, out, 0, run_meta)

    use_bf16 = str(tcfg.get("mixed_precision", "bf16")).lower() == "bf16"
    if use_bf16 and not torch.cuda.is_bf16_supported():
        raise RuntimeError("config requests bf16 but this GPU/runtime does not report bf16 support")
    autocast_dtype = torch.bfloat16 if use_bf16 else torch.float32
    reset_at = 2 * phase if schedule in {"en_then_de", "de_then_en"} else -1
    reset_optimizer = bool(tcfg.get("reset_optimizer_at_balanced_tail", False))

    model.train()
    running = 0.0
    for update in range(max_updates):
        if reset_optimizer and update == reset_at:
            # Remove optimizer-state recency from the common-tail path test.
            optimizer = make_optimizer(model, tcfg)
            scheduler = make_scheduler(optimizer, tcfg, max_updates - update)

        optimizer.zero_grad(set_to_none=True)
        update_loss = 0.0
        for _micro_step in range(accum):
            langs = language_plan(schedule, update, phase, micro, plan_rng)
            batch = sample_microbatch(streams, masks, remapper, langs, block, rngs, device)
            with torch.autocast(device_type="cuda", dtype=autocast_dtype, enabled=use_bf16):
                loss = causal_lm_loss(model, batch, remapper)
            (loss / accum).backward()
            update_loss += float(loss.detach()) / accum

        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()
        scheduler.step()
        completed = update + 1
        running += update_loss

        if completed % log_every == 0:
            avg = running / log_every
            lr = optimizer.param_groups[0]["lr"]
            line = {"update": completed, "loss": avg, "ppl": math.exp(min(avg, 20)), "lr": lr}
            print(json.dumps(line), flush=True)
            with open(out / "train_log.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(line) + "\n")
            running = 0.0

        if completed % save_every == 0 or completed == max_updates:
            save_checkpoint(model, out, completed, run_meta)


if __name__ == "__main__":
    main()
