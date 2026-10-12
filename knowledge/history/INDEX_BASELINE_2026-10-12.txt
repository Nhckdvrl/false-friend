# Paper and theory index (updated 2026-10-12)

**Reading status is honest and content-dependent**: S1 main methods/results/figures inspected, not full appendices; S2 targeted or partial methods; S3 abstract/metadata or earlier audit only; S0 navigation. **This index is not a claim that all listed papers were fully read.** Link to individual structured note if available. Each note must distinguish paper evidence from reconstructed idea origins.

## 1. Core false-friend phenomena, context, lexical transfer

| Work | Core issue | Reading | Detailed research asset |
|---|---|---|---|
| [Kallini et al., False Friends Are Not Foes, Findings EMNLP 2025](https://aclanthology.org/2025.findings-emnlp.1153/) | semantic quality of shared tokens vs global transfer | S1 | [idea, four-way interventions, baselines, limitations](papers/kallini-2025-vocabulary-overlap.md) |
| [Škrjanec et al., Is Cross-Lingual Transfer Human-Like?, CMCL 2026](https://aclanthology.org/2026.cmcl-1.10/) | Dutch-English FF form surprisal and pooled frequency | S1 | [surprisal not sense](papers/skrjanec-2026-human-like-transfer.md) |
| [Cahyawijaya et al., StingrayBench, Findings NAACL 2025](https://aclanthology.org/2025.findings-naacl.178/) | sentence-level semantic correctness and language bias | S1 | [data/label identity caution](papers/cahyawijaya-2025-stingray.md) |
| [Tanwar et al., Multilingual LLMs Struggle to Link Orthography and Semantics, arXiv v2 2026](https://arxiv.org/abs/2501.09127) | lexical identification, high/low contextual constraints | S1 | [critical prior to route A](papers/tanwar-2026-orthography-semantics.md) |
| [Kitamura et al., Doppelganger-JC, IJCNLP 2025](https://aclanthology.org/2025.ijcnlp-long.96/) | Chinese-Japanese lexical/contextual/translation and copy | S1 | [prompt-task controls](papers/kitamura-2025-doppelganger-jc.md) |
| [Vázquez Abuín et al., False Friends or Cognates?, ACL 2026](https://aclanthology.org/2026.acl-long.1818/) | Romance cross-language WiC, partial/total divergence | S1 | [dataset and matched semantic contrast](papers/abuin-2026-romance-wic.md) |
| [SemCog Bench, 2026](https://arxiv.org/abs/2606.13218) | Arabic-Hebrew sense and script conditions | S3 | [dataset atlas](data/DATASET_ATLAS.md) |
| [Uban et al., Friend or Foe?, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.773/) | Romance semantic divergence detection, lexicon induction | S2 | [atlas and concept map](data/DATASET_ATLAS.md) |
| [Brillant & Pinter, Tokenizing Crosslingual Homographs, 2026](https://arxiv.org/abs/2607.17689) | language-specific tokenization rescue | S3 | no deep note yet |
| [Marecka et al., False friends or real friends?, Cognition 2021](https://doi.org/10.1016/j.cognition.2020.104477) | form vs meaning learning in human L2 | S3 | theory background; needs full read |
| [Winther et al., Cumulative Frequency Can Explain Cognate Facilitation, CogSci 2021](https://repositories.cdlib.org/uc/item/5d39q2k1) | form frequency explanation | S3 | appears in Škrjanec/Kallini genealogy |

| [Östling & Kurfalı, Language Bias under Conflicting Information, arXiv v2 2026](https://arxiv.org/html/2604.07123v2) | multilingual evidence-language preference under conflicting facts (NOT homograph senses) | S1 | [source-language-swap methodology](papers/ostling-kurfali-2026-conflicting-language.md) |
| [Dijkstra, van Hell & Brenders, Bilingualism 2015](https://doi.org/10.1017/S1366728914000388) | human sentence language × semantic-constraint × target-language asymmetry | S2 | [human factorial predecessor](papers/dijkstra-van-hell-brenders-2015-sentence-context.md) |

| [Biloushchenko, Dijkstra & Sandra, Bilingualism 2026](https://www.cambridge.org/core/journals/bilingualism-language-and-cognition/article/effects-of-list-composition-and-task-demands-on-interlingual-homograph-processing-in-unbalanced-trilinguals/4920AF0BB80130ACC9AB4D7388965015) | human homograph inhibition; task schema × list composition | S1 | [task and decision contribution](papers/biloushchenko-dijkstra-sandra-2026-task-list-homographs.md) |

## 2. Representation, concept and causal mechanism

| Work | Core issue | Reading | Asset |
|---|---|---|---|
| [Dumas et al., Separating Tongue from Thought, ACL 2025](https://aclanthology.org/2025.acl-long.1536/) | concept versus output-language activation interchange | S1 | [note](papers/dumas-2025-separating-tongue.md) |
| [Körner et al., When Meanings Meet, EACL 2026](https://aclanthology.org/2026.eacl-long.145/) | training-stage concept emergence; polysemy/copy artifacts | S1 | [strongest nearest-causal note](papers/korner-2026-when-meanings-meet.md) |
| [Ravisankar et al., Can you map it to English?, EACL 2026](https://aclanthology.org/2026.eacl-long.225/) | instance-level alignment, controlled patch donors | S1 | [causal control note](papers/ravisankar-2026-english-alignment.md) |
| [de Seyssel et al., Discriminating Form and Meaning in Multilingual Models, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1210/) | minimal-pair ABX probing | S3 | concept map only |
| [Inaba et al., How a Bilingual LM Becomes Bilingual, Findings EMNLP 2025](https://aclanthology.org/2025.findings-emnlp.725/) | bilingual SAE/representation dynamics | S3 | concept map only |
| [Goworek & Dubossarsky, Multilinguality Does not Make Sense, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1773/) | sense-aware transfer confounds | S3 | concept map only |
| [Conneau et al., Emerging Cross-lingual Structure, ACL 2020](https://aclanthology.org/2020.acl-main.536/) | transfer without shared vocabulary | S3 | [idea genealogy](ideas/IDEA_GENESIS_GRAPH.md) |
| [Limisiewicz et al., Findings ACL 2023](https://aclanthology.org/2023.findings-acl.350/) | task-sensitive vocabulary overlap | S3 | [route B](ideas/RETIRED_HYPOTHESES.md) |
| [Shao et al., ACL 2026](https://aclanthology.org/2026.acl-long.1706/) | bilingual mixture and parallel data contributions | S3 | needs paper note |

## 3. Human bilingual / garden-path / updating

| Work | Core issue | Reading | Asset |
|---|---|---|---|
| [Dijkstra & van Heuven, BIA+, 2002](https://doi.org/10.1017/S1366728902003012) | word identification vs decision processes | S3 | [theory card](theories/BIA_PLUS.md) |
| [Christianson et al., Thematic roles assigned along garden paths linger, 2001](https://doi.org/10.1006/cogp.2001.0752) | persistent human misinterpretation | S3 | [theory card](theories/GOOD_ENOUGH_AND_REVISION.md) |
| [Christianson et al., 2009 paraphrase study](https://pubmed.ncbi.nlm.nih.gov/19210099/) | test task artifact vs lingering meaning | S3 | [theory card](theories/GOOD_ENOUGH_AND_REVISION.md) |
| [Tarin et al., Bilingualism 2026](https://doi.org/10.1017/S1366728925000380) | eye-movement cross-language context interference | S3 | contextual background only |
| [Amouyal et al., When the LM misunderstood the human chuckled, ACL 2025](https://aclanthology.org/2025.acl-long.403/) | human/LLM garden-path understanding, multiple tasks | S2 | [paired note](papers/amouyal-2025-2026-gardenpath.md) |
| [Amouyal et al., Comparing humans/LMs on complex structures, ACL 2026](https://aclanthology.org/2026.acl-long.1040/) | multiple constructions and explanations | S1 | [paired note](papers/amouyal-2025-2026-gardenpath.md) |
| [Yoshida et al., Existence Proof for Garden-Path Surprisal, ACL 2026](https://aclanthology.org/2026.acl-long.1694/) | off-the-shelf model limitation vs impossibility of a theory | S1 | [experimental logic note](papers/yoshida-2026-gardenpath-surprisal.md) |
| [Clark, Levy & Gibson, targeted regressions in noisy-channel GP, CoNLL 2026](https://aclanthology.org/2026.conll-main.25/) | location-specific reanalysis behavior | S1 | [theory-to-measurement note](papers/clark-2026-noisy-channel.md) |
| [Paape & Vasishth, JML 2026](https://doi.org/10.1016/j.jml.2026.104748) | latent-process garden-path effects | S3 | [theory card](theories/GOOD_ENOUGH_AND_REVISION.md) |

| [Ok & Lee, Lost in the Prompt Order, Findings ACL 2026](https://aclanthology.org/2026.findings-acl.1921/) | disentangle prompt order, training bias, option recall vs causal attention via selective patch | S1 | [mechanistic experiment chain](papers/ok-lee-2026-prompt-order.md) |

## 4. Learning history and Cho as scientific-design case studies

| Work | Core issue | Reading | Asset |
|---|---|---|---|
| [Elhady, Agirre & Artetxe, 2025](https://arxiv.org/abs/2506.00288) | continual language adaptation, English replay, forgetting | S3 | [route C](ideas/RETIRED_HYPOTHESES.md) |
| [Arnett et al., ACL 2025](https://aclanthology.org/2025.acl-long.1010/) | bilingual priming / learning schedule | S3 | [route C](ideas/RETIRED_HYPOTHESES.md) |
| [Cho et al., Revisiting In-context Learning Inference Circuit, ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/22d4f952efa13970f0b1ffb22170d416-Abstract-Conference.html) | multi-operation ICL explanation and bypass | S3 | [joint design note](papers/cho-2025-2026-method-genesis.md) |
| [Cho et al., Mechanism of Task-oriented Information Removal, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/105112d52254f86d5854f3da734a52b4-Abstract-Conference.html) | information filtering constructive → natural measures → ablation | S1 | [joint design note](papers/cho-2025-2026-method-genesis.md), [official code](https://github.com/hc495/Verb_subspace) |
| [Yang, Cho et al., Task Vectors, Learned Not Extracted, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/79ada0f9bc4e41192ad5a80d13c8ca7e-Abstract-Conference.html) | train vectors rather than opaque extraction; OV-mediated mechanism | S3 | future Cho-method audit |
| [Yang, Cho et al., Localizing Task Recognition and Task Learning, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/974726d56a6ddfac48486e57d5e798e4-Abstract-Conference.html) | TR/TL decomposition and causal controls | S3 | future Cho-method audit |
| [Tsujimura et al., Belief Consistency, ACL 2026](https://aclanthology.org/2026.acl-long.1860/) | persistent consistency in incremental reasoning independent of task correctness | S3 | candidate *neighbor* for A; deep read needed before formal novelty claim |

## Existing historical record

Earlier [docs/LITERATURE_MATRIX.md](../docs/LITERATURE_MATRIX.md) was a succinct pre-2026-10-11 map. It is now a pointer only; this index controls current reading completeness. [docs/LEGACY_RECORD.md](../docs/LEGACY_RECORD.md) is the retrospective of the invalid EN-DE matching study, not literature evidence for lexical interference.

**Reading debt, highest priority**: ICLR 2025 Cho full paper beyond official abstract (ICLR 2026 full 87-page methods, main results and Appendix controls independently reviewed in user-supplied original PDF), Dumas/Körner detailed patch donor confounds, human lingering misinterpretation full texts, Tanwar v1→v2 changes, Ravisankar same-answer donor analysis, SemCog/Tanwar released dataset fields, new late-2026 evidence-consistency papers.


**2026-10-12 update:** main mechanistic reference [Cho ICLR 2026 detailed full-paper reconstruction](notes/CHO_FULL_PAPER_RECONSTRUCTION_2026.md). Older route B/C references are to [retired research reasoning](ideas/RETIRED_HYPOTHESES.md), **not** active plans. Only [one current research question](ideas/ACTIVE_QUESTION.md).

**Source-method audit:** [Tanwar source-label identifiability and autoregressive Q1→Q2 self-conditioning](notes/TANWAR_IDENTIFIABILITY_AUDIT.md) — key caution before any sense routing inference.
