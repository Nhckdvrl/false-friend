#!/usr/bin/env python3
from __future__ import annotations

import argparse, json
from pathlib import Path
from typing import List
import pandas as pd
import torch
import torch.nn.functional as F
from transformers import GPT2LMHeadModel
from false_friend_lab.io import read_jsonl
from false_friend_lab.remap import TargetLexicalRemapper


def token_nlls(model, ids: torch.Tensor) -> torch.Tensor:
    with torch.no_grad(): logits=model(input_ids=ids.unsqueeze(0),use_cache=False).logits[0]
    lprobs=F.log_softmax(logits[:-1].float(),dim=-1); labels=ids[1:]; nll=-lprobs.gather(1,labels.unsqueeze(1)).squeeze(1)
    out=torch.full((ids.numel(),),float("nan"),device=ids.device); out[1:]=nll; return out


def window_for_position(ids: List[int], pos: int, max_len: int, post_k: int):
    if len(ids)<=max_len: return ids,pos,0
    suffix_budget=min(post_k+8,max_len//3); start=max(0,pos-(max_len-suffix_budget-1)); end=min(len(ids),start+max_len)
    if end-start<max_len: start=max(0,end-max_len)
    return ids[start:end],pos-start,start


def safe_mean(x:torch.Tensor)->float:
    x=x[~torch.isnan(x)]; return float(x.mean().item()) if x.numel() else float("nan")


def main():
    p=argparse.ArgumentParser(); p.add_argument("--checkpoint",required=True); p.add_argument("--data",default="data/processed/en_de"); p.add_argument("--post-k",type=int,default=8); p.add_argument("--pre-k",type=int,default=8); p.add_argument("--output",default=None); args=p.parse_args()
    ckpt,data_dir=Path(args.checkpoint),Path(args.data); run_meta=json.load(open(ckpt/"run_meta.json",encoding="utf-8")); data_meta=json.load(open(data_dir/"metadata.json",encoding="utf-8")); targets=pd.read_csv(data_dir/"targets.csv")
    target_ids=sorted(set(map(int,targets.compact_token_id.tolist()))); target_meta=targets.set_index("word").to_dict(orient="index"); remapper=TargetLexicalRemapper(int(data_meta["compact_vocab_size"]),target_ids,run_meta["condition"],split_lang="de")
    if not torch.cuda.is_available(): raise RuntimeError("evaluation expects CUDA for fast checkpoint sweeps")
    device=torch.device("cuda:0"); model=GPT2LMHeadModel.from_pretrained(ckpt).to(device).eval(); max_len=int(model.config.n_positions); rows=[]
    for row in read_jsonl(data_dir/"contexts.jsonl"):
        ids_base=list(map(int,row["compact_ids"])); exact=list(map(bool,row["exact_mask"])); pos=int(row["target_position"]); target_base=int(row["compact_target_id"])
        if len(ids_base)!=len(exact) or sum(exact)!=1 or not exact[pos] or ids_base[pos]!=target_base: raise AssertionError("invalid strict evaluation context")
        ids_mapped=remapper.map_ids(ids_base,row["lang"],exact); target_mapped=ids_mapped[pos]; win,win_pos,_=window_for_position(ids_mapped,pos,max_len,args.post_k)
        if win_pos==0 or win_pos>=len(win)-1: continue
        ids=torch.tensor(win,dtype=torch.long,device=device); nlls=token_nlls(model,ids)
        with torch.no_grad(): logits=model(input_ids=ids.unsqueeze(0),use_cache=False).logits[0,win_pos-1].float(); lp=F.log_softmax(logits,dim=-1)
        alias=remapper.alias_id(target_base); surface_nll=float((-torch.logsumexp(torch.stack([lp[target_base],lp[alias]]),dim=0)).item()); lexical_nll=float((-lp[target_mapped]).item())
        post_nll=safe_mean(nlls[win_pos+1:min(len(win),win_pos+1+args.post_k)]); pre_nll=safe_mean(nlls[max(1,win_pos-args.pre_k):win_pos]); tm=target_meta[row["word"]]
        rows.append({"context_id":row["context_id"],"pair_id":row["pair_id"],"word":row["word"],"relation":row["relation"],"lang":row["lang"],"condition":run_meta["condition"],"seed":int(run_meta["seed"]),"schedule":run_meta["schedule"],"update":int(run_meta.get("update",run_meta.get("step",-1))),"surface_nll":surface_nll,"lexical_nll":lexical_nll,"post_nll":post_nll,"pre_nll":pre_nll,"local_post":post_nll-pre_nll,"local_surface":surface_nll-pre_nll,"train_count_en":int(tm["train_count_en"]),"train_count_de":int(tm["train_count_de"]),"gpu_name":run_meta.get("gpu_name","unknown"),"init_sha256":run_meta.get("init_sha256","unknown"),"effective_batch_size":int(run_meta.get("effective_batch_size",-1)),"git_commit":run_meta.get("git_commit","unknown"),"data_schema_version":int(data_meta.get("schema_version",-1)),"text":row["text"]})
    df=pd.DataFrame(rows); output=Path(args.output or (ckpt/"eval_contexts.csv")); output.parent.mkdir(parents=True,exist_ok=True); df.to_csv(output,index=False); print(f"wrote {len(df)} strict context rows to {output}")
    if len(df): print(df.groupby(["relation","lang"])[["surface_nll","lexical_nll","post_nll","pre_nll","local_post"]].mean())


if __name__=="__main__": main()
