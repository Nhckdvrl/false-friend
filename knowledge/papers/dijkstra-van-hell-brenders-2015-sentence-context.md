# Dijkstra, van Hell & Brenders 2015 — Sentence Context Effects in Bilingual Word Recognition

- Source PDF: https://bpb-us-e1.wpmucdn.com/sites.psu.edu/dist/3/112775/files/2019/11/Dijkstra-VanHell-Brenders-2015.pdf
- Reading level: S1: complete primary paper methods, stimuli criteria and central figures/results independently reread; not a reanalysis of original human subject data.
- Scientific family: human BIA+ lexical identification, semantic constraint, language switching.

## Scientific question and idea genealogy (INFERENCE)

Rather than arguing whether human lexical access is always language-selective, ask **under what contexts does lexical competition survive**. Study Dutch/English bilingual target-word lexical decision with a crossed host-sentence language and low/high semantic constraint; compare L1 versus L2 target language. The scientific innovation is not a new lexical theory but a counterfactual design revealing task/context *boundaries*.

## Main results (FACT from abstract)

English cognate targets were facilitated under several low/high constraint and switch/no-switch settings. Dutch cognates showed inhibition with low-constraint contexts or English-language switch contexts. Strong semantic evidence modulates cross-language activation but does not always remove it. The asymmetry is informative in humans, and the design is a natural ancestor of Tanwar et al. Task3.

## Non-equivalence and next tests

Reaction time/lexical decision in human bilinguals cannot be equated to model-generated lexical source labels or MCQA logits. Any LLM language-direction asymmetry is already a **known scientific class of phenomenon**; further value requires reproducing word-level behavior and distinguishing competence, prompts, and origin-label non-identifiability.

Unresolved for a human–LLM comparison: full item-frequency matching, subject proficiency and per-trial statistical model; do not claim same mechanism from superficially similar asymmetry.


## Major newly verified methodological choice (2026-10-12)

On printed paper p.6 in the Method/Materials description, the authors **excluded exact-orthographic-identity cognates and interlingual homographs** from their **56 experimental words** (28 cognates + 28 non-cognate matched controls) to make target-word language more identifiable in sentences that switch between Dutch and English. This matters directly for us: the design of a reputable human experiment recognizes that literally identical word forms make *the language of an isolated target stimulus underdetermined*. Our audit of Tanwar's Task3, by contrast, found 29/36/37 exact same-form false cognates EN–DE/FR/ES. Do not merge these designs in a meta-analysis as if their "word language" labels were equivalent.

This criterion is a **valuable negative methodological control**, not evidence that all exact-form false friends are unusable: for semantic-in-context understanding, exact homographs are the main scientific object, but their **hidden source attribution** cannot be treated as an independently observable true label.

## Remaining question

The paper's task targets online lexical decision RT and cognate benefits/inhibitions, not modern instruction-following LLM Task3 forced language-Q1 then free meaning-Q2. The human paper gives source-selection and task-control logic; it does not authorize a direct architectural analogy.
