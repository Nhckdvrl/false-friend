#!/usr/bin/env python3
"""Research-KB structural integrity, not scientific truth or full-paper verification."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LOCAL_MD_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
PAPER_STATUS = re.compile(r"\bS[123]\b")


def audit(root: Path = ROOT) -> list[str]:
    kb = root / "knowledge"
    problems: list[str] = []
    if not kb.exists():
        return ["missing knowledge directory"]
    index = kb / "PAPERS_INDEX.md"
    if not index.exists():
        return ["missing knowledge/PAPERS_INDEX.md"]
    notes = sorted((kb / "papers").glob("*.md"))
    if len(notes) < 12:
        problems.append(f"only {len(notes)} individual/pair paper notes; expected at least 12")

    index_text = index.read_text(encoding="utf-8")
    for paper in notes:
        body = paper.read_text(encoding="utf-8")
        rel = paper.relative_to(kb).as_posix()
        if f"({rel})" not in index_text:
            problems.append(f"unregistered paper note: {rel}")
        if len(body) < 900:
            problems.append(f"paper note too short for a structured research asset: {rel}")
        if not PAPER_STATUS.search(body):
            problems.append(f"no verified reading-depth marker: {rel}")
        if "INFERENCE" not in body:
            problems.append(f"paper lacks separate reconstructed idea-origin inference: {rel}")
        if "https://" not in body:
            problems.append(f"paper lacks a verifiable primary source link: {rel}")

    # Check all local Markdown references, including future note crosslinks.
    candidates = [root / "README.md", root / "RESEARCH_MAINLINE.md", root / "AGENTS.md"]
    candidates += sorted((root / "docs").glob("*.md"))
    candidates += sorted(kb.rglob("*.md"))
    checked = 0
    for doc in candidates:
        if not doc.exists():
            continue
        for raw in LOCAL_MD_LINK.findall(doc.read_text(encoding="utf-8")):
            dest = raw.strip().split("#", 1)[0]
            if not dest or dest.startswith(("http:", "https:", "mailto:", "data:")):
                continue
            # Plain relative paths are used in this repo; no markdown link titles.
            target = (doc.parent / unquote(dest)).resolve()
            checked += 1
            if not target.is_relative_to(root.resolve()):
                problems.append(f"link escapes repo root: {doc.relative_to(root)} -> {raw}")
            elif not target.exists():
                problems.append(f"broken local link: {doc.relative_to(root)} -> {raw}")

    summary = f"knowledge audit: {len(notes)} paper notes, {checked} local crosslinks, {len(problems)} problems"
    print(summary)
    return problems


def main() -> int:
    problems = audit()
    for problem in problems:
        print(f"ERROR: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
