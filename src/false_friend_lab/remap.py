from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

import torch


@dataclass(frozen=True)
class TargetLexicalRemapper:
    """Language-conditional exact-lexical remapping with fixed model size.

    Base ids occupy ``[0, base_vocab_size)``. Each selected target gets one
    reserved alias row in *both* shared and split models. In the primary EN-DE
    contrast, only exact standalone German lexical occurrences are routed to
    aliases in the split condition. Unmasked subword reuse is never changed.
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
        return {t: self.base_vocab_size + i for i, t in enumerate(self.target_token_ids)}

    @property
    def reverse_alias_map(self) -> Dict[int, int]:
        return {alias: base for base, alias in self.alias_map.items()}

    @property
    def vocab_size(self) -> int:
        return self.base_vocab_size + len(self.target_token_ids)

    def map_ids(
        self,
        ids: Iterable[int],
        lang: str,
        lexical_mask: Sequence[bool] | None = None,
    ) -> List[int]:
        out = [int(x) for x in ids]
        if self.condition == "shared" or lang != self.split_lang:
            return out
        if lexical_mask is None:
            raise ValueError("split-language remapping requires an exact lexical_mask")
        if len(lexical_mask) != len(out):
            raise ValueError("lexical_mask length must equal ids length")
        aliases = self.alias_map
        for i, is_lexical in enumerate(lexical_mask):
            if is_lexical and out[i] in aliases:
                out[i] = aliases[out[i]]
        return out

    def map_tensor(self, ids: torch.Tensor, lang: str, lexical_mask: torch.Tensor | None = None) -> torch.Tensor:
        if self.condition == "shared" or lang != self.split_lang:
            return ids
        if lexical_mask is None or lexical_mask.shape != ids.shape:
            raise ValueError("split-language tensor remapping requires an aligned lexical_mask")
        out = ids.clone()
        for base_id, alias_id in self.alias_map.items():
            hit = lexical_mask.bool() & (out == base_id)
            out.masked_fill_(hit, alias_id)
        return out

    def canonical_id(self, token_id: int) -> int:
        return self.reverse_alias_map.get(int(token_id), int(token_id))


def initialize_alias_rows_identically(model, remapper: TargetLexicalRemapper) -> None:
    """Copy every reserved alias row exactly from its base row at step zero."""
    emb = model.get_input_embeddings().weight
    with torch.no_grad():
        for base_id, alias_id in remapper.alias_map.items():
            emb[alias_id].copy_(emb[base_id])
    out = model.get_output_embeddings()
    if out is not None and out.weight.data_ptr() != emb.data_ptr():
        with torch.no_grad():
            for base_id, alias_id in remapper.alias_map.items():
                out.weight[alias_id].copy_(out.weight[base_id])


def apply_causal_vocab_mask(
    logits: torch.Tensor,
    labels: torch.Tensor,
    remapper: TargetLexicalRemapper,
) -> torch.Tensor:
    """Make shared/split output normalization exactly comparable.

    Reserved aliases must not silently enlarge split's softmax. At every
    prediction position exactly ``base_vocab_size`` rows are active:

    * shared (and ordinary split positions): all aliases are masked;
    * split exact-DE target label: all aliases are masked except the correct
      alias, and the corresponding base row is masked (one-in / one-out).

    Thus the only intervention is which initially-identical lexical row receives
    DE target gradients and is later used as DE target input.
    """
    if logits.shape[:-1] != labels.shape:
        raise ValueError("logits prefix shape must match labels")
    if logits.shape[-1] != remapper.vocab_size:
        raise ValueError("logit vocabulary does not match remapper")

    alias_ids = list(remapper.alias_map.values())
    if not alias_ids:
        return logits
    masked = logits.clone()
    floor = torch.finfo(masked.dtype).min
    masked[..., alias_ids] = floor

    if remapper.condition == "shared":
        if torch.any(labels >= remapper.base_vocab_size):
            raise ValueError("shared condition must never contain alias labels")
        return masked

    # In split, an alias label denotes exactly one DE lexical target. Restore
    # that alias's original logit and remove its paired base row at that position.
    for base_id, alias_id in remapper.alias_map.items():
        hit = labels == alias_id
        if torch.any(hit):
            masked[..., alias_id] = torch.where(hit, logits[..., alias_id], masked[..., alias_id])
            masked[..., base_id] = torch.where(
                hit,
                torch.full_like(masked[..., base_id], floor),
                masked[..., base_id],
            )
    return masked
