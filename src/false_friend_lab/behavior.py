"""Paired, label-swapped meaning selection. Not a direct measurement of hidden senses."""
from __future__ import annotations

from .schema import LANGUAGES


def make_prompt(item: dict, *, correct_is_a: bool) -> str:
    correct, foil = item["gloss_correct"], item["gloss_competitor"]
    # Never reintroduce the ambiguous original into a paraphrase control prompt.
    focus = item.get("focus_form", item["target_form"])
    a, b = (correct, foil) if correct_is_a else (foil, correct)
    language = LANGUAGES[item["language"]]
    hint = f"The sentence is written in {language}.\n" if item["explicit_language"] else ""
    return (
        "Identify the intended meaning of the highlighted word in this sentence.\n"
        + hint
        + "Choose between the two meanings. Reply with A or B only.\n"
        + f"Sentence: {item['context']}\n"
        + f"Highlighted word: {focus}\n"
        + f"A) {a}\nB) {b}\nAnswer:"
    )


def assess_item(item: dict, score_continuation) -> dict:
    """score_continuation(prompt, ' A'/' B') -> conditional sequence log likelihood.

    The two label orders are both evaluated; positive mean margin favors the
    intended sense. This guards against A/B prior, but does NOT make answer
    probability equal to P(latent sense | context). See docs/EXPERIMENT_DESIGN.md.
    """
    results = {}
    gaps = []
    for correct_is_a in (True, False):
        prompt = make_prompt(item, correct_is_a=correct_is_a)
        a = float(score_continuation(prompt, " A"))
        b = float(score_continuation(prompt, " B"))
        gap = a - b if correct_is_a else b - a
        gaps.append(gap)
        results["correct_as_a" if correct_is_a else "correct_as_b"] = {
            "logp_A": a, "logp_B": b, "correct_minus_foil": gap
        }
    return {
        "item_id": item["item_id"], "family_id": item["family_id"],
        "lexeme_id": item["lexeme_id"], "language": item["language"],
        "condition": item["condition"], "phenomenon": item["phenomenon"],
        "review_status": item["review_status"],
        "mean_correct_minus_foil_logp": sum(gaps) / 2.0,
        "correct_as_a": results["correct_as_a"],
        "correct_as_b": results["correct_as_b"],
    }
