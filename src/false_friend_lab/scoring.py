"""Autoregressive candidate likelihood with explicit token-boundary checks.

Do not reuse the archived ground-truth-conditioned one-in/one-out softmax.
"""
from __future__ import annotations

import math


class TokenBoundaryError(ValueError):
    pass


def continuation_ids(tokenizer, prefix: str, continuation: str) -> tuple[list[int], list[int]]:
    prefix_ids = tokenizer.encode(prefix, add_special_tokens=False)
    whole_ids = tokenizer.encode(prefix + continuation, add_special_tokens=False)
    if not prefix_ids or len(whole_ids) <= len(prefix_ids):
        raise TokenBoundaryError("empty prefix/candidate or no generated candidate tokens")
    if whole_ids[:len(prefix_ids)] != prefix_ids:
        raise TokenBoundaryError(
            "tokenizer resegments the prefix after appending the answer; "
            "cannot assign a defensible conditional likelihood"
        )
    return prefix_ids, whole_ids


def ensure_label_tokens(tokenizer, prefix: str) -> None:
    """Both labels must each add exactly one token from the identical prefix."""
    lengths = [len(continuation_ids(tokenizer, prefix, s)[1]) -
               len(continuation_ids(tokenizer, prefix, s)[0]) for s in (" A", " B")]
    if lengths != [1, 1]:
        raise TokenBoundaryError(f"answer labels are not both single token: {lengths}")


def hf_score(model, tokenizer, prefix: str, continuation: str) -> float:
    """Log p(continuation | prefix). No answer-dependent candidate masking."""
    import torch  # optional: installed only with the pilot extra
    prefix_ids, whole_ids = continuation_ids(tokenizer, prefix, continuation)
    device = next(model.parameters()).device
    ids = torch.tensor([whole_ids], dtype=torch.long, device=device)
    with torch.inference_mode():
        logits = model(input_ids=ids, use_cache=False).logits[0].float()
        log_probs = torch.log_softmax(logits, dim=-1)
    start = len(prefix_ids)
    scores = [log_probs[i - 1, whole_ids[i]].item() for i in range(start, len(whole_ids))]
    result = float(sum(scores))
    if not math.isfinite(result):
        raise FloatingPointError("non-finite answer likelihood")
    return result
