import torch
from torch import nn

from false_friend_lab.remap import TargetLexicalRemapper, initialize_alias_rows_from_base


class DummyLM(nn.Module):
    def __init__(self, vocab=22, dim=8):
        super().__init__()
        self.emb = nn.Embedding(vocab, dim)
        self.out = nn.Linear(dim, vocab, bias=False)
        self.out.weight = self.emb.weight
    def get_input_embeddings(self): return self.emb
    def get_output_embeddings(self): return self.out


def test_vocab_is_identical_across_conditions():
    shared = TargetLexicalRemapper(100, [3, 7, 20], "shared")
    split = TargetLexicalRemapper(100, [3, 7, 20], "split")
    assert shared.vocab_size == split.vocab_size == 103


def test_split_changes_only_masked_target_occurrences():
    remap = TargetLexicalRemapper(100, [3, 7], "split", split_lang="de")
    ids = torch.tensor([1, 3, 4, 7, 3, 9])
    mask = torch.tensor([0, 1, 0, 0, 0, 0], dtype=torch.bool)
    assert remap.map_tensor(ids, "en", mask).tolist() == ids.tolist()
    assert remap.map_tensor(ids, "de", mask).tolist() == [1, 100, 4, 7, 3, 9]


def test_split_requires_exact_mask():
    remap = TargetLexicalRemapper(100, [3], "split")
    try:
        remap.map_ids([3], "de")
    except ValueError:
        pass
    else:
        raise AssertionError("expected exact-mask requirement")


def test_alias_initialization_copies_base_rows():
    remap = TargetLexicalRemapper(20, [3, 7], "split")
    model = DummyLM(vocab=22)
    initialize_alias_rows_from_base(model, remap)
    w = model.get_input_embeddings().weight
    assert torch.equal(w[20], w[3])
    assert torch.equal(w[21], w[7])
