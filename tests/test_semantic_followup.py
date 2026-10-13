from scripts.run_semantic_followup import build_trials, summarize


def test_binary_rotations_and_ambiguous_variants_do_not_invent_gold():
    item = {
        "item_id": "x", "lexeme_family_id": "family", "source_language": "zh",
        "context_revision": "low", "options": ["repair", "course"], "correct_index": None,
        "variants": ["original", "paraphrase", "foil_paraphrase"],
        "variant_prompts": {"original": "ambiguous", "paraphrase": "repair", "foil_paraphrase": "course"},
        "variant_correct_indices": {"original": None, "paraphrase": 0, "foil_paraphrase": 1},
    }
    trials = build_trials([item])
    assert len(trials) == 6
    for row in trials:
        preferred = 1 if row["variant"] == "foil_paraphrase" else 0
        row["label_logps"] = [-0.1 if content == preferred else -3.0 for content in row["content_order"]]
    result = summarize(trials)
    decisions = {r["variant"]: r for r in result["decisions"]}
    assert decisions["original"]["correct"] is None
    assert decisions["original"]["correct_minus_foil_logp"] is None
    assert decisions["paraphrase"]["prediction"] == 0
    assert decisions["foil_paraphrase"]["prediction"] == 1
    assert all(r["rotation_stable"] for r in decisions.values())
    ambiguous = next(r for r in result["groups"] if r["variant"] == "original")
    assert ambiguous["n_labeled"] == 0
    assert ambiguous["family_agreement"]["mean"] is None
