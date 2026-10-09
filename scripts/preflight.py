#!/usr/bin/env python3
"""Validate dataset provenance and contrast coverage before allocating GPUs."""
import argparse
import json
from false_friend_lab.schema import load_items, preflight_report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--allow-illustrative", action="store_true", help="dry-run only")
    a = ap.parse_args()
    rows = load_items(a.data, allow_illustrative=a.allow_illustrative)
    print(json.dumps(preflight_report(rows), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
