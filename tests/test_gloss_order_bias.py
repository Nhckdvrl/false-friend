import pytest
from scripts.analyze_gloss_order_bias import audit_scores


def trial(is_a,margin):
    return {
        "source_id":"x","host_language":"de","context_strength":"high","cue":"none",
        "correct_as_a":is_a,"correct_minus_foil_margin":margin,"form":"genial"
    }


def test_sign_change_and_order_gap():
    r=audit_scores([trial(True,-1),trial(False,3)])
    assert r["n_pairs"]==1 and r["n_sign_reversals"]==1
    assert r["n_order_gaps_above_threshold"]==1
    assert r["pair_details"][0]["mean_margin"]==1
    assert r["mean_abs_order_gap_nats"]==4


def test_incomplete_or_invalid_scores():
    with pytest.raises(ValueError,match="incomplete"):
        audit_scores([trial(True,1)])
    with pytest.raises(ValueError,match="incomplete"):
        audit_scores([trial(True,1),trial(True,2)])
    with pytest.raises(ValueError,match="nonfinite"):
        audit_scores([trial(True,float("nan"))])
    with pytest.raises(ValueError,match="threshold"):
        audit_scores([trial(True,1),trial(False,2)],threshold=0)
