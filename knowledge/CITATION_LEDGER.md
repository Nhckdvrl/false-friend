# Assertion ledger / 论断证据登记（更新 2026-10-11）

| id | 可核验的主张 | 原始来源、具体位置 | 不能外推到 |
|---|---|---|---|
| C01 | 词表 high-/low-sim/full/no-overlap 影响多语 global transfer；高相似共享通常优于低相似 | [Kallini 2025](https://aclanthology.org/2025.findings-emnlp.1153.pdf), §§3–6, Table 1 and Appendix F | 任一具体 false-friend 的 sense 不受损 |
| C02 | Low-similarity overlap 可能制造低语义相似 token 的误导性表征相似 | Kallini 2025 §5, Fig. 2 | 所有 low-sim token 都是自然 false friends |
| C03 | 四种词汇共享设定下，荷英 false friends 的 surprisal 促进强烈关联累计频率 | [Škrjanec 2026](https://aclanthology.org/2026.cmcl-1.10.pdf), §§4–6, Figs. 3–4 | sense selection 正确或者错误 |
| C04 | Stingray 705 entries，其中 259 true cognates, 446 false friends（en-de 196） | [Stingray 2025](https://aclanthology.org/2025.findings-naacl.178.pdf), §3, Table 1 | 自然训练语料中同形词完整语义分布 |
| C05 | 中文日文同形词的词义、语境和翻译三种任务；出现 homograph-copy shortcut | [Doppelganger-JC 2025](https://aclanthology.org/2025.ijcnlp-long.96.pdf), §§3–5, Fig. 2 | 所有错误都来自内部词义混淆 |
| C06 | 早期概念空间随预训练形成；部分 patching 改善实为 polysemy 选义或复制行为改变 | [Körner 2026](https://aclanthology.org/2026.eacl-long.145.pdf), §§3–5.3, Figs. 4–5 and Table 2 | patch success == 语义理解改善 |
| C07 | translation task 的 concept 和 output language 信息可被激活干预相对独立地改变 | [Dumas 2025](https://aclanthology.org/2025.acl-long.1536.pdf), §§3–5 | 任意语言任务中的语义决策独立模块 |
| C08 | English → target language 的实例级 activation patching 提升部分 MCQA，且作者做了同答案标签控制 | [Ravisankar 2026](https://aclanthology.org/2026.eacl-long.225.pdf), §§2–4, Fig. 4 | patch 只传语义而不传答案或任务 |
| C09 | 英德/英法/英西 same-form homograph 的孤立词义、语义判断、高低语义约束已被系统研究 | [Tanwar v2 2026](https://arxiv.org/html/2501.09127v2), §§3–4.3 | 晚证据修正机制已建立 |
| C10 | 704 Romance word pairs / 1,408 paired sentences, human and semi-auto, partial/total FF 与 WiC | [Abuín 2026](https://aclanthology.org/2026.acl-long.1818.pdf), §§3–4 and Table 2；[data](https://github.com/mrtva/false-friends-vs-cognates) | same-form only; incremental revision pairs |
| C11 | 英语 garden-path LM 理解有明显行为错误，任务与人类比较 | [Amouyal 2025](https://aclanthology.org/2025.acl-long.403/), abstract; [Amouyal 2026](https://aclanthology.org/2026.acl-long.1040.pdf), §§2–4, Table 2 | 它们直接证明跨语言语义冲突机制 |
| C12 | Surprisal 难解释 GP 并不意味着 surprisal 理论不可行；微调后可拟合 held-out RT | [Yoshida et al. 2026](https://aclanthology.org/2026.acl-long.1694.pdf), §§3–5 | 语言模型内部的“意识到误解” |
| C13 | BIA+ 区分 word identification 与 task/decision，语言上下文和任务上下文影响不同 | [Dijkstra & van Heuven 2002](https://doi.org/10.1017/S1366728902003012), abstract | LLM 必然遵守人类 BIA+ 结构 |
| C14 | 人类旧解释部分保留、好够理解已是经典路线 | [Christianson et al. 2001](https://doi.org/10.1006/cogp.2001.0752), abstract | LLM 必然存在同样持续机制 |
| C15 | 有错误线索时，人类选择性回看可能错误位置，与 noisy-channel 预测有定性符合 | [Clark et al. 2026](https://aclanthology.org/2026.conll-main.25.pdf), §§2–4 | 语言模型的后续 attention 就等同眼动回视 |
| C16 | Cho 的 constructive filtering、指标观察、干预消融是连续的证据阶梯 | [Cho et al. ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/105112d52254f86d5854f3da734a52b4-Abstract-Conference.html), conference abstract. *完整手稿本轮未可靠打开* | 具体层、公式或作者动机细节 |
| C17 | Cho 2025 的 Encode/Merge/Retrieve-Copy 与 bypass 并存 | [Cho et al. ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/22d4f952efa13970f0b1ffb22170d416-Abstract-Conference.html), conference abstract | 它揭示了一切 ICL 或我们研究的特定机制 |

## 纠错记录

- 旧 [docs/LITERATURE_MATRIX.md](../docs/LITERATURE_MATRIX.md) 某条 BIA+ DOI 写成以 **3019** 结尾；核验 Cambridge 原文应为 **3012**。
- 旧归档中的“true cognate”并不能实现「自然同 form + matched sense distribution」的因果对照。不是 Stingray 原设计的错误，是研究对象错位。
- “semantic confusion” “copying” “surprisal facilitation” 和 “wrong MCQA answer” 是四种不同证据；不能互相引用为同一个 mechanism claim。
- S1 指核心章节与表图核查，不暗示完整逐页精读所有 17–32 页附录；未核查处保留 debt。


| C18 | Formally identical EN/DE source word indices cannot be recovered solely from fixed displayed sentence; German common nouns lowercased create linguistic risk | [Tanwar Task3 source code](https://github.com/EshaanT/Bilingual_processing_LLMs/blob/281a67eac6ddbe5445e1c10277e5833d40d72125/src/data.py), [our pinned-source audit](https://github.com/Nhckdvrl/false-friend/actions/runs/38158254706) | Internal meaning selection errors or invalidity of all original sentences |
| C19 | Context-question-option vs question-option-context causes ~14.7pp gap in 21 decoder LMs; architecture and targeted option-activation tests favor causal-attention explanation | [Ok & Lee Findings ACL 2026](https://aclanthology.org/2026.findings-acl.1921.pdf), Figs 1–6, Tables 1–2 | Tanwar Q1-generated-response self-conditioning is the same mechanism |
| C20 | Mixed list, task type and source-language dominance affect human interlingual homograph latency and errors | [Biloushchenko et al., Bilingualism 2026](https://doi.org/10.1017/S1366728926101916), experiments 1–6 and Tables 2–4 | Equivalent Transformer lexical architecture or identical automatic sense decisions |
