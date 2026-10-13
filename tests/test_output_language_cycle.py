from scripts.build_output_language_cycle import build
from scripts.run_output_language_cycle import build_trials, generation_specs


def test_rule_mapping_and_position_are_independently_counterbalanced():
    items = build()
    trials = build_trials(items)
    assert len(trials) == 1728
    for item in items:
        rows = [r for r in trials if r["item_id"] == item["item_id"] and r["task"] == "rule"
                and r["representation"] == "original" and r["explanation_language"] == "English"]
        assert len(rows) == 4
        correct_display_positions = [r["content_order"].index(r["correct_index"]) for r in rows]
        assert correct_display_positions.count(0) == correct_display_positions.count(1) == 2
        for r in rows:
            assert r["correct_index"] ^ r["mapping"] == item["sense_index"]
    assert all(r["correct_index"] is None for r in trials if r["representation"] == "masked")


def test_explanation_language_contrast_changes_only_language_name():
    items = build()
    trials = build_trials(items)
    lookup = {(r["item_id"], r["representation"], r["task"], r["mapping"], r["rotation"], r["explanation_language"]): r for r in trials}
    for key, english in lookup.items():
        if key[-1] == "English":
            german = lookup[key[:-1] + ("German",)]
            assert english["prompt"].removesuffix("English.") == german["prompt"].removesuffix("German.")
            assert english["correct_index"] == german["correct_index"]
    assert len(generation_specs(items, trials)) == 96
