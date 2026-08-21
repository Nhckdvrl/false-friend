# Literature and Open-Source Audit

_Last searched: 2026-08-21_

This document records what is already known, what code/data can be reused, and exactly what remains untested. The project should be re-searched before submission.

## 1. Direct multilingual-LLM false-friend work

### StingrayBench — Cahyawijaya et al., Findings NAACL 2025

**Paper:** “Thank You, Stingray: Multilingual Large Language Models Can Not (Yet) Disambiguate Cross-Lingual Word Senses”  
ACL Anthology: https://aclanthology.org/2025.findings-naacl.178/  
Code: https://github.com/SamuelCahyawijaya/stingraybench  
Dataset: https://huggingface.co/datasets/StingrayBench/StingrayBench

Relevant facts:

- 705 entries overall: 259 true cognates, 446 false friends.
- EN-DE has 196 entries, evenly split 98/98.
- Tasks explicitly target semantic appropriateness and usage correctness.
- The paper reports cross-lingual sense-disambiguation errors and bias toward higher-resource languages.

**What it occupies:** “false friends are hard,” high-resource bias, benchmark-style evaluation.

**What it does not establish:** a causal effect of sharing one lexical representation versus splitting it while holding training data/model constant.

### Doppelganger-JC — Japanese/Chinese homographs

Paper PDF surfaced through ACL/IJCNLP proceedings: https://aclanthology.org/2025.ijcnlp-long.96.pdf

Relevant facts:

- word-meaning, context, and translation tasks;
- generated examples were reviewed by native speakers;
- identifies a “homograph shortcut” where models preserve the misleading shared form in translation.

**Implication:** Japanese-Chinese is valuable later, but a new JA-ZH benchmark is not the contribution.

### SemCog Bench — Liang, Abo Mokh & Alhafni, 2026

arXiv: https://arxiv.org/abs/2606.13218  
Code/data: https://github.com/mbzuai-nlp/SemCog

Relevant facts:

- 1,858 Arabic-Hebrew pairs;
- true cognates, false friends, and loanwords;
- sentence-level semantic disambiguation;
- context only modestly repairs false-friend failures.

**Implication:** ideal later replication resource; does not answer shared-vs-split causal learning dynamics.

### Abuín, Camacho-Collados & Garcia, ACL 2026

**Paper:** “False Friends or Cognates? A Cross-lingual Semantic Ambiguity Evaluation for Galician, Portuguese and Spanish”  
https://aclanthology.org/2026.acl-long.1818/

- six datasets across Galician/Portuguese/Spanish;
- covers cognates, partial false friends, total false friends;
- closely related language pairs can be harder despite linguistic proximity.

**Implication:** another false-friend category benchmark would have poor novelty.

### Uban et al., EMNLP 2025

**Paper:** “Friend or Foe? A Computational Investigation of Semantic False Friends across Romance Languages”  
https://aclanthology.org/2025.emnlp-main.773/

- semantic-divergence/false-friend detection across Romance languages;
- releases cognate/borrowing lexicons.

**Implication:** lexicon induction/detection is not our space.

### Brillant & Pinter, 2026

**Paper:** “Tokenizing Crosslingual Homographs”  
https://arxiv.org/abs/2607.17689

- studies language-agnostic treatment of cross-lingual homographs by tokenizers;
- adds language-specific cues during tokenization;
- reports modest downstream MT improvements in several settings.

**Implication:** tokenizer/lang-tag mitigation is already occupied. Our causal split is an experimental intervention, not a proposed tokenizer product.

## 2. The key contradictory results

### Kallini et al., Findings EMNLP 2025 — controlled vocabulary overlap

**Paper:** “False Friends Are Not Foes: Investigating Vocabulary Overlap in Multilingual Language Models”  
https://aclanthology.org/2025.findings-emnlp.1153/  
Official code: https://github.com/jkallini/false-friends

Core design:

