#!/usr/bin/env python3
"""Local, transparent keyword lookup for the workbench research source registry.

This is a navigation aid, not semantic search or an answer-producing literature review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

try:
    from .build_knowledge_index import load_registry
except ImportError:
    from build_knowledge_index import load_registry

ROOT = Path(__file__).resolve().parent.parent


def query_sources(root: Path, query: str, limit: int = 8) -> list[dict]:
    terms = [t.casefold() for t in re.split(r'\s+', query.strip()) if t]
    if not terms or limit < 1:
        raise ValueError('query must be nonblank and limit positive')
    matches = []
    for row in load_registry(root / 'knowledge/sources.tsv'):
        heading = ' '.join(row[k] for k in ('id', 'title', 'domain', 'scope')).casefold()
        asset = root / 'knowledge' / row['asset'].split('#', 1)[0]
        body = asset.read_text(encoding='utf-8') if asset.is_file() else ''
        # Catalogue cards share a file: do not match the content of unrelated cards.
        if row['asset'].startswith('catalogue/'):
            body = row['scope']
        score = sum(4 * heading.count(t) + min(body.casefold().count(t), 8) for t in terms)
        if score:
            matching = next((line.strip() for line in body.splitlines()
                             if any(t in line.casefold() for t in terms)), row['scope'])
            matches.append({**row, 'navigation_score': score, 'snippet': matching[:320]})
    return sorted(matches, key=lambda x: (-x['navigation_score'], x['id']))[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--query', required=True)
    parser.add_argument('--limit', type=int, default=8)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(query_sources(args.root, args.query, args.limit), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
