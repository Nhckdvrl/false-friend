# Tanwar Task3 measurement and method audit: source labels, answer order, and word senses

**Sources:** [arXiv v2 §4.3](https://arxiv.org/html/2501.09127v2); [data implementation](https://github.com/EshaanT/Bilingual_processing_LLMs/blob/281a67eac6ddbe5445e1c10277e5833d40d72125/src/data.py), especially `Task3.get_test_prompts`; [generation runner](https://github.com/EshaanT/Bilingual_processing_LLMs/blob/281a67eac6ddbe5445e1c10277e5833d40d72125/task-gen.py) and `src/llm.py`. Main paper v2 methods/results and actual repo code checked. **No new model trial yet**.

## Existing empirical puzzle (FACT, not our new result)

Tanwar et al. report approximately **70%** contextual correction when non-English homographs appear in English sentence contexts, versus **34%** when English homographs appear in non-English contexts (Fig.4, `4.3). Meanings of inserted FR/DE/ES words were often mapped to English senses. The authors categorize outputs into correction type 1, correction type 2, confusion and no-correction through human interpretation of generated answers.

These “corrections” are ***response categories***, not evidence that the model sequentially repaired a hidden representation of a previously processed token.

## Code mechanism 1: unobservable lexical source for exact forms

For each row, the original Task3 prompt loops over `lang=en,L2` and uses `word=row[lang]`. Normal condition uses sentence `high_lang`/`low_lang`. Cross condition uses sentence from the OTHER language but keeps word from the original `lang`. Sentence string is constructed by replacing `<MASK>` with the double-quoted word.

For pairs with EXACT same case-sensitive spelling, the normal and cross **SENTENCE STRINGS** under the same host language are literally identical, although their *dataset source-language index* differs. The input alone does not identify which language the inserted instance “came from”.

**Qualification:** the full prompts are NOT identical. Normal setup says “sentence in German/English”; cross setup explicitly says “code-mix ... EN–L2”, then requests language, meaning, coherence. The model can use **pragmatic task instruction** to infer “source must be the other language,” which is distinct from detecting the true source from orthography. Source row identity is a convention, not an observable word property in the exact-string collision subset.

## Code mechanism 2: sequential answer self-conditioning

The original cross task puts **Q1 What is language?** before **Q2 What is meaning?** before **Q3 Is sentence meaningful?**. `llm_call` generates up to 512 tokens in one sequence. Therefore the text generated for Q1 becomes part of the model's causal prefix when it produces Q2; Q2 can be influenced by Q1 **even with identical original sentence**. The paper's correlation between model-reported word language and interpreted word meaning cannot be assumed to isolate a preexisting shared internal decision.

This is not an accusation of implementation error: it is a scientific **measurement limitation** and an opportunity for a small causal manipulation of task format.

## Most informative next experiment (not yet executed)

- First, reproduce the original three-question Task3 prompts and generation on the authors' specific stimulus set and a pinned multilingual model. Original reported LLaMA3.1 8B, but any other model must be marked as a new transfer check, not a faithful replication.
- Within the SAME item: original `Q1→Q2→Q3`, `Q2 only`, `Q1 only`, and `Q2→Q1`. Prefer pre-reg semantic evaluations of Q2 that do not repeat the original homograph.
- Direct causal prompt conditioning: insert a FIXED Q1 answer explicitly (host language vs putative source language vs unknown) then ask Q2, with all sentence content and option verbalizers fixed.
- Separate whether language label is **identifiable**: exact form plus no explicit source tag, near form, and exact form with externally authenticated source language. Never interpret hidden source index as a model-readable fact.
- Check if ~70/34 survives on **independent semantic consequence questions**, not only sequential free text, and after lexical knowledge and language proficiency controls.
- Sample by lexical TYPE, not thousands of sentence variants; cross-host sentence strength and domain must be matched when comparing languages.

## Research value and failure

If asymmetry vanishes after removing Q1 self-conditioning or under non-copy sense measurements, the conclusion should be narrower: output/prompt effects, not a hidden semantic gate. If it survives **validated source labels** and matched language ability on unseen word types, it offers a genuine candidate question about direction-specific contextual meaning arbitration.

This is Cho-like because we start from an existing published anomaly and challenge the smallest assumption needed to interpret it. The experiment is designed to REFUTE a preferred explanation, not manufacture a new benchmark.


## 2026-10-12 material grammar preflight (SOURCE ONLY)

Of 29 exact-spelling EN–DE source FALSE COGNATE entries, **22 are lexicon category N and written lowercase** in the released source. German common nouns normally require capitalization. Substitution of lowercase 'brand', 'gift', 'kind' into German noun contexts can therefore create a grammatical/case anomaly that contaminates any semantic-source judgement. It is a **risk flag**, not a proof every stimulus is grammatically impossible; metalinguistic quotes and unusual spellings require native adjudication.

The first Qwen2.5-0.5B CPU smoke sampled source ID 180 'brand'. For English-source word in a German-host context, answer-to-meaning-only incorrectly targeted *Holz* rather than the highlighted word 'brand'. That six-generation test is **inadequate evidence of a sense-selection mechanism** and the material is risky due to noun casing. [Unreviewed raw six generations](https://github.com/Nhckdvrl/false-friend/actions/runs/38158541047/artifacts/11709752090). The pilot is retained transparently as a methodological failure.

For the next code smoke, source ADJ forms IDs 261 'genial', 264 'blank', 272 'stark' were preselected for relatively natural EN and DE contexts **after the failed first smoke**; they are NOT a preregistered scientific sample, and definitions/collocations still need independent human review. Use a contrastive **A/B logprob** with swapped gloss order and externally stated Q1 answer; candidate scoring is not a latent-sense posterior.

This source preflight is necessary before attempting a faithful reproduction of original paper's 70/34 directional claim, which might include many invalid/linguistically inequivalent material cells.
