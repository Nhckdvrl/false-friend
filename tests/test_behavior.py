from false_friend_lab.behavior import assess_item, make_prompt
from false_friend_lab.scoring import TokenBoundaryError, continuation_ids, ensure_label_tokens
from test_schema import example


def test_order_swap_changes_options():
    item = example()
    p1 = make_prompt(item, correct_is_a=True)
    p2 = make_prompt(item, correct_is_a=False)
    assert "A) cream" in p1 and "B) cream" in p2
    assert "Dutch" in p1


def test_implicit_language_cue():
    p = make_prompt(example(explicit_language=False), correct_is_a=True)
    assert "written in Dutch" not in p


def test_balanced_margin():
    def fake_scorer(prompt, continuation):
        correct_label = " A" if "A) cream" in prompt else " B"
        return 3.0 if continuation == correct_label else -1.0
    result = assess_item(example(), fake_scorer)
    assert result["mean_correct_minus_foil_logp"] == 4.0
    assert result["correct_as_a"]["correct_minus_foil"] == 4.0
    assert result["correct_as_b"]["correct_minus_foil"] == 4.0


class DummyTokenizer:
    def encode(self, text, add_special_tokens=False):
        assert add_special_tokens is False
        return [ord(c) for c in text]


class BrokenTokenizer:
    def encode(self, text, add_special_tokens=False):
        result = [ord(c) for c in text]
        return result[:-3] if text.endswith(" A") else result


def test_tokenizer_boundary_check():
    ids1, ids2 = continuation_ids(DummyTokenizer(), "Answer:", " A")
    assert ids2[:len(ids1)] == ids1
    with __import__("pytest").raises(TokenBoundaryError):
        continuation_ids(BrokenTokenizer(), "Answer:", " A")


def test_single_token_label_gate():
    with __import__("pytest").raises(TokenBoundaryError, match="single token"):
        ensure_label_tokens(DummyTokenizer(), "Answer:")
