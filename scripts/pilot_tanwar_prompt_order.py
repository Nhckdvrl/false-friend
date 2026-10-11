#!/usr/bin/env python3
"""Reproducible Tanwar Task3 same-item prompt-order pilot.

The original three-question user message is reproduced VERBATIM from
EshaanT/Bilingual_processing_LLMs/src/data.py Task3.instruction, pinned at
281a67eac6ddbe5445e1c10277e5833d40d72125.

Original authors use LLaMA3.1 generation and human annotations. Alternative
questions and the optional Qwen CPU runner are NEW exploratory tests, NOT
an exact baseline reproduction or calibrated semantic accuracy.

--dry-run never downloads model weights; all output records clearly say so.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

NAMES = {"en":"English", "de":"German", "fr":"French", "es":"Spanish"}
ORIGINAL_INSTRUCTION = (
    "Given the following code-mix sentence in {l1}-{l2}. "
    "Answer the following questions about the word enclosed in double quotes\n"
    "Q1. What is the language of the enclosed word?\n"
    "Q2. What is the meaning of the enclosed word?\n"
    "Q3. Does the given sentence make sense in context with the meaning of the enclosed word?"
)
ALTERED = {
    "original": ORIGINAL_INSTRUCTION,
    "meaning_first": (
        "Given the following code-mix sentence in {l1}-{l2}. "
        "Answer the following questions about the word enclosed in double quotes\n"
        "Q1. What is the meaning of the enclosed word?\n"
        "Q2. What is the language of the enclosed word?\n"
        "Q3. Does the given sentence make sense in context with the meaning of the enclosed word?"
    ),
    "meaning_only": (
        "Given the following code-mix sentence in {l1}-{l2}. "
        "Answer the following question about the word enclosed in double quotes\n"
        "What is the meaning of the enclosed word?"
    ),
    "language_only": (
        "Given the following code-mix sentence in {l1}-{l2}. "
        "Answer the following question about the word enclosed in double quotes\n"
        "What is the language of the enclosed word?"
    )
}


def make_stimulus(row: dict, *, l2: str, word_language: str, strength: str) -> tuple[str,str]:
    """Cross setup: word from 'word_language', host sentence in OTHER language."""
    if word_language not in ("en", l2):
        raise ValueError("word_language must be en or l2")
    if strength not in ("high","low"):
        raise ValueError("strength must be high/low")
    host = l2 if word_language == "en" else "en"
    word = row[word_language].strip()
    original = row[f"{strength}_{host}"]
    if original.count("<MASK>") != 1:
        raise ValueError("expected exactly one target slot")
    return original.replace("<MASK>", '"' + word + '"'), host


def prompt_text(row: dict, *, l2: str, word_language: str, strength: str, variant: str) -> dict:
    if variant not in ALTERED:
        raise ValueError(f"unknown question-order variant {variant}")
    sentence, host = make_stimulus(row,l2=l2,word_language=word_language,strength=strength)
    return {
        "item_id":row["ID"], "word_language_index":word_language,
        "host_sentence_language":host, "word":row[word_language],
        "other_language_word":row[host], "surface_identity":row["en"]==row[l2],
        "source_type":row["type"],"lexical_category":row.get("lexical_category",""),
        "semantic_constraint":strength, "prompt_variant":variant,
        "context":sentence,
        "prompt":ALTERED[variant].format(l1=NAMES["en"],l2=NAMES[l2])+"\n"+sentence,
        "status":"UNVALIDATED_SOURCE_STIMULUS",
    }


def build_manifest(source: Path, l2: str, *, limit: int, strength: str, variants: list[str]) -> list[dict]:
    if l2 not in ("de","fr","es"):
        raise ValueError("supported L2: de/fr/es")
    with source.open(encoding="utf-8-sig", newline="") as f:
        data = list(csv.DictReader(f))
    exact_ff = [r for r in data if r["type"]=="FALSE COGNATE"
                and r["en"].strip()==r[l2].strip()]
    if not exact_ff:
        raise ValueError("no strictly identical false cognates in source")
    if limit < 1:
        raise ValueError("limit must be >=1")
    manifest=[]
    for row in exact_ff[:limit]:
        for word_language in ("en",l2):
            for v in variants:
                manifest.append(prompt_text(row,l2=l2,word_language=word_language,
                                            strength=strength,variant=v))
    return manifest


def run_model(records: list[dict], *, model_id: str, revision: str, max_new_tokens: int) -> list[dict]:
    """Small exploratory generative smoke; no automatic gold semantic labels."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from huggingface_hub import model_info
    commit = model_info(model_id, revision=revision).sha
    tokenizer = AutoTokenizer.from_pretrained(model_id, revision=commit, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, revision=commit, trust_remote_code=False,
        torch_dtype=torch.float32, low_cpu_mem_usage=False,
    ).to("cpu").eval()
    torch.set_num_threads(min(4, os.cpu_count() or 1))
    out=[]
    for i, rec in enumerate(records,1):
        rendered = tokenizer.apply_chat_template(
            [{"role":"user","content":rec["prompt"]}],
            add_generation_prompt=True, tokenize=False,
        )
        inputs=tokenizer(rendered,return_tensors="pt")
        with torch.inference_mode():
            ids=model.generate(**inputs, do_sample=False, max_new_tokens=max_new_tokens,
                               pad_token_id=tokenizer.eos_token_id)
        generated=tokenizer.decode(ids[0][inputs.input_ids.shape[-1]:],
                                   skip_special_tokens=True)
        out.append({
            **rec, "status":"EXPLORATORY_GENERATION_NOT_VALIDATED",
            "generated":generated,
            "model_id":model_id,
            "model_sha":commit,
            "tokenizer_sha":commit,
            "chat_template_deviation":(
                "Hugging Face add_generation_prompt=True; original code used "
                "apply_chat_template(tokenize=False) with library default"
            )
        })
        print(f"{i}/{len(records)} {rec['item_id']} {rec['word_language_index']} "
              f"{rec['prompt_variant']}: {generated[:90]!r}", flush=True)
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-tsv",required=True,type=Path)
    ap.add_argument("--l2",required=True,choices=("de","fr","es"))
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--limit",type=int,default=2)
    ap.add_argument("--strength",choices=("high","low"),default="high")
    ap.add_argument("--variants",default="original,meaning_first,meaning_only")
    ap.add_argument("--dry-run",action="store_true")
    ap.add_argument("--model-id",default="Qwen/Qwen2.5-0.5B-Instruct")
    ap.add_argument("--model-revision",default="main")
    ap.add_argument("--max-new-tokens",type=int,default=64)
    a=ap.parse_args()
    variants=[x.strip() for x in a.variants.split(",") if x.strip()]
    manifest=build_manifest(a.source_tsv,a.l2,limit=a.limit,strength=a.strength,
                            variants=variants)
    if a.dry_run:
        for r in manifest:
            r["status"]="DRY_RUN_NO_MODEL"
    else:
        manifest=run_model(manifest,model_id=a.model_id,
                           revision=a.model_revision,max_new_tokens=a.max_new_tokens)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",encoding="utf-8") as f:
        for r in manifest:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")
    print(f"Wrote {len(manifest)} records to {a.output}")


if __name__=="__main__":
    main()
