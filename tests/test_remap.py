import torch

from false_friend_lab.remap import TargetLexicalRemapper


def test_vocab_is_identical_across_conditions():
    shared = TargetLexicalRemapper(100, [3, 7, 20], "shared")
    split = TargetLexicalRemapper(100, [3, 7, 20], "split")
    assert shared.vocab_size == split.vocab_size == 103


def test_only_split_language_targets_change():
    remap = TargetLexicalRemapper(100, [3, 7], "split", split_lang="de")
    x = torch.tensor([1, 3, 4, 7, 9])
    assert remap.map_tensor(x, "en").tolist() == x.tolist()
    assert remap.map_tensor(x, "de").tolist() == [1, 100, 4, 101, 9]


def test_shared_is_identity():
    remap = TargetLexicalRemapper(100, [3, 7], "shared")
    assert remap.map_ids([3, 8, 7], "de") == [3, 8, 7]
