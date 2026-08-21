#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, math, os, random, subprocess
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
import pandas as pd
import torch
from torch.optim import AdamW
from transformers import GPT2Config, GPT2LMHeadModel, get_cosine_schedule_with_warmup
from false_friend_lab.config import load_config
from false_friend_lab.remap import TargetLexicalRemapper, initialize_alias_rows_from_base


def git_commit() -> str:
    try: return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception: return "unknown"


def model_fingerprint(model: torch.nn.Module) -> str:
    h = hashlib.sha256()
    with torch.no_grad():
        for name, tensor in model.state_dict().items():
            h.update(name.encode()); h.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def balanced_plan(batch_size: int, seed: int, update: int, micro: int) -> list[str]:
    if batch_size % 2: raise ValueError("balanced batches require even micro_batch_size")
    plan = ["en"] * (batch_size // 2) + ["de"] * (batch_size // 2)
    rng = random.Random(seed * 1_000_003 + update * 1009 + micro); rng.shuffle(plan); return plan


def language_plan(schedule: str, update: int, micro: int, cfg: dict, batch_size: int, seed: int) -> list[str]:
    if schedule == "joint": return balanced_plan(batch_size, seed, update, micro)
    if schedule == "en_only": return ["en"] * batch_size
    if schedule == "de_only": return ["de"] * batch_size
    if schedule in {"en_then_de", "de_then_en"}:
        phase = int(cfg["train"].get("phase_updates", 0))
        if phase <= 0: raise ValueError("phase_updates must be > 0 for sequential schedules")
        first, second = ("en", "de") if schedule == "en_then_de" else ("de", "en")
        if update < phase: return [first] * batch_size
        if update < 2 * phase: return [second] * batch_size
        return balanced_plan(batch_size, seed, update, micro)
    raise ValueError(f"unknown schedule: {schedule}")


def sample_chunk(stream: np.ndarray, mask: np.ndarray, block_size: int, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    if len(stream) != len(mask): raise ValueError("stream/mask length mismatch")
    if len(stream) <= block_size + 1: raise ValueError("training stream too small")
    start = int(rng.integers(0, len(stream) - block_size))
    return np.asarray(stream[start:start + block_size], dtype=np.int64), np.asarray(mask[start:start + block_size], dtype=np.uint8)


def sample_batch(streams: Dict[str,np.ndarray], masks: Dict[str,np.ndarray], remapper: TargetLexicalRemapper,
                 micro_batch_size: int, block_size: int, schedule: str, update: int, micro: int,
                 cfg: dict, seed: int, rngs: Dict[str,np.random.Generator], device: torch.device) -> torch.Tensor:
    rows=[]
    for lang in language_plan(schedule, update, micro, cfg, micro_batch_size, seed):
        ids, exact = sample_chunk(streams[lang], masks[lang], block_size, rngs[lang])
        rows.append(remapper.map_ids(ids.tolist(), lang, exact.tolist()))
    return torch.tensor(rows, dtype=torch.long, device=device)


def make_optimizer(model, cfg):
    return AdamW(model.parameters(), lr=float(cfg["train"]["learning_rate"]), betas=tuple(cfg["train"].get("betas", [0.9,0.95])), weight_decay=float(cfg["train"].get("weight_decay",0.1)))


def make_scheduler(optimizer, cfg, max_updates):
    kind = str(cfg["train"].get("lr_schedule", "cosine")); warm = int(cfg["train"].get("warmup_updates", 0))
    if kind == "constant":
        if warm != 0: raise ValueError("constant LR path experiments require warmup_updates=0")
        return torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0)
    if kind == "cosine": return get_cosine_schedule_with_warmup(optimizer, warm, max_updates)
    raise ValueError(f"unknown lr_schedule={kind}")


def save_checkpoint(model, output: Path, update: int, meta: dict):
    ckpt = output / f"checkpoint-{update:07d}"; ckpt.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(ckpt, safe_serialization=True)
    with open(ckpt / "run_meta.json", "w", encoding="utf-8") as f: json.dump({**meta, "update": int(update), "step": int(update)}, f, indent=2)


def main():
    p=argparse.ArgumentParser(description="Single-GPU controlled bilingual causal-LM training")
    p.add_argument("--config",required=True); p.add_argument("--condition",choices=["shared","split"],required=True); p.add_argument("--seed",type=int,required=True); p.add_argument("--schedule",default=None); p.add_argument("--output",default=None); args=p.parse_args()
    if not torch.cuda.is_available(): raise RuntimeError("scientific training requires one explicitly selected CUDA GPU")
    if torch.cuda.device_count()!=1: raise RuntimeError(f"expected exactly one visible GPU, found {torch.cuda.device_count()}")
    device=torch.device("cuda:0"); torch.set_float32_matmul_precision("high"); torch.backends.cuda.matmul.allow_tf32=True
    cfg=load_config(args.config); data_dir=Path(cfg["data"]["processed_dir"]); meta=json.load(open(data_dir/"metadata.json",encoding="utf-8"))
    if int(meta.get("schema_version",0))<2 or not meta.get("strict_exact_lexical_mask") or not meta.get("pair_level_holdout"): raise RuntimeError("processed data is pre-hardening; rerun scripts/prepare.py")
    targets=pd.read_csv(data_dir/"targets.csv"); target_ids=sorted(set(map(int,targets.compact_token_id.tolist()))); remapper=TargetLexicalRemapper(int(meta["compact_vocab_size"]),target_ids,args.condition,split_lang="de")
    schedule=args.schedule or cfg["train"].get("schedule","joint"); max_updates=int(cfg["train"]["max_updates"]); micro_bs=int(cfg["train"]["micro_batch_size"]); grad_accum=int(cfg["train"].get("gradient_accumulation_steps",1)); block_size=int(cfg["model"]["block_size"])
    output=Path(args.output or cfg["experiment"]["output_root"])/f"{args.condition}/seed_{args.seed}/{schedule}"; output.mkdir(parents=True,exist_ok=True)

    torch.manual_seed(args.seed); np.random.seed(args.seed); random.seed(args.seed)
    model_cfg=GPT2Config(vocab_size=remapper.vocab_size,n_positions=block_size,n_ctx=block_size,n_embd=int(cfg["model"]["n_embd"]),n_layer=int(cfg["model"]["n_layer"]),n_head=int(cfg["model"]["n_head"]),resid_pdrop=float(cfg["model"].get("dropout",0.0)),embd_pdrop=float(cfg["model"].get("dropout",0.0)),attn_pdrop=float(cfg["model"].get("dropout",0.0)),bos_token_id=int(meta["eos_compact_id"]),eos_token_id=int(meta["eos_compact_id"]),tie_word_embeddings=True)
    model=GPT2LMHeadModel(model_cfg); initialize_alias_rows_from_base(model,remapper); init_sha256=model_fingerprint(model)
    if cfg["train"].get("gradient_checkpointing",False): model.gradient_checkpointing_enable()
    model.to(device)
    streams={lang:np.load(data_dir/f"train_{lang}.npy",mmap_mode="r") for lang in ("en","de")}; masks={lang:np.load(data_dir/f"train_{lang}_exact_mask.npy",mmap_mode="r") for lang in ("en","de")}
    rngs={"en":np.random.default_rng(args.seed*10_000+101),"de":np.random.default_rng(args.seed*10_000+202)}
    optimizer=make_optimizer(model,cfg); scheduler=make_scheduler(optimizer,cfg,max_updates)
    reset_at_tail=bool(cfg["train"].get("reset_optimizer_at_balanced_tail",False)); phase_updates=int(cfg["train"].get("phase_updates",0))
    if reset_at_tail and schedule not in {"en_then_de","de_then_en"}: raise ValueError("optimizer-tail reset only for sequential schedules")
    if schedule in {"en_then_de","de_then_en"} and str(cfg["train"].get("lr_schedule"))!="constant": raise ValueError("path schedules require constant LR")

    run_meta={"condition":args.condition,"seed":args.seed,"schedule":schedule,"config":cfg,"data_metadata":meta,"base_vocab_size":remapper.base_vocab_size,"effective_vocab_size":remapper.vocab_size,"n_target_alias_rows":len(target_ids),"init_sha256":init_sha256,"gpu_name":torch.cuda.get_device_name(0),"cuda_visible_devices":os.environ.get("CUDA_VISIBLE_DEVICES",""),"torch_version":torch.__version__,"cuda_version":torch.version.cuda,"git_commit":git_commit(),"micro_batch_size":micro_bs,"gradient_accumulation_steps":grad_accum,"effective_batch_size":micro_bs*grad_accum,"max_updates":max_updates}
    with open(output/"run_meta.json","w",encoding="utf-8") as f: json.dump(run_meta,f,indent=2)

    mixed=str(cfg["train"].get("mixed_precision","bf16")); amp_dtype=torch.bfloat16 if mixed=="bf16" else torch.float16
    log_every=int(cfg["train"].get("log_every",50)); save_every=int(cfg["train"].get("save_every_updates",1000)); grad_clip=float(cfg["train"].get("grad_clip",1.0)); model.train(); running=0.0
    for update in range(max_updates):
        if reset_at_tail and update==2*phase_updates:
            optimizer=make_optimizer(model,cfg); scheduler=make_scheduler(optimizer,cfg,max_updates-update)
        optimizer.zero_grad(set_to_none=True); update_loss=0.0
        for micro in range(grad_accum):
            batch=sample_batch(streams,masks,remapper,micro_bs,block_size,schedule,update,micro,cfg,args.seed,rngs,device)
            with torch.autocast(device_type="cuda",dtype=amp_dtype,enabled=True):
                loss=model(input_ids=batch,labels=batch,use_cache=False).loss/grad_accum
            loss.backward(); update_loss+=float(loss.detach().float().item())
        torch.nn.utils.clip_grad_norm_(model.parameters(),grad_clip); optimizer.step(); scheduler.step(); running+=update_loss
        done=update+1
        if done%log_every==0:
            avg=running/log_every; lr=scheduler.get_last_lr()[0]; rec={"update":done,"loss":avg,"ppl":math.exp(min(avg,20)),"lr":lr}; print(json.dumps(rec),flush=True)
            with open(output/"train_log.jsonl","a",encoding="utf-8") as f: f.write(json.dumps(rec)+"\n")
            running=0.0
        if done%save_every==0 or done==max_updates: save_checkpoint(model,output,done,run_meta)


if __name__=="__main__": main()
