"""Audited item contract. Illustrations are never scientific observations."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REQUIRED = (
    "item_id", "family_id", "lexeme_id", "language", "target_form",
    "context", "gloss_correct", "gloss_competitor", "condition",
    "phenomenon", "review_status", "source_ref", "explicit_language",
)
PHENOMENA = {"cross_lingual_false_friend", "within_language_polysemy", "unambiguous"}
REVIEW_STATUSES = {"illustrative", "verified"}
LANGUAGES = {"en": "English", "de": "German", "nl": "Dutch", "fr": "French",
             "es": "Spanish", "zh": "Chinese", "ja": "Japanese",
             "id": "Indonesian", "ms": "Malay"}
SLUG = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$")


class DataError(ValueError):
    """Invalid science-facing dataset rather than a recoverable formatting warning."""


def validate_item(row: dict, *, allow_illustrative: bool = False) -> dict:
    if not isinstance(row, dict):
        raise DataError("each item must be a JSON object")
    missing = [k for k in REQUIRED if k not in row]
    if missing:
        raise DataError("missing required fields: " + ", ".join(missing))
    for key in REQUIRED:
        if key == "explicit_language":
            if not isinstance(row[key], bool):
                raise DataError("explicit_language must be a JSON boolean")
            continue
        if not isinstance(row[key], str) or not row[key].strip():
            raise DataError(f"{key} must be a nonempty string")
    for key in ("item_id", "family_id", "lexeme_id", "condition"):
        if not SLUG.fullmatch(row[key]):
            raise DataError(f"{key} must be a simple identifier")
    if row["phenomenon"] not in PHENOMENA:
        raise DataError(f"invalid phenomenon: {row['phenomenon']}")
    if row["language"] not in LANGUAGES:
        raise DataError(f"unknown language: {row['language']}")
    if row["review_status"] not in REVIEW_STATUSES:
        raise DataError("invalid review_status")
    if row["gloss_correct"].casefold().strip() == row["gloss_competitor"].casefold().strip():
        raise DataError("the two competing glosses must differ")
    reviewers = row.get("reviewers", [])
    if not isinstance(reviewers, list) or not all(isinstance(r, str) and r.strip() for r in reviewers):
        raise DataError("reviewers must be a list of nonempty strings")
    if row["review_status"] == "verified":
        if len(set(reviewers)) < 2:
            raise DataError("verified observations require two distinct independent reviewers")
        if row["source_ref"] in {"demo", "illustration", "synthetic", "unknown"}:
            raise DataError("verified observations require traceable real provenance")
    elif not allow_illustrative:
        raise DataError("illustrative rows are blocked; use --allow-illustrative ONLY for dry runs")
    context = row["context"]
    exact_occurrence = re.search(r"(?<!\w)" + re.escape(row["target_form"]) + r"(?!\w)", context)
    if row["condition"] != "paraphrase":
        if exact_occurrence is None:
            raise DataError("target_form must occur as an exact lexical form in context")
    else:
        if exact_occurrence is not None:
            raise DataError("paraphrase control must remove the ambiguous target_form")
        focus = row.get("focus_form")
        if not isinstance(focus, str) or not focus.strip() or focus == row["target_form"]:
            raise DataError("paraphrase requires a distinct nonambiguous focus_form")
        if not re.search(r"(?<!\w)" + re.escape(focus) + r"(?!\w)", context):
            raise DataError("focus_form must occur as an exact lexical word in paraphrase context")
    return dict(row)


def load_items(path: str | Path, *, allow_illustrative: bool = False) -> list[dict]:
    result = []
    seen = set()
    with Path(path).open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                item = validate_item(json.loads(line), allow_illustrative=allow_illustrative)
            except (json.JSONDecodeError, DataError) as e:
                raise DataError(f"{path}:{line_no}: {e}") from e
            if item["item_id"] in seen:
                raise DataError(f"duplicate item_id: {item['item_id']}")
            seen.add(item["item_id"])
            result.append(item)
    if not result:
        raise DataError("empty dataset")
    return result


def preflight_report(rows: list[dict]) -> dict:
    if not rows:
        raise DataError("empty dataset")
    by_group = defaultdict(set)
    for r in rows:
        by_group[r["family_id"]].add(r["condition"])
    return {
        "rows": len(rows),
        "lexical_types": len({r["lexeme_id"] for r in rows}),
        "families": len(by_group),
        "phenomena": dict(sorted(Counter(r["phenomenon"] for r in rows).items())),
        "conditions": dict(sorted(Counter(r["condition"] for r in rows).items())),
        "languages": dict(sorted(Counter(r["language"] for r in rows).items())),
        "review_statuses": dict(sorted(Counter(r["review_status"] for r in rows).items())),
        "matched_families_two_or_more_conditions": sum(len(v) >= 2 for v in by_group.values()),
        "scientific_claims_permitted": all(r["review_status"] == "verified" for r in rows),
    }
