#!/usr/bin/env python3
"""Build a browseable index and bounded source cards from the local source registry.

This validates bookkeeping, not paper correctness, research merit, or reading quality.
No downloads, model calls, or mutations outside this repository.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('id', 'title', 'url', 'stage', 'domain', 'asset', 'scope', 'origin')
STAGES = {'S0', 'S1', 'S2', 'S3'}
ORIGINS = {'current', 'inherited', 'catalogue'}


def load_registry(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError(f'{path}: expected TSV columns {FIELDS}')
        rows = list(reader)
    if not rows:
        raise ValueError('empty source registry')
    seen = set()
    for row_number, row in enumerate(rows, 2):
        if None in row or any(not isinstance(row.get(k), str) or not row[k].strip() for k in FIELDS):
            raise ValueError(f'row {row_number}: blank or malformed registry field')
        if not re.fullmatch(r'P\d{3}', row['id']) or row['id'] in seen:
            raise ValueError(f'row {row_number}: invalid or duplicate source ID {row["id"]}')
        seen.add(row['id'])
        if row['stage'] not in STAGES or row['origin'] not in ORIGINS:
            raise ValueError(f'{row["id"]}: invalid reading stage or provenance origin')
        parsed = urlparse(row['url'])
        if parsed.scheme != 'https' or not parsed.netloc:
            raise ValueError(f'{row["id"]}: source must have a verifiable HTTPS address')
        if Path(row['asset'].split('#', 1)[0]).is_absolute() or '..' in Path(row['asset'].split('#', 1)[0]).parts:
            raise ValueError(f'{row["id"]}: asset must remain inside knowledge/')
        if row['origin'] == 'catalogue' and row['stage'] not in {'S0', 'S3'}:
            raise ValueError(f'{row["id"]}: catalogue-only is not a detailed reading')
    return rows


def _text(value: str) -> str:
    return value.replace('|', '\\|').replace('\n', ' ')


def render_index(rows: list[dict[str, str]]) -> str:
    counts = Counter(r['stage'] for r in rows)
    domains = defaultdict(list)
    for row in rows:
        domains[row['domain']].append(row)
    lines = [
        '# 文献与研究资产总索引', '',
        '<!-- GENERATED: edit knowledge/sources.tsv then run scripts/build_knowledge_index.py -->', '',
        f'共 **{len(rows)}** 个来源条目。' + ' / '.join(f'{s}: {counts[s]}' for s in sorted(STAGES)) + '。', '',
        '**登记齐全不等于全部精读。** S1为有主方法/结果阅读记录，S2为定向正文，S3仅摘要/元数据，S0仅题名。',
        '`current` 是本轮补读或新读；`inherited` 保留前轮已有笔记，不假称本轮全部重读；`catalogue` 是有边界的导航。', '',
        '从 [领域画像](FIELD_GUIDE.md) → [实验设计来源](EXPERIMENT_DESIGN_LESSONS.md) → [本地交接](../HANDOFF.md) 进入当前工作。',
        '机器可检索 [sources.tsv](sources.tsv)；未精读资料的已知范围与禁用推断在 [来源卡](catalogue/SOURCE_CARDS.md)。', '',
    ]
    for domain, items in domains.items():
        lines += [f'## {domain}', '', '| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |', '|---|---|---|---|']
        for row in items:
            lines.append(f'| {row["id"]} · [{_text(row["title"])}]({row["url"]}) | {row["stage"]} / {row["origin"]} | [记录]({row["asset"]}) | {_text(row["scope"])} |')
        lines.append('')
    lines += [
        '## 历史与范围', '',
        '原先40条索引的完整快照保留在 `history/INDEX_BASELINE_2026-10-12.txt`，检查脚本防止静默漏收原来源。',
        '表内网址重复可以是不同目录题名（例如官方会议总目录）；ID才是唯一主键。',
        'S3/S0不支持细致机制或实验结论；后续真正读到原文时更新记录，而不是把空白写成已知。',
        '目前没有声称已完成整个领域或所有最新会议论文的阅读。正式主张依已核实的原文与独立实验。', '',
    ]
    return '\n'.join(lines)


def render_cards(rows: list[dict[str, str]]) -> str:
    lines = [
        '# 受限阅读来源卡：保留全部输入，不伪造精读', '',
        '<!-- GENERATED from knowledge/sources.tsv -->', '',
        '这些记录保存已检索来源及其在领域地图中的作用。没有可靠全文阅读时，不补写作者方法、数据量、结果或创新声明。',
        '当前主线见 [研究主线](../../RESEARCH_MAINLINE.md)；所有条目见 [总索引](../PAPERS_INDEX.md)。', '',
    ]
    for row in rows:
        if not row['asset'].startswith('catalogue/SOURCE_CARDS.md#'):
            continue
        lines += [
            f'<a id="{row["id"].lower()}"></a>', '',
            f'## {row["id"]} · {row["title"]}', '',
            f'**原始入口**：[来源]({row["url"]})。**范围**：{row["stage"]}，{row["domain"]}。', '',
            row['scope'] + '。', '',
            '**如何使用**：它是进一步检索的有界入口，不是本文机制结论的证据。若下一实验直接依赖该工作的具体方法或对照，先读对应原文，再升级并写结构化笔记。',
            '**不能使用**：不把题名或摘要补成实验链，不以它证明独创性或判死一个领域；不把已有论文的存在误解为问题已充分解释。', '',
        ]
    return '\n'.join(lines)


def expected_outputs(root: Path) -> dict[Path, str]:
    rows = load_registry(root / 'knowledge/sources.tsv')
    return {
        root / 'knowledge/PAPERS_INDEX.md': render_index(rows),
        root / 'knowledge/catalogue/SOURCE_CARDS.md': render_cards(rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for path, content in expected_outputs(args.root).items():
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                stale.append(str(path.relative_to(args.root)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
    if stale:
        print('Stale or missing generated knowledge assets:', ', '.join(stale))
        return 1
    print('Knowledge index/cards checked' if args.check else 'Knowledge index/cards generated')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