- bilingual autoregressive models;
- EN paired with ES/DE/TR/ZH/AR/SW;
- Full, high-semantic-similarity, low-semantic-similarity, and no-overlap vocabularies;
- token-ID remapping is used to make language vocabularies overlap or become disjoint;
- GPT-2-style 12-layer / 12-head / 768-hidden models;
- CCMatrix training and XNLI/XQuAD transfer evaluation.

Main result relevant here:

- vocabulary overlap generally improves cross-lingual transfer;
- even low-semantic-similarity overlap is usually better than completely disjoint vocabularies.

**Gap left open for us:** their low-similarity token set is not a lexical false-friend experiment with language-specific sense behavior on the same lexical items. Global transfer can improve while local semantic fidelity worsens.

### Škrjanec et al., CMCL 2026 — overlapping Dutch/English word forms

**Paper:** “Is Cross-Lingual Transfer in Bilingual Models Human-Like? A Study with Overlapping Word Forms in Dutch and English”  
https://arxiv.org/abs/2604.07067  
CMCL proceedings: https://aclanthology.org/2026.cmcl-1.pdf

The paper trains causal Transformers under four lexical conditions:

- Full overlap;
- Friends overlap;
- False-friends overlap;
- Minimal overlap.

Key result:

- when embeddings are shared, both friends and false friends show surprisal facilitation;
- regression suggests much of the facilitation is frequency-driven;
- the result differs from the usual human false-friend interference expectation.

Their paper explicitly notes code at `https://github.com/izaskr/cross_lingual_transfer_dutch_english_forms`; as checked on 2026-08-21, the public repository contains only an empty README, so there is no usable implementation to build on at present.

**Gap left open for us:** surprisal is primarily a surface-form prediction outcome. The paper does not causally measure whether the same shared false-friend representation damages language-specific semantic continuation/disambiguation.

## 3. Form versus meaning is a real theoretical distinction

### Marecka et al., Cognition 2021

**Paper:** “False friends or real friends? False cognates show advantage in word form learning”  
DOI: https://doi.org/10.1016/j.cognition.2020.104477

Participants learned L2-like forms and meanings across repeated blocks. False cognates were learned faster than non-cognates in form production, while meaning recognition did not show the same advantage. The authors explicitly distinguish:

- benefit from L1-L2 form overlap;
- benefit from form-meaning overlap;
- possible interference from the old meaning.

**Why it matters:** our form/meaning split is not invented for LMs. But this also means “form and meaning can dissociate” alone is not a sufficient novelty claim. The LM contribution must be the controlled lexical-sharing cause and its training dynamics.

## 4. Frequency and bilingual-processing precedents

### Winther, Matusevych & Pickering, CogSci 2021

**Paper:** “Cumulative Frequency Can Explain Cognate Facilitation in Language Models”  
https://repositories.cdlib.org/uc/item/5d39q2k1

- trains bilingual LMs under different input-presentation conditions;
- demonstrates that cumulative frequency can reproduce cognate facilitation.

**Implication:** “shared forms get more effective frequency and therefore lower surprisal” is not a novel endpoint. Frequency must be treated as a moderator/mechanistic explanation, not the paper headline.

### Bilingual psycholinguistic literature

The bilingual-interactive-activation/BIA+ tradition and interlingual-homograph experiments report task-, context-, and frequency-dependent effects. A useful older experimental result is that inhibition grows when the non-target-language reading is high-frequency relative to the target reading. See discussion in:

- Dijkstra & van Heuven, BIA+ model (2002) and related interlingual-homograph work;
- “Testing a model for bilingual semantic priming with interlingual homographs: RT and N400 effects” and cited Dijkstra experiments;
- subsequent reading/eye-tracking work cited by the CMCL 2026 paper.

**Implication:** a simple “high-frequency language dominates low-frequency language” result is expected and insufficient.

## 5. Broader multilingual training-dynamics work

