# Ohmer, Bruni & Hupkes — From Form(s) to Meaning

- Primary: https://aclanthology.org/2024.cl-4.10/ (Computational Linguistics 50(4), 2024).
- Reading S2: §§3.1–3.4, 5.1, 7.1–7.4, Tables 3–4; not all benchmark appendices or an empirical reproduction.
- Author terminology: “sense” here includes alternative task formulations, not a WordNet lexical sense. Do not merge these objects with our WiC labels.

## Experimental reasoning

The authors generate alternative formulations with the tested model, evaluate consistency, check translation quality, and independently vary instructions versus input data. They also examine consistency conditional on correctness and language–information matching. These experiments target several explanations of the same initial inconsistency, rather than merely adding datasets.

## Idea genesis and distance — INFERENCE

The conceptual move is to turn form-independent meaning into a behavioral invariance requirement. Self-generated alternatives reduce one source of mismatch, but generation does not certify that the model itself treats them as equivalent. The value of §7 is its return to competing explanations after the initial measurement.

Our independent-gloss intervention changes a potential competitor while keeping task and target fixed; it is not a replication of multilingual paraphrase consistency. A nontrivial extension would predict *which meaning* is substituted under competition, beyond finding another inconsistency.

## Critical assessment

Instruction-only changes can alter answer priors, style and decoding, so their effect is not a pure measurement of task interpretation. Input-only changes can also alter instruction binding. These are useful behavioral contrasts, not identifiable internal modules. High average translation quality does not eliminate rare meaning-changing translations concentrated on failing items.

The argument that consistent errors are stronger evidence of shared meaning assumes errors were unlikely to be learned independently. Correlated training sources, shared misconceptions and response priors offer alternatives. Conversely, inconsistent correct/incorrect outputs do not uniquely imply separate knowledge stores.

## Transfer to this project

Keep an invariance test separate from its proposed explanation. First establish target-level correctness; then change competitor, task wording or requested relation in separate contrasts. Do not use self-generated gloss agreement as truth, and do not call successful glossary assistance a discovery of natural computation. The [fourth-round design](../notes/ROMANCE_ORTHOGONAL_DESIGN_2026-10-13.md) uses this separation. If clear authored material has no failures, retain it as a boundary and return to source cases rather than making templates increasingly adversarial.
