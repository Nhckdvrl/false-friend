import random

import numpy as np
import torch

from false_friend_lab.remap import (
    TargetLexicalRemapper,
    apply_causal_vocab_mask,
    initialize_alias_rows_identically,
)
from false_friend_lab.sampling import language_plan, make_language_rngs, sample_chunk


def test_vocab_identical():
    assert TargetLexicalRemapper(100, [3, 7], "shared").vocab_size == 102
    assert TargetLexicalRemapper(100, [3, 7], "split").vocab_size == 102


def test_split_requires_mask_and_changes_only_exact_positions():
    r = TargetLexicalRemapper(100, [3, 7], "split", "de")
    x = [3, 3, 4, 7, 7]
    mask = [True, False, False, False, True]
    assert r.map_ids(x, "de", mask) == [100, 3, 4, 7, 101]
    assert r.map_ids(x, "en", mask) == x
    try:
        r.map_ids(x, "de")
    except ValueError:
        pass
    else:
        raise AssertionError("split DE without exact mask must fail")


def test_shared_identity_without_mask():
    r = TargetLexicalRemapper(100, [3, 7], "shared")
    assert r.map_ids([3, 8, 7], "de") == [3, 8, 7]


def test_alias_rows_copy_base_exactly():
    class M(torch.nn.Module):
        def __init__(self):
            super().__init__(); self.e = torch.nn.Embedding(12, 4); self.o = torch.nn.Linear(4, 12, bias=False); self.o.weight = self.e.weight
        def get_input_embeddings(self): return self.e
        def get_output_embeddings(self): return self.o
    torch.manual_seed(0); m=M(); r=TargetLexicalRemapper(10,[2,5],"split"); initialize_alias_rows_identically(m,r)
    assert torch.equal(m.e.weight[10],m.e.weight[2]); assert torch.equal(m.e.weight[11],m.e.weight[5])


def test_shared_masks_all_aliases_from_softmax():
    r=TargetLexicalRemapper(5,[1,3],"shared"); logits=torch.zeros(1,2,7); labels=torch.tensor([[1,4]]); m=apply_causal_vocab_mask(logits,labels,r)
    assert torch.all(m[...,5:] < -1e20); assert torch.all(m[...,:5] == 0)


def test_split_uses_one_in_one_out_at_alias_label():
    r=TargetLexicalRemapper(5,[1,3],"split"); logits=torch.arange(14,dtype=torch.float32).reshape(1,2,7); labels=torch.tensor([[5,4]]); m=apply_causal_vocab_mask(logits,labels,r)
    assert m[0,0,5] == logits[0,0,5]; assert m[0,0,1] < -1e20; assert m[0,0,6] < -1e20
    assert torch.all(m[0,1,5:] < -1e20); assert torch.all(m[0,1,:5] == logits[0,1,:5])


def test_step0_shared_split_probabilities_identical_under_row_copy():
    shared=TargetLexicalRemapper(5,[1],"shared"); split=TargetLexicalRemapper(5,[1],"split"); logits=torch.tensor([[[0.1,1.2,-0.4,0.3,0.8,1.2]]])
    s=apply_causal_vocab_mask(logits,torch.tensor([[1]]),shared); q=apply_causal_vocab_mask(logits,torch.tensor([[5]]),split)
    assert torch.equal(torch.log_softmax(s,-1)[0,0,1],torch.log_softmax(q,-1)[0,0,5])


def test_path_schedules_use_same_per_language_samples_and_same_tail_plans():
    phase,tail,micro=3,4,2; ids={"en":np.arange(100),"de":np.arange(1000,1100)}; masks={"en":np.zeros(100,bool),"de":np.zeros(100,bool)}; records={}; tails={}
    for schedule in ["en_then_de","de_then_en"]:
        rngs=make_language_rngs(11); plan_rng=random.Random(11*100_003+41); rec={"en":[],"de":[]}; tplans=[]
        for u in range(2*phase+tail):
            plan=language_plan(schedule,u,phase,micro,plan_rng)
            if u>=2*phase: tplans.append(tuple(plan))
            for lang in plan:
                chunk,_=sample_chunk(ids[lang],masks[lang],4,rngs[lang]); rec[lang].append(int(chunk[0]))
        records[schedule]=rec; tails[schedule]=tplans
    assert records["en_then_de"]["en"] == records["de_then_en"]["en"]
    assert records["en_then_de"]["de"] == records["de_then_en"]["de"]
    assert tails["en_then_de"] == tails["de_then_en"]