### Inaba et al., Findings EMNLP 2025

**Paper:** “How a Bilingual LM Becomes Bilingual: Tracing Internal Representations with Sparse Autoencoders”  
https://aclanthology.org/2025.findings-emnlp.725/

- studies training steps/layers/model sizes;
- reports languages are represented more separately early and become increasingly aligned later.

**Implication:** generic “bilingual representations align over checkpoints” is occupied. We require an item-level behavioral collision/separation trajectory before using representation analysis.

### Elhady, Agirre & Artetxe, 2025 — continued pretraining for language adaptation

**Paper:** “Emergent Abilities of Large Language Models under Continued Pretraining for Language Adaptation”  
https://arxiv.org/abs/2506.00288

- language adaptation via continued pretraining;
- catastrophic forgetting can occur early;
- curriculum choices and English replay change downstream emergence.

**Implication:** sequential language exposure and curriculum effects are real, but false-friend lexical path dependence under matched final experience remains a more specific question.

### de Seyssel et al., EMNLP 2025

**Paper:** “Discriminating Form and Meaning in Multilingual Models with Minimal-Pair ABX Tasks”  
https://aclanthology.org/2025.emnlp-main.1210/

- explicitly separates language/form discrimination from semantic-content discrimination in multilingual models.

**Implication:** do not claim that distinguishing “form” and “meaning” as evaluation dimensions is itself new.

### Goworek & Dubossarsky, EMNLP 2025

**Paper:** “Multilinguality Does not Make Sense: Investigating Factors Behind Zero-Shot Cross-Lingual Transfer in Sense-Aware Tasks”  
https://aclanthology.org/2025.emnlp-main.1773/

- sense-aware transfer across 28 languages;
- warns that multilinguality effects can be explained by data/evaluation confounds.

**Implication:** reinforces the need for a same-data, same-architecture causal intervention and lexical-item clustered statistics.

## 6. Training corpus

### OPUS-100

Hugging Face: https://huggingface.co/datasets/Helsinki-NLP/opus-100  
OPUS page: https://opus.nlpl.eu/OPUS-100

- English-centric parallel corpus covering 100 languages;
- DE-EN configuration contains 1,000,000 training pairs plus 2,000 validation and 2,000 test pairs;
- convenient Parquet distribution on Hugging Face.

We use OPUS-100 for the first causal validation because it is compact enough to prepare quickly and large enough for repeated controlled from-scratch runs. If the result becomes publication-critical, replicate on a larger/noisier corpus (e.g. CCMatrix as in Kallini) to rule out corpus-specificity.

## 7. Open-source reuse decisions

### Reused ideas, reimplemented locally

From Kallini et al.:

- language-conditional token-ID remapping;
- controlled bilingual from-scratch training;
- vocabulary compaction for computational efficiency.

We do **not** vendor their repository. Our code narrows the intervention to curated lexical targets and keeps model vocabulary size fixed across shared/split conditions.

### Reused data/resources

- StingrayBench EN-DE lexical items/annotations;
- OPUS-100 natural bilingual text.

### Later confirmatory resources

- SemCog: Arabic-Hebrew semantic replication;
- Doppelganger-JC: Japanese-Chinese semantic/translation replication;
- Romance false-friend resources from Abuín et al. and Uban et al. if a third family is needed.

## 8. Novelty statement we are willing to defend *if the experiment is positive*

Not:

> False friends hurt multilingual LMs.

Not:

> Form and meaning are different metrics.

Not:

> Shared tokens have higher effective frequency.

Potential defensible claim:

> Holding bilingual data, architecture, vocabulary size, and lexical items fixed, forcing a conflicting cross-lingual form to share one lexical representation can improve prediction of the form while selectively degrading the model's ability to predict the natural language-specific continuation; this divergence has a measurable learning trajectory and may or may not persist under matched later experience.

That claim lives or dies with the causal gates in `RESEARCH_MAINLINE.md`.
