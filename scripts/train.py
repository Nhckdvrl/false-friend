#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import random
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
import torch
from accelerate import Accelerator
from torch.optim import AdamW
from transformers import GPT2Config, GPT2LMHeadModel, get_cosine_schedule_with_warmup

from false_friend_lab.config import load_config
from false_friend_lab.remap import TargetLexicalRemapper


def language_plan(schedule: str, step: int, cfg: dict, batch_size: int, rng: random.Random) -> list[str]:
    """Return an exact per-batch language plan.

    Balanced phases use exactly half EN and half DE (then shuffle), so the two
    path-dependence curricula can finish with exactly matched cumulative token
    counts rather than merely matching them in expectation.
    """
    if batch_size % 2 != 0 and schedule in {"joint", "en_then_de", "de_then_en"}:
        raise ValueError("balanced schedules require an even per-device batch size")

    def balanced() -> list[str]:
        plan = ["en"] * (batch_size // 2) + ["de"] * (batch_size // 2)
        rng.shuffle(plan)
        return plan

    if schedule == "joint":
        return balanced()
    if schedule == "en_only":
        return ["en"] * batch_size
    if schedule == "de_only":
        return ["de"] * batch_size
    if schedule in {"en_then_de", "de_then_en"}:
        phase = int(cfg["train"].get("phase_steps", 0))
        tail = int(cfg["train"].get("balanced_tail_steps", 0))
        if phase <= 0:
            raise ValueError("phase_steps must be >0 for sequential schedules")
        first, second = ("en", "de") if schedule == "en_then_de" else ("de", "en")
        if step < phase:
            return [first] * batch_size
        if step < 2 * phase:
            return [second] * batch_size
        if tail and step < 2 * phase + tail:
            return balanced()
        return balanced()
    raise ValueError(f"unknown schedule: {schedule}")


def sample_chunk(stream: np.ndarray, block_size: int, rng: np.random.Generator) -> np.ndarray:
    if len(stream) <= block_size + 1:
        raise ValueError("training stream is too small for configured block_size")
    start = int(rng.integers(0, len(stream) - block_size - 1))
    return np.asarray(stream[start : start + block_size], dtype=np.int64)


def sample_batch(
    streams: Dict[str, np.ndarray],
    remapper: TargetLexicalRemapper,
    batch_size: int,
    block_size: int,
    schedule: str,
    step: int,
    cfg: dict,
    py_rng: random.Random,
    np_rng: np.random.Generator,
    device: torch.device,
) -> torch.Tensor:
    rows = []
    for lang in language_plan(schedule, step, cfg, batch_size, py_rng):
        chunk = sample_chunk(streams[lang], block_size, np_rng)
        mapped = remapper.map_ids(chunk.tolist(), lang)
        rows.append(mapped)
    return torch.tensor(rows, dtype=torch.long, device=device)


def save_checkpoint(accelerator: Accelerator, model, optimizer, scheduler, output: Path, step: int, meta: dict) -> None:
    accelerator.wait_for_everyone()
    ckpt = output / f"checkpoint-{step:07d}"
    if accelerator.is_main_process:
        ckpt.mkdir(parents=True, exist_ok=True)
        unwrapped = accelerator.unwrap_model(model)
        unwrapped.save_pretrained(ckpt, safe_serialization=True)
        with open(ckpt / "run_meta.json", "w", encoding="utf-8") as f:
            json.dump({**meta, "step": step}, f, indent=2)
    accelerator.wait_for_everyone()
    accelerator.save_state(output_dir=str(ckpt / "accelerate_state"))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--condition", choices=["shared", "split"], required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--schedule", default=None)
    p.add_argument("--output", default=None)
    args = p.parse_args()

    cfg = load_config(args.config)
    data_dir = Path(cfg["data"]["processed_dir"])
    meta = json.load(open(data_dir / "metadata.json", "r", encoding="utf-8"))
    targets = pd.read_csv(data_dir / "targets.csv")
    target_ids = sorted(set(map(int, targets["compact_token_id"].tolist())))
    base_vocab = int(meta["compact_vocab_size"])
    remapper = TargetLexicalRemapper(base_vocab, target_ids, args.condition, split_lang="de")

    schedule_name = args.schedule or cfg["train"].get("schedule", "joint")
    run_name = f"{args.condition}/seed_{args.seed}/{schedule_name}"
    output = Path(args.output or cfg["experiment"]["output_root"]) / run_name
    output.mkdir(parents=True, exist_ok=True)

    mixed_precision = cfg["train"].get("mixed_precision", "bf16")
    accelerator = Accelerator(
        mixed_precision=mixed_precision,
        gradient_accumulation_steps=int(cfg["train"].get("gradient_accumulation_steps", 1)),
    )
    torch.manual_seed(args.seed + accelerator.process_index)
    np.random.seed(args.seed + accelerator.process_index)
    random.seed(args.seed + accelerator.process_index)

    model_cfg = GPT2Config(
        vocab_size=remapper.vocab_size,
        n_positions=int(cfg["model"]["block_size"]),
        n_ctx=int(cfg["model"]["block_size"]),
        n_embd=int(cfg["model"]["n_embd"]),
        n_layer=int(cfg["model"]["n_layer"]),
        n_head=int(cfg["model"]["n_head"]),
        resid_pdrop=float(cfg["model"].get("dropout", 0.0)),
        embd_pdrop=float(cfg["model"].get("dropout", 0.0)),
        attn_pdrop=float(cfg["model"].get("dropout", 0.0)),
        bos_token_id=int(meta["eos_compact_id"]),
        eos_token_id=int(meta["eos_compact_id"]),
        tie_word_embeddings=True,
    )
    model = GPT2LMHeadModel(model_cfg)
    if cfg["train"].get("gradient_checkpointing", False):
        model.gradient_checkpointing_enable()

    optimizer = AdamW(
        model.parameters(),
        lr=float(cfg["train"]["learning_rate"]),
        betas=tuple(cfg["train"].get("betas", [0.9, 0.95])),
        weight_decay=float(cfg["train"].get("weight_decay", 0.1)),
    )
    max_steps = int(cfg["train"]["max_steps"])
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(cfg["train"].get("warmup_steps", 500)),
        num_training_steps=max_steps,
    )
    model, optimizer, scheduler = accelerator.prepare(model, optimizer, scheduler)

    streams = {
        "en": np.load(data_dir / "train_en.npy", mmap_mode="r"),
        "de": np.load(data_dir / "train_de.npy", mmap_mode="r"),
    }
    block_size = int(cfg["model"]["block_size"])
    device_bs = int(cfg["train"]["per_device_batch_size"])
    py_rng = random.Random(args.seed * 10_000 + accelerator.process_index)
    np_rng = np.random.default_rng(args.seed * 10_000 + accelerator.process_index)
    log_every = int(cfg["train"].get("log_every", 50))
    save_every = int(cfg["train"].get("save_every", 1000))
    grad_clip = float(cfg["train"].get("grad_clip", 1.0))

    run_meta = {
        "condition": args.condition,
        "seed": args.seed,
        "schedule": schedule_name,
        "config": cfg,
        "data_metadata": meta,
        "base_vocab_size": base_vocab,
        "effective_vocab_size": remapper.vocab_size,
        "n_target_alias_rows": len(target_ids),
        "world_size": accelerator.num_processes,
    }
    if accelerator.is_main_process:
        with open(output / "run_meta.json", "w", encoding="utf-8") as f:
            json.dump(run_meta, f, indent=2)

    model.train()
    running = 0.0
    for step in range(1, max_steps + 1):
        batch = sample_batch(
            streams,
            remapper,
            device_bs,
            block_size,
            schedule_name,
            step - 1,
            cfg,
            py_rng,
            np_rng,
            accelerator.device,
        )
        with accelerator.accumulate(model):
            out = model(input_ids=batch, labels=batch, use_cache=False)
            loss = out.loss
            accelerator.backward(loss)
            if accelerator.sync_gradients:
                accelerator.clip_grad_norm_(model.parameters(), grad_clip)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad(set_to_none=True)

        gathered = accelerator.gather(loss.detach().float().reshape(1)).mean().item()
        running += gathered
        if accelerator.is_main_process and step % log_every == 0:
            avg = running / log_every
            lr = scheduler.get_last_lr()[0]
            print(f"step={step} loss={avg:.4f} ppl={math.exp(min(avg, 20)):.2f} lr={lr:.3e}", flush=True)
            with open(output / "train_log.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps({"step": step, "loss": avg, "lr": lr}) + "\n")
            running = 0.0

        if step % save_every == 0 or step == max_steps:
            save_checkpoint(accelerator, model, optimizer, scheduler, output, step, run_meta)


if __name__ == "__main__":
    main()
