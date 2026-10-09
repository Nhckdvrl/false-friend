# Literature map — verified links, claims covered, and plausible open questions

Reviewed 2026-10-09. **Scope note:** Papers whose full PDFs were inspected are distinguished from bibliographic / abstract-level checks. Neither establishes priority over unsearched work; refresh before writing a novelty claim.

## Direct empirical literature (closest competition)

| Work | Established / experiment | Boundary relevant to us | Reading status |
|---|---|---|---|
| [Cahyawijaya et al., StingrayBench, Findings NAACL 2025](https://aclanthology.org/2025.findings-naacl.178/) | Four pairs; cross-lingual sense errors and resource-language biases | Benchmark category is *not* natural corpus matched sense distribution; does not locate processing failure | Paper + dataset-method sections inspected |
| [Kallini et al., False Friends Are Not Foes, Findings EMNLP 2025](https://aclanthology.org/2025.findings-emnlp.1153/) | Controlled six bilingual pairs with varying token vocabulary overlap; global XNLI/XQuAD transfer improves with overlap, even some low-similarity overlaps | Global transfer / embedding alignment is not local target-sense correctness; sharing conditions carry distribution/capacity complications | Full PDF, results table and limitations inspected |
| [Škrjanec et al., Is Cross-Lingual Transfer in Bilingual Models Human-Like?, CMCL 2026](https://aclanthology.org/2026.cmcl-1.10/) | English/Dutch controlled word-form overlap, embedded contextual similarity and surprisal; false friends show facilitation linked to both-language frequency | Form surprisal ≠ choice of correct dictionary sense in sentence; human reading comparison not LLM causal sense-revision | Full PDF, fig. 3/4, regression and discussion inspected |
| [Körner et al., When Meanings Meet, EACL 2026](https://aclanthology.org/2026.eacl-long.145/) | Cross-lingual concept activation patching across 26 EuroLLM checkpoints; shared space develops early; manual error labels distinguish copy, synonym, hyper/hyponym, polysemy | Already exposes homograph-copy artifact and sense shifts. Novelty must go beyond simple patch-and-fix and quantify conditional revision | Full PDF methodology, result and manual error sections inspected |
| [Dumas et al., Separating Tongue from Thought, ACL 2025](https://aclanthology.org/2025.acl-long.1536/) | Swap concept independently of output language using causal activation patching | Separation of language and concept is not novel; selection after *conflicting local evidence* is narrower | Abstract/method overview verified; full text needs targeted reread |
| [Ravisankar et al., Can you map it to English?, EACL 2026](https://aclanthology.org/2026.eacl-long.225/) | Instance-level alignment predicts multilingual NLU errors; English-activation replacement fixes some mistakes | Generic cross-lingual representation rescue already exists; must rule out broad alignment explanation | Abstract verified; full experimental detail pending |
| [Brillant & Pinter, Tokenizing Crosslingual Homographs, 2026](https://arxiv.org/abs/2607.17689) | Language-aware tokenization can modestly improve some MT settings | Language-aware token split is an occupied mitigation idea, not a new causal scientific explanation | Abstract verified |
| [Abuín et al., False Friends or Cognates?, ACL 2026](https://aclanthology.org/2026.acl-long.1818/) | Romance-family cross-lingual ambiguity and benchmark evaluation | Another ambiguous-word benchmark alone is weak novelty | Prior literature audit, abstract-level |
| [Doppelganger-JC, IJCNLP 2025](https://aclanthology.org/2025.ijcnlp-long.96/) | Japanese/Chinese false-friend tasks and homograph shortcut | Copying artifact has precedent | Prior audit, paper overview |
| [SemCog Bench, 2026](https://arxiv.org/abs/2606.13218) | Arabic–Hebrew semantic disambiguation examples and limited contextual rescue | Strong cross-script confirmation resource, not a new mechanism | Abstract + prior audit |
| [Tanwar et al., 2025](https://arxiv.org/abs/2501.09127) | Language and contextual cues in false-friend interpretation | Simple context-strength contrasts are occupied; check exact sentence manipulations before E2 | Prior audit; deep comparison pending |

## Neighboring work that bounds claims

- [de Seyssel et al., Discriminating Form and Meaning in Multilingual Models with Minimal-Pair ABX Tasks, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1210/): form/meaning separability through ABX is not by itself new.
- [Inaba et al., How a Bilingual LM Becomes Bilingual, Findings EMNLP 2025](https://aclanthology.org/2025.findings-emnlp.725/): language representation development across training already studied.
- [Goworek & Dubossarsky, Multilinguality Does not Make Sense, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.1773/): warns about sense-aware multilingual transfer confounds.
- [Conneau et al., Emerging Cross-lingual Structure in Pretrained Language Models, ACL 2020](https://aclanthology.org/2020.acl-main.536/): transfer without shared vocabulary; overlap is not a necessary explanation.
- [Dijkstra & van Heuven, The architecture of the bilingual word recognition system, BIA+, 2002](https://doi.org/10.1017/S1366728902003019): bilingual word identification and task decision are conceptually distinct, nonselective activation; analogy for hypotheses, not evidence that LLMs instantiate human BIA+ stages.
- [Tarin et al., When sentence meaning biases another language, Bilingualism: Language and Cognition 2026](https://doi.org/10.1017/S1366728925000380): eye-tracking shows late cross-language interference and frequency moderators; late contextual homograph interference is **not** a new human discovery.

## Cho as experimental-design references (different substantive domain)

- [Cho et al., Revisiting In-context Learning Inference Circuit in Large Language Models, ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/22d4f952efa13970f0b1ffb22170d416-Abstract-Conference.html): multi-step computation claim; observational measures, selective disabling, bypass caveat.
- [Cho et al., Mechanism of Task-oriented Information Removal in In-context Learning, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/105112d52254f86d5854f3da734a52b4-Abstract-Conference.html): concrete counterexample → constructive filtering → analogous observation in natural ICL → causal necessity test.

## Novelty stress test / necessary further reading

**Occupied:** false friends cause errors; language/resource bias; shared words reduce surprisal; any overlap can aid global transfer; semantic vs language output separation; simple homograph copy can be changed by patching; ordinary contextual disambiguation; language-aware tokenization.

**Candidate, not confirmed gap:** whether a *matched, late contextual semantic correction* changes a model's downstream use of the intended sense, vs merely changes the final answer form; and whether competition, generic ambiguity, language identity or output copying uniquely explains that pattern.

Before E2/E4: deep-read the nearest contemporary revision, garden-path, multilingual WSD, contextual patching, and bilingual interference papers, and run a second novelty search including preprints after 2026-07. This table is a decision aid, not a proof of novelty.
