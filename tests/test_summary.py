import pytest
from false_friend_lab.summary import summarize


def row(item, family, lexeme, condition, margin):
    return {"item_id": item, "family_id": family, "lexeme_id": lexeme, "condition": condition,
            "mean_correct_minus_foil_logp": margin}


def test_lexeme_not_context_as_independent_unit():
    rows = [
        row("a1", "f1", "x", "baseline", -3),
        row("a2", "f2", "x", "baseline", -3),
        row("b1", "f3", "y", "baseline", 3),
        row("a3", "f1", "x", "early_evidence", 2),
    ]
    out = summarize(rows, bootstrap=10, seed=7)
    assert out["conditions"]["baseline"]["n_lexemes"] == 2
    assert out["conditions"]["baseline"]["mean_logp_margin"] == 0
    assert out["paired_vs_baseline_by_family"]["early_evidence"]["mean_delta_logp_margin"] == 5
    assert out["status"].startswith("DESCRIPTIVE_ONLY")


def test_nonfinite_and_duplicate_rejected():
    with pytest.raises(ValueError, match="non-finite"):
        summarize([row("a", "f", "x", "baseline", float("nan"))])
    duplicate = row("a", "f", "x", "baseline", 1)
    with pytest.raises(ValueError, match="duplicate"):
        summarize([duplicate, duplicate])
