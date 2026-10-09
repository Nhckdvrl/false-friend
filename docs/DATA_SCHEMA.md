# Research dataset contract — strict JSONL

A single row represents a **contextual sense-choice observation**, not a lexical concept identity. Context variants are linked by family_id and lexeme_id; never infer corpus-wide semantic identity from a published label.

## Required keys

| Field | Type | Meaning |
|---|---|---|
| item_id | unique string | stable ID for the exact context and condition |
| family_id | string | groups controlled variants of one intended semantic proposition |
| lexeme_id | string | sampling cluster for a cross-language form/sense object |
| language | code string | current supported: en, nl, de, fr, es, zh, ja, id, ms |
| target_form | string | exact lexical form shown (not normalized across case) |
| context | string | independently checked natural sentence/context |
| gloss_correct | string | intended meaning rendered as an option |
| gloss_competitor | string | a plausible rival meaning, same gloss language |
| condition | string | e.g. baseline, explicit_language, early_evidence, late_evidence, paraphrase |
| phenomenon | category | cross_lingual_false_friend, within_language_polysemy, unambiguous |
| review_status | category | illustrative or verified |
| source_ref | string | dictionary/corpus URL, stable ID, or citation |
| explicit_language | boolean | whether the prompt explicitly names language |

Optional field: reviewers — list of independently assigned reviewer IDs; **verified requires at least two unique reviewers**. Add POS, original source sentence, language pair, source licenses, tokenization checks, gloss paraphrase IDs, review notes, and sense-frequency estimates when material. Any other fields are retained by validator.

Rows marked illustrative (including data/examples/illustrative.jsonl) are **blocked by default**. To test code, use --allow-illustrative; the preflight explicitly reports scientific_claims_permitted=false. Do not promote sample rows to verified without human review.

## Validation rules

- All required values are typed and nonblank; no duplicate item_id.
- Correct and foil glosses must be distinct.
- Exact standalone target_form must occur in context except in paraphrase controls.
- Paraphrase condition must *remove* the ambiguous lexical word as a whole form.
- Verified rows require traceable source_ref and two distinct reviewers.
- Reviewers are independent of the model outputs being compared.
- Never silently convert `arm` → `Arm` or vice versa to manufacture same-form controls. Word class and intended meaning can change.
- Different example translations are **not** evidence that the complete P(sense|form,language) distributions are aligned.

## Paired contrasts

Comparing conditions uses rows with the same family_id; matched lexical type alone is not enough. Multiple contexts per lexeme are not independent lexical types. A condition may be missing for a family: exploratory summaries will only pair available baseline–condition families and report the count. A confirmatory dataset must preregister its coverage criteria separately.

## Data pipeline stages

1. Candidate lexical inventory (not automatically verified).
2. Curate sentences/semantics; independent review, license audit, class and case check.
3. Freeze item, family, controls, answer glosses and optional paraphrases.
4. Split **by lexeme_id** for future holdout predictions; preserve paired contexts.
5. Frozen preflight; test run for label tokenization/templating; evaluate all order pairs.
6. Audit worst cases manually before asserting semantic rather than output artifacts.

No script in this repository claims to have completed steps 1–4. Example lines are workflow illustrations, not experimental data.
