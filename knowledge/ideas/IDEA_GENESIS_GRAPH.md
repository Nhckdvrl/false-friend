# Historical idea genealogies — NOT active research directions (2026-10-12)

The original Route A/B/C proposals were discontinued after nearest-paper, identifiability and source-data review. Arrows below are scientific idea-genesis exercises **only**; active work is now [multilingual evidence-based sense arbitration](ACTIVE_QUESTION.md), with [rejected alternatives](RETIRED_HYPOTHESES.md).

# Idea genealogy — how mature-domain papers grow from earlier questions

All arrows marked **INFERENCE**: conceptual reconstruction of possible idea formation, not a quote about authors' thought processes. This is a practical idea-generation asset, not a historical assertion about anyone's mind.

## Branch 1: the value of shared lexical representations

Conneau 2020 (transfer exists without shared vocabulary)
→ Is sharing necessary, or merely beneficial under some conditions?
→ Kallini 2025 (Full / High / Low / No overlap, six bilingual pairs)
→ Empirical surprise: low-semantic-similarity shared IDs still often beat disjoint vocab on global transfer.
→ Multiple rival causal accounts: pooled frequency, effective parameter capacity, valid semantic anchors, graph connectivity
→ **Route B**: manipulate anchor semantic correctness and topology *independently* of frequency/capacity; try to predict sign on new remappings.

A parallel thread:
Winther 2021 (cumulative frequency facilitates shared forms)
+ human interlingual homograph experiments
→ Škrjanec 2026 (Dutch-English friends/false friends, target surprisal)
→ Realization: easier prediction of the written form is NOT a statement about correctly selected meaning.
**Idea lesson:** apparent contradiction may be a measurement mismatch; first reconcile dependent variables rather than inventing a new framework.

## Branch 2: language-specific sense errors

BIA+ 2002 (word identification versus task-level decision)
→ Stingray 2025 (localized cross-language false-friend sense benchmark + language bias)
→ Tanwar 2025/v2 2026 (word identification, semantic judgment, contextual strength)
→ Doppelganger-JC 2025 (word meaning vs sentence meaning vs translation, homograph copying)
→ Abuín 2026 (cross-language WiC, human vs Wikipedia, partial vs total false friends)
→ **Route A**: only if an effect remains beyond *all* these neighboring tasks/contexts, test cross-language-specific residual meaning use after late evidence.

Parallel intervention thread:
language-agnostic probing → Dumas 2025 (concept/output language patching)
→ Körner 2026 (training-time concept emergence; copy and polysemy error categories)
→ Ravisankar 2026 (instance-level alignment and **same answer label / different semantics** negative donors).
**Idea lesson:** a causal rescue with a patched answer is not yet proof that a concept was transferred.

## Branch 3: incremental interpretation and reanalysis

Christianson 2001/2009 (partially lingering garden-path misinterpretation)
→ good-enough vs full reanalysis debates; noisy channel
→ Amouyal 2025/2026 (humans/LLMs and diverse garden-path structures)
→ Yoshida 2026 (fine-tuned model can explain reading-time slowdown through surprisal; repairs the logical inference about impossibility)
→ Clark 2026 (specific candidate corruption location predicts where a human reader regresses).
**Idea lesson:** explanation advances by **changing what must be discriminated**, not necessarily inventing a new task.

## Cho as methodological, not content, genealogy

ICL induction / copying / task vectors → Cho ICLR 2025 (Encode/Merge/Retrieve-Copy with bypass) → counterexample to simple label copying (missing correct label) → Cho ICLR 2026 (constructive low-rank information removal, observation in actual few-shot ICL, targeted ablation).
What we want to imitate is the logical sequence **rival explanation → discriminating manipulation → remaining inference gap → causal or predictive test**, not a paper's exact experimental architecture.

## Five questions to generate ideas from the graph

1. Which nearest paper actually supports the claim, and how strong is its quantifier?
2. Is the apparent contradiction on the SAME measured variable?
3. Which two distinct mechanisms yield the same current evidence?
4. What is the **cheapest valid intervention** that predicts opposite outcomes under them?
5. If it succeeds, what old explanation must be revised, and can it predict held-out cases?

Merely adding more languages, larger models, more probes or more metrics to an occupied claim is usually too small a contribution.
