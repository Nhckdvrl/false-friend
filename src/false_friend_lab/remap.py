from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

import torch


@dataclass(frozen=True)
class TargetLexicalRemapper:
    """Language-conditional target-token remapping with a fixed vocabulary size.

    Base compact token ids occupy ``[0, base_vocab_size)``.  Each selected target
    token receives one reserved alias row.  The alias rows exist in *both* shared
    and split conditions, so parameter count and output-softmax cardinality are
    identical across the causal comparison.

    In the primary EN-DE experiment English keeps the base id.  German uses the
    alias only in the ``split`` condition.  All non-target tokens are identical
    across conditions.
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
        return {
            token_id: self.base_vocab_size + i
            for i, token_id in enumerate(self.target_token_ids)
        }

    @property
    def vocab_size(self) -> int:
        return self.base_vocab_size + len(self.target_token_ids)

    def map_ids(self, ids: Iterable[int], lang: str) -> List[int]:
        ids = list(ids)
        if self.condition == "shared" or lang != self.split_lang:
            return ids
        aliases = self.alias_map
        return [aliases.get(int(token_id), int(token_id)) for token_id in ids]

    def map_tensor(self, ids: torch.Tensor, lang: str) -> torch.Tensor:
        if self.condition == "shared" or lang != self.split_lang:
            return ids
        out = ids.clone()
        for base_id, alias_id in self.alias_map.items():
            out.masked_fill_(out == base_id, alias_id)
        return out

    def canonical_id(self, token_id: int) -> int:
        reverse = {alias: base for base, alias in self.alias_map.items()}
        return reverse.get(int(token_id), int(token_id))
