from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

import torch


@dataclass(frozen=True)
class TargetLexicalRemapper:
    """Language-conditional remapping of *exact lexical occurrences* only.

    Base compact ids occupy [0, base_vocab_size). Every retained lexical target
    receives one reserved alias row. Shared and split conditions therefore have
    identical model shapes and parameter counts. The split condition remaps only
    masked occurrences in ``split_lang``; unmasked uses of the same subword id are
    left untouched.
    """

    base_vocab_size: int
    target_token_ids: List[int]
    condition: str
    split_lang: str = "de"

    def __post_init__(self) -> None:
        if self.condition not in {"shared", "split"}:
            raise ValueError("condition must be 'shared' or 'split'")
        if len(set(self.target_token_ids)) != len(self.target_token_ids):
            raise ValueError("target_token_ids must be unique")
        if any(t < 0 or t >= self.base_vocab_size for t in self.target_token_ids):
            raise ValueError("target token id outside compact base vocabulary")

    @property
    def alias_map(self) -> Dict[int, int]:
        return {tid: self.base_vocab_size + i for i, tid in enumerate(self.target_token_ids)}

    @property
    def reverse_alias_map(self) -> Dict[int, int]:
        return {v: k for k, v in self.alias_map.items()}

    @property
    def vocab_size(self) -> int:
        return self.base_vocab_size + len(self.target_token_ids)

    def map_ids(self, ids: Iterable[int], lang: str, exact_mask: Sequence[bool] | Sequence[int] | None = None) -> List[int]:
        ids = [int(x) for x in ids]
        if self.condition == "shared" or lang != self.split_lang:
            return ids
        if exact_mask is None:
            raise ValueError("split-language remapping requires exact_mask")
        if len(exact_mask) != len(ids):
            raise ValueError("exact_mask length must equal ids length")
        amap = self.alias_map
        return [amap.get(tid, tid) if bool(flag) else tid for tid, flag in zip(ids, exact_mask)]

    def map_tensor(self, ids: torch.Tensor, lang: str, exact_mask: torch.Tensor | None = None) -> torch.Tensor:
        if self.condition == "shared" or lang != self.split_lang:
            return ids
        if exact_mask is None:
            raise ValueError("split-language remapping requires exact_mask")
        if exact_mask.shape != ids.shape:
            raise ValueError("exact_mask shape must equal ids shape")
        out = ids.clone()
        for base_id, alias_id in self.alias_map.items():
            out[(ids == base_id) & exact_mask.bool()] = alias_id
        return out

    def canonical_id(self, token_id: int) -> int:
        return self.reverse_alias_map.get(int(token_id), int(token_id))

    def alias_id(self, base_id: int) -> int:
        return self.alias_map[int(base_id)]


def initialize_alias_rows_from_base(model, remapper: TargetLexicalRemapper) -> None:
    """Copy base rows into all aliases in both conditions before training."""
    with torch.no_grad():
        inp = model.get_input_embeddings().weight
        out_mod = model.get_output_embeddings()
        out = out_mod.weight if out_mod is not None else None
        for base_id, alias_id in remapper.alias_map.items():
            inp[alias_id].copy_(inp[base_id])
            if out is not None and out.data_ptr() != inp.data_ptr():
                out[alias_id].copy_(out[base_id])
