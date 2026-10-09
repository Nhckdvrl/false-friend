#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from false_friend_lab.summary import summarize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--bootstrap", type=int, default=2000)
    a = ap.parse_args()
    if a.bootstrap < 0:
        ap.error("--bootstrap must be nonnegative")
    rows = [json.loads(line) for line in Path(a.input).read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        ap.error("empty result file")
    if any(r.get("review_status") != "verified" for r in rows):
        print("WARNING: illustrative/unverified rows: any numbers are workflow demonstrations only")
    result = summarize(rows, bootstrap=a.bootstrap)
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote descriptive summary: {out}")


if __name__ == "__main__":
    main()
