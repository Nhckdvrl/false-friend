#!/usr/bin/env python3
"""Check source coverage, registry provenance, generated indexes and local links.

No arbitrary paper-count or note-length quality threshold. Software cannot certify
that a paper was deeply read, that its claims are true, or that an idea is worthwhile.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import unquote

try:
    from .build_knowledge_index import load_registry, expected_outputs
except ImportError:
    from build_knowledge_index import load_registry, expected_outputs

ROOT = Path(__file__).resolve().parent.parent
LOCAL_LINK = re.compile(r'(?<!!)\[[^\]]+\]\(([^)]+)\)')
OLD_FIRST_SOURCE = re.compile(r'^\|\s*\[[^\]]+\]\((https://[^)]+)\)', re.MULTILINE)


def _without_fences(text: str) -> str:
    return re.sub(r'(?ms)^(```|~~~).*?^\1[^\n]*$', '', text)


def coverage_missing(old_index: str, rows: list[dict[str, str]]) -> list[str]:
    present = {r['url'].rstrip('/') for r in rows}
    return sorted({u.rstrip('/') for u in OLD_FIRST_SOURCE.findall(old_index)} - present)


def audit(root: Path = ROOT) -> list[str]:
    root = root.resolve()
    problems: list[str] = []
    try:
        rows = load_registry(root / 'knowledge/sources.tsv')
    except (ValueError, OSError) as error:
        return [str(error)]
    kb = root / 'knowledge'
    registered = set()
    for row in rows:
        name, _, anchor = row['asset'].partition('#')
        path = (kb / name).resolve()
        registered.add(path)
        if not path.is_relative_to(kb.resolve()) or not path.is_file():
            problems.append(f'{row["id"]}: missing or out-of-scope asset {row["asset"]}')
            continue
        body = path.read_text(encoding='utf-8')
        if anchor and f'id="{anchor}"' not in body:
            problems.append(f'{row["id"]}: missing explicit catalogue anchor {anchor}')
        if row['stage'] in {'S1', 'S2'} and not any(word in body for word in ('INFERENCE', '推测', '推演')):
            problems.append(f'{row["id"]}: structured reading asset lacks separated idea-origin inference')
    notes = sorted((kb / 'papers').glob('*.md'))
    for note in notes:
        if note.resolve() not in registered:
            problems.append(f'unregistered paper note: {note.relative_to(kb)}')
    baseline = kb / 'history/INDEX_BASELINE_2026-10-12.txt'
    if not baseline.is_file():
        problems.append('missing immutable pre-integration index coverage record')
    else:
        for url in coverage_missing(baseline.read_text(encoding='utf-8'), rows):
            problems.append(f'previously indexed source silently omitted: {url}')
    for path, expected in expected_outputs(root).items():
        if not path.is_file() or path.read_text(encoding='utf-8') != expected:
            problems.append(f'stale generated asset: {path.relative_to(root)}')
    links = 0
    documents = [root / n for n in ('README.md', 'RESEARCH_MAINLINE.md', 'AGENTS.md', 'HANDOFF.md')]
    for folder in ('knowledge', 'docs', 'experiments', 'evidence'):
        documents.extend((root / folder).rglob('*.md'))
    for document in documents:
        if not document.is_file():
            continue
        for raw in LOCAL_LINK.findall(_without_fences(document.read_text(encoding='utf-8'))):
            dest = raw.split('#', 1)[0].strip()
            if not dest or dest.startswith(('https:', 'http:', 'mailto:', 'data:')):
                continue
            path = (document.parent / unquote(dest)).resolve()
            links += 1
            if not path.is_relative_to(root) or not path.exists():
                problems.append(f'broken/outside local link: {document.relative_to(root)} -> {raw}')
    print(f'knowledge audit: {len(rows)} source entries, {len(notes)} paper notes, {links} local links, {len(problems)} problems')
    return problems


def main() -> int:
    problems = audit()
    for problem in problems:
        print(f'ERROR: {problem}', file=sys.stderr)
    return int(bool(problems))


if __name__ == '__main__':
    raise SystemExit(main())
