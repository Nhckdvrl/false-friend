# Hwang et al. — LLMs can be easily Confused by Instructional Distractions

- Primary: https://aclanthology.org/2025.acl-long.957/ (ACL 2025 main).
- Reading S2: §§3–5, Tables 3–6, Appendix A.3–A.4; not a reproduction. The [erratum](https://aclanthology.org/2025.acl-long.957e1.pdf) only clarifies the corresponding author; it explicitly leaves technical content unchanged.

## What the experiment changes

DIM-Bench crosses four text-transformation instructions with five types of input tasks. The intended operation is to transform the input, while the input can itself invite a response. Evaluation combines a model judge with an output-length diagnostic. Direct reminders, reasoning prompts and context-length conditions are follow-ups; sampled generations use temperature 0.7, with a repetition penalty for Llama.

## Idea genesis — INFERENCE

The scientific opening is a practical mismatch: a model capable of both operations may execute the operation afforded by the data instead of the requested transformation. Separating instruction type from input type exposes the mismatch more clearly than one aggregate instruction-following score.

## Experimental critique

Task switch must be distinguished from a bad translation or an incomplete output. A length heuristic cannot establish that distinction by itself: tokenization ratios, verbosity and truncation can produce short responses. The length manipulation also changes content unless the same question and relevant evidence are controlled. Thus the proposed distance-from-instruction explanation needs a positional intervention, not just a longer-input comparison. Single sampled runs leave uncertainty about stability; model-judge agreement is not independent human verification.

## Distance and transfer

Our task is lexical knowledge selection, not processing embedded instructions. This paper motivates classifying *what operation the output performed* before labeling a semantic failure. For a false-friend pair, switching to the other target, translating the whole sentence, or comparing propositions are distinct from choosing the wrong sense. It does not establish that any of those causes explain our data.

A useful further test is to fix both sentences and separately request word-meaning equivalence versus proposition equivalence, with their gold relations orthogonal. This would discriminate an operation switch from missing lexical knowledge; merely appending a stronger instruction would show repair without identifying the original cause.
