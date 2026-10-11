# Dataset atlas: available sources versus required causal objects

Inventory date 2026-10-11. Dataset names do not imply fitness for our estimand. Provider license, version, and any derivatives must be checked before redistribution or automated bulk import.

| Resource | Files / source | Ground-truth object | Good use | Invalid shortcut |
|---|---|---|---|---|
| StingrayBench | [HF](https://huggingface.co/datasets/StingrayBench/StingrayBench), [code](https://github.com/SamuelCahyawijaya/stingraybench) | 705 cognate/FF entries across four pairs, semantic appropriateness + usage-correction, some intentionally wrong sentences | Local FF diagnostic, lexical discovery | Its 'true cognate' doesn't mean *natural full-distribution sense alignment*; corrupt sentences are not naturally correct contexts |
| Doppelganger-JC | [GitHub](https://github.com/0017-alt/Doppelganger-JC), questions/jp_zh/homographs.py etc | Chinese/Japanese word, context, translation with competing translations; sample keys target-sentence, target-meaning, correct, wrong1–3 | Same-item sense-vs-copy exploratory contrast | MCQA answer error is not necessarily incorrect internal meaning; source license to verify |
| SemCog | [GitHub](https://github.com/mbzuai-nlp/SemCog) | Arabic/Hebrew FF, true cognate and loanword; diacritized, undiacritized, romanized versions; data/semantic_disambiguation/false_friend JSONL | Script/form robustness and unrelated-language replication | Romanization/diacritic changes alter token/lexical identity; not late evidence stimulus |
| Abuín Romance WiC | [GitHub](https://github.com/mrtva/false-friends-vs-cognates): human-*.tsv and auto-*.tsv | 704 pairs, 1,408 contexts. W1/C1/P1/W2/C2/P2/R/POS, same or different sense in GIVEN contexts; partial/total FF; human vs Wikipedia sentences | Natural contextual sense relation, degree-of-divergence controls | Some word forms differ; R=1 doesn't mean full lexical sense distributions match |
| Tanwar bilingual | [GitHub](https://github.com/EshaanT/Bilingual_processing_LLMs) | Orthography, semantics, high/low contextual constraints (released subsets to audit) | Nearest baseline, detect recycled experiment | Do not presume every paper stimulus is downloadable or independently verified |
| MCL-WiC | [GitHub](https://github.com/SapienzaNLP/mcl-wic), [Zenodo](https://zenodo.org/records/5144515) | multilingual/crosslingual context-sense judgment | Ordinary WSD and ambiguity controls | Not a ready matched false-friend revision contrast |
| XL-WiC | [project](https://pilehvar.github.io/xlwic/) | multilingual contextual sense labels | Test general sense-identification ability | Corpus/context distributions unaligned with FF |
| OPUS-100 | [HF](https://huggingface.co/datasets/Helsinki-NLP/opus-100) | parallel bilingual sentences, NOT two-language sense-distribution labels | Only controlled training with separate causal preflight | More corpus doesn't repair old identity mismatch |

### Checked real file examples

Doppelganger-JC sample file questions/jp_zh/homographs.py exposes target-sentence, target-meaning, correct and wrong1–3, e.g. a Japanese question to be translated to Chinese.
Romance human-es-pt.tsv header W1, C1, P1, W2, C2, P2, R, POS, including contextual false-friend pairs such as Spanish/Portuguese 'azar'.
SemCog tree contains data/false_friend_corpus/false_friend_corpus.json, data/merged_dataset.json and multiple semantic_disambiguation/false_friend/*.jsonl versions.

### Mandatory preflight before using any source as evidence

- State sample unit and label semantics **exactly**; distinguish word pairs and sentences.
- Tag naturally occurring usage vs deliberately corrupted usage.
- Tag exact-identical vs orthographic-near vs capitalization-only forms; no silent normalization.
- Keep original source IDs, sense annotations, direction, POS, provenance and annotation confidence.
- Independently inspect 10–20 random entries and all suspected label conflicts, blinded to desired model outcome.
- Validate which files license redistribution; repo availability != permission for publication of derivatives.
- Hold out lexical types for theory evaluation; don't leak alternate forms/translated copies across split.
- Dataset does not substitute for an independent **late-evidence correction** design.

**Missing from all currently inspected datasets:** a ready, human-audited, fixed-final-sense, initially misleading → late correction, within-language ambiguity-matched sequence. This must be designed and audited as a new condition, not presumed to exist in a WiC label.
