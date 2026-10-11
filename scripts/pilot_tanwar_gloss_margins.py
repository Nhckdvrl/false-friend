#!/usr/bin/env python3
"""Exploratory, label-balanced lexical-sense preference under externally supplied Q1 cues.

Uses Tanwar et al. published EN-DE word definitions and Task3 sentence templates
(official code/data: EshaanT/Bilingual_processing_LLMs), NOT the authors'
original scoring protocol and NOT validated causal semantic evidence.

Every row reports model log p(A/B) with two answer-option orders. This tests
whether an externally prefixed language statement changes which gloss is
preferred; it DOES NOT show the unmodified model internally uses a language
gate. The same generated context and word is used across cue variants.
No answer-conditional softmax masking, no free-text automated gold labels.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

LANG = {"en":"English","de":"German"}
CUES = ("none", "q1_host", "q1_other")


def load_items(context_tsv: Path, lexicon_csv: Path, ids: list[str]) -> list[dict]:
    with context_tsv.open(encoding="utf-8-sig",newline="") as f:
        contexts={x["ID"]:x for x in csv.DictReader(f)}
    with lexicon_csv.open(encoding="utf-8-sig",newline="") as f:
        lex={x["ID"]:x for x in csv.DictReader(f)}
    out=[]
    for id_ in ids:
        if id_ not in contexts or id_ not in lex:
            raise ValueError(f"missing linked ID {id_}")
        x,y=contexts[id_],lex[id_]
        if x["type"] != "FALSE COGNATE" or x["en"] != x["de"]:
            raise ValueError(f"{id_}: require exact-case form and FALSE COGNATE")
        if x["lexical_category"]!="ADJ":
            raise ValueError(f"{id_}: requires adjective-only pilot, noun capitalization confounded")
        if (x["en"],x["de"]) != (y["en"],y["de"]):
            raise ValueError(f"{id_}: cross-file lexical alignment failed")
        if not y.get("en_meaning","").strip() or not y.get("de_meaning","").strip():
            raise ValueError(f"{id_}: missing published glosses")
        out.append({
            "id":id_, "form":x["en"],
            "english_meaning":y["en_meaning"].strip(),
            "german_meaning":y["de_meaning"].strip(),
            "contexts":{k:x[k] for k in ("high_en","low_en","high_de","low_de")},
            "source_pos":x["lexical_category"],
        })
    return out


def material(item: dict, host: str, strength: str, cue: str, correct_first: bool) -> dict:
    if host not in LANG or strength not in ("high","low") or cue not in CUES:
        raise ValueError("unsupported condition")
    ctx=item["contexts"][strength+"_"+host]
    if ctx.count("<MASK>")!=1:
        raise ValueError("source sentence must contain precisely one mask")
    sentence=ctx.replace("<MASK>",'"'+item["form"]+'"')
    other="de" if host=="en" else "en"
    cue_line={
        "none":"",
        "q1_host":f"Previous answer to Q1 (may be wrong): the quoted word is {LANG[host]}.\n",
        "q1_other":f"Previous answer to Q1 (may be wrong): the quoted word is {LANG[other]}.\n"
    }[cue]
    gloss1=item["english_meaning"]
    gloss2=item["german_meaning"]
    correct=gloss1 if host=="en" else gloss2
    foil=gloss2 if host=="en" else gloss1
    a,b=(correct,foil) if correct_first else (foil,correct)
    prompt=(
        "Answer one question about the word enclosed in quotation marks. "
        "Select the meaning that best fits the full sentence; choose A or B only.\n"
        +cue_line
        +f"Sentence: {sentence}\n"
        +f"A) {a}\nB) {b}\nAnswer:"
    )
    return {
        "source_id":item["id"], "form":item["form"],
        "host_language":host, "source_language_index_used":host,
        "context_strength":strength,"cue":cue,
        "correct_as_a":correct_first,
        "candidate_correct":correct,"candidate_foil":foil,
        "source_glosses_unreviewed":True,
        "source_item_naturalness_unreviewed":True,
        "original_published_task_metric":False,
        "prompt":prompt,
        "prompt_sha256":hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "status":"DRY_RUN_NO_MODEL",
    }


def manifest(items: list[dict],strengths: list[str],cues: list[str]) -> list[dict]:
    return [material(item,host,strength,cue,correct_first)
            for item in items for host in ("en","de")
            for strength in strengths for cue in cues
            for correct_first in (True,False)]


def next_label_logps(model, tokenizer, rendered_prefix: str) -> tuple[float,float]:
    import torch
    ids=tokenizer.encode(rendered_prefix,add_special_tokens=False)
    ca=tokenizer.encode(rendered_prefix+" A",add_special_tokens=False)
    cb=tokenizer.encode(rendered_prefix+" B",add_special_tokens=False)
    if not ids or ca[:len(ids)]!=ids or cb[:len(ids)]!=ids:
        raise ValueError("Answer suffix causes tokenizer prefix resegmentation")
    if len(ca)!=len(ids)+1 or len(cb)!=len(ids)+1 or ca[-1]==cb[-1]:
        raise ValueError("A/B must each add a unique single token")
    dev=next(model.parameters()).device
    inp=torch.tensor([ids],dtype=torch.long,device=dev)
    with torch.inference_mode():
        logits=model(input_ids=inp,use_cache=False).logits[0,-1].float()
        lp=torch.log_softmax(logits,dim=-1)
        return lp[ca[-1]].item(),lp[cb[-1]].item()


def score_records(records: list[dict],model_id: str,revision: str) -> list[dict]:
    import torch
    from huggingface_hub import model_info
    from transformers import AutoModelForCausalLM,AutoTokenizer
    resolved=model_info(model_id,revision=revision).sha
    torch.set_num_threads(min(4,os.cpu_count() or 1))
    tokenizer=AutoTokenizer.from_pretrained(model_id,revision=resolved,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(
        model_id,revision=resolved,trust_remote_code=False,
        torch_dtype=torch.float32,low_cpu_mem_usage=False,
    ).to("cpu").eval()
    out=[]
    for idx, r in enumerate(records,1):
        rendered=tokenizer.apply_chat_template(
            [{"role":"user","content":r["prompt"]}],
            tokenize=False, add_generation_prompt=True
        )
        a,b=next_label_logps(model,tokenizer,rendered)
        margin=(a-b) if r["correct_as_a"] else (b-a)
        rr={**r,"logp_A":a,"logp_B":b,"correct_minus_foil_margin":margin,
            "model_id":model_id,"model_sha":resolved,"tokenizer_sha":resolved,
            "status":"EXPLORATORY_LOGPROB_NOT_VALIDATED"}
        out.append(rr)
        print(f'{idx}/{len(records)} {rr["form"]} host={rr["host_language"]} '
              f'{rr["context_strength"]}/{rr["cue"]} correct_as_a={rr["correct_as_a"]} '
              f'margin={margin:+.3f}',flush=True)
    return out


def summarize(records: list[dict]) -> list[dict]:
    grouping={}
    for r in records:
        key=(r["source_id"],r["host_language"],r["context_strength"],r["cue"])
        grouping.setdefault(key,[]).append(r)
    out=[]
    for k,v in sorted(grouping.items()):
        if len(v)!=2 or {x["correct_as_a"] for x in v}!={True,False}:
            raise ValueError("missing exact A/B order pair")
        out.append({
            "item_id":k[0],"form":v[0]["form"],"host_language":k[1],
            "strength":k[2],"cue":k[3],
            "mean_correct_minus_foil_margin":sum(q.get("correct_minus_foil_margin",float("nan")) for q in v)/2,
            "source_glosses_unreviewed":True,
            "status":"EXPLORATORY_NOT_INFERENTIAL",
        })
    return out


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--context-tsv",required=True,type=Path)
    ap.add_argument("--lexicon-csv",required=True,type=Path)
    ap.add_argument("--ids",default="261,264,272",help="predeclared source IDs; 3 adjective contexts are pilot examples")
    ap.add_argument("--strengths",default="high")
    ap.add_argument("--cues",default="none,q1_host,q1_other")
    ap.add_argument("--dry-run",action="store_true")
    ap.add_argument("--model-id",default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--revision",default="main")
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    items=load_items(a.context_tsv,a.lexicon_csv,[x.strip() for x in a.ids.split(",")])
    strengths=[s.strip() for s in a.strengths.split(",")]
    cues=[s.strip() for s in a.cues.split(",")]
    records=manifest(items,strengths,cues)
    if not a.dry_run:
        records=score_records(records,a.model_id,a.revision)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")
    if not a.dry_run:
        result=summarize(records)
        path=a.output.with_suffix(".summary.json")
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(f"Saved {len(result)} paired descriptive margins to {path}")
    print(f"Saved {len(records)} scored/dry-run conditions to {a.output}")


if __name__=="__main__":
    main()
