import json
import pytest
from false_friend_lab.schema import DataError, load_items, preflight_report, validate_item


def example(**changes):
    value = {
        "item_id": "test-1", "family_id": "family-1", "lexeme_id": "room",
        "language": "nl", "target_form": "room",
        "context": "De kok deed room in de soep.",
        "gloss_correct": "cream", "gloss_competitor": "space inside a building",
        "condition": "baseline", "phenomenon": "cross_lingual_false_friend",
        "review_status": "illustrative", "source_ref": "demo",
        "explicit_language": True, "reviewers": []
    }
    value.update(changes)
    return value


def test_demo_blocked_by_default():
    with pytest.raises(DataError, match="illustrative"):
        validate_item(example())


def test_demo_opt_in_is_not_scientific():
    rows = [validate_item(example(), allow_illustrative=True)]
    assert preflight_report(rows)["scientific_claims_permitted"] is False


def test_verified_requires_independent_review():
    with pytest.raises(DataError, match="two distinct"):
        validate_item(example(review_status="verified", source_ref="https://example.org", reviewers=["r1"]))
    item = validate_item(example(review_status="verified", source_ref="https://example.org", reviewers=["r1", "r2"]))
    assert item["review_status"] == "verified"


def test_target_exact_and_gloss_distinct():
    with pytest.raises(DataError, match="exact lexical"):
        validate_item(example(context="A bedroom is small."), allow_illustrative=True)
    with pytest.raises(DataError, match="glosses must differ"):
        validate_item(example(gloss_competitor="cream"), allow_illustrative=True)


def test_paraphrase_must_remove_surface():
    with pytest.raises(DataError, match="remove"):
        validate_item(example(condition="paraphrase"), allow_illustrative=True)
    with pytest.raises(DataError, match="focus_form"):
        validate_item(example(condition="paraphrase", context="De kok voegde zuivel toe."), allow_illustrative=True)
    validate_item(example(condition="paraphrase", context="De kok voegde zuivel toe.", focus_form="zuivel"), allow_illustrative=True)
    # A compound containing the sequence is not the exact ambiguous lexical word.
    validate_item(example(condition="paraphrase", context="De kok voegde kookroom toe.", focus_form="kookroom"), allow_illustrative=True)


def test_load_duplicate_id_and_line_diagnostics(tmp_path):
    path = tmp_path / "sample.jsonl"
    line = json.dumps(example())
    path.write_text(line + "\n" + line + "\n", encoding="utf-8")
    with pytest.raises(DataError, match="duplicate item_id"):
        load_items(path, allow_illustrative=True)
    path.write_text("not json\n", encoding="utf-8")
    with pytest.raises(DataError, match=":1:"):
        load_items(path, allow_illustrative=True)
