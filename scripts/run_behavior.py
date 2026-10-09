#!/usr/bin/env python3
"""Pilot behavior runner for local/open-weight HF causal language models."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from false_friend_lab.behavior import assess_item, make_prompt
from false_friend_lab.schema import load_items
from false_friend_lab.scoring import ensure_label_tokens, hf_score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--model", required=True, help="HF model ID or local checkpoint")
    ap.add_argument("--revision", default="main", help="pin commit SHA for reproducibility")
    ap.add_argument("--device", default="cpu", help="cpu or cuda:0, etc.")
    ap.add_argument("--output", required=True)
    ap.add_argument("--allow-illustrative", action="store_true", help="dry-run only")
    a = ap.parse_args()

    rows = load_items(a.data, allow_illustrative=a.allow_illustrative)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(a.model, revision=a.revision, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        a.model, revision=a.revision, trust_remote_code=False
    ).to(a.device).eval()
    records = []
    for item in rows:
        for is_a in (True, False):
            ensure_label_tokens(tokenizer, make_prompt(item, correct_is_a=is_a))
        result = assess_item(item, lambda p, c: hf_score(model, tokenizer, p, c))
        result["model"] = a.model
        result["revision"] = a.revision
        records.append(result)

    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Write only after full successful validation and inference (no partial pseudodata).
    with out.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = {
        "data": str(a.data), "model": a.model, "revision": a.revision,
        "device": a.device, "rows": len(records),
        "scientific_claims_permitted": all(x["review_status"] == "verified" for x in records),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "note": "These are behavior-pilot outputs, not mechanism or causal results.",
    }
    out.with_suffix(out.suffix + ".meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(records)} pilot results: {out}")


if __name__ == "__main__":
    main()
