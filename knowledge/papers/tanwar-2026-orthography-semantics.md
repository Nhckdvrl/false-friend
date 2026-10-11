# Tanwar, Oke & Chakraborty — Multilingual LLMs Struggle to Link Orthography and Semantics in Bilingual Word Processing

- **Link**: https://arxiv.org/abs/2501.09127
- **Version**: arXiv v2 2026-03-18 (not original v1 2025)
- **Depth**: **S1** (HTML full main sections + PDF §§1–4.3 checked; not appendices)
- **Code**: https://github.com/EshaanT/Bilingual_processing_LLMs
- **Role**: **most direct novelty threat to “contextual competition” route A**.

## 1. 问题

能否把从人类双语 lexicon 得来的 form/meaning 同时激活理论迁移到多语言 LLM？人类实验强调 cognate ease 与 interlingual homograph confusion，LLM 是否同样？与 Stingray 不同，本文对 **词义孤立识别、词义判断、不同语义约束语境**给出连续诊断。

## 2. Idea 来源与尺度（INFERENCE）

作者显式以 BIA+/lexical decision、语境约束的人类双语实验为知识母体。其合理生成路径：先问 LLM 是否存储各语言 lexical meaning → 再问相同词形如何导致识别干扰 → 再问句子级 high/low semantic constraint 是否救得回来。比单独出一个 false-friend 列表多了**“能力 vs 提取 vs 语境”多测量方案**，但还不是对网络内部机制的因果定位。

## 3. 实验事实

英语与西班牙语/法语/德语的 cognates、non-cognates、interlingual homographs。§4.1 lexical identification/disambiguation，§4.2 semantic judgment，§4.3 设计 low/high semantic-constraint sentence（并讨论 code mixed / incongruent condition），测语言识别与语境理解。作者结果指向模型经常按字形而非正确 sense 判断，并且孤立识别与语义表现未必一致。

**重要前例**：我们旧 E1“先看知道词义吗，再加语境”以及 E2“high vs low contextual constraints”都已经被本文大规模涉及，不能当作核心原创实验。

## 4. 作者实验链逆向（INFERENCE）

开始可能来自经典语言认知中**孤立 word decision vs sentence context**的分歧。先在语言和词汇类别上建立错误分布 → 将语义知识判断与形式区分任务分开 → 高/低语义约束来检验能否单靠上下文救回。他们没有把所有错误都归入同一个 cause，而比较不同操作条件。这启发我们在每步**预注册相反预测**而非复刻结构。

## 5. 解释边界

- 并未自动证明模型没有存某 sense；任务失败可能出自 prompt、语言生成、词频与 verbalizer。
- 语义约束是整个句子/局部上下文强度，不是固定最终语义后严格操纵提示到达时刻的 causal revision 设计。
- “上下文有影响”的重复观测无法带来机制突破。

## 6. 与直接邻居距离

Stingray：多语类别化与语言 bias；Tanwar：词义、语义判断、context strength，直接覆盖我们的基础行为问题。Doppelganger：同形词的 word/context/translation，又覆盖输出形式的误读；Körner：patch 已能改变 sense/copied form。这迫使新路线 A 要走到**双重因果分离或 out-of-sample prediction**。

## 7. 真正可形成新认识的测试

如果 E0 发现在强语境下仍留 cross-lingual-specific error，先用**源语言不一样而最终语义相同、同语言多义词匹配、词频固定**的系统对照验证。必要时用 delayed downstream implication questions 验证是不是只受 prompt / output copying 影响。

**判死条件**：跨语言 interaction 与同语言普通 ambiguity / token frequency 能完全解释，或在二种语义任务之间不可重复。不允许为追逐“修正失败”加无意义的 neuron probe。

## 8. 待做

拿作者数据做 schema/annotation 审查，与 Stingray 和 Doppelganger 去重（防止假独立复现）；详查 high/low 构造是否充分匹配语法、长度与语言优先级。v2 与 v1 的实验和结论差异待核对。


## Deep source-audit correction (2026-10-12)

A close read of the actual Tanwar Task3 code reveals a more subtle problem than a high/low context effect. The authors report approximately **70% vs 34%** context-based "correction" for non-English homographs in English vs English homographs in non-English host sentences. But in the `cross` condition, source language is assigned by a hidden **row index** while the host sentence is from the opposite language. When EN/L2 word strings are case-sensitive identical, ordinary and cross word **sentence surfaces are exactly the same** for that host. The complete prompts differ (explicit "code-mix" instruction), so any inference about true source may reflect **prompt pragmatics**, not word-form recognition.

Furthermore the original generation always asks **Q1 source language → Q2 meaning → Q3 sentence coherence** in a single 512-token autoregressive response. Q2 sees Q1's generated text, introducing a possible self-conditioning pathway. Four "correction" categories are annotated from this **joint verbal response**, not from separately randomized and independently elicited latent senses or temporally observed revisions.

This is not proof the paper is wrong. It is the cheapest high-information **identification test**: reproduce the original prompts, then compare isolated meaning, original Q1-first, Q2-first and externally fixed language answers on **identical items**, with controls and non-copy semantic judgments. See [source audit protocol](../notes/TANWAR_IDENTIFIABILITY_AUDIT.md). If asymmetry vanishes, do not invent a special semantic gate. New model trials have NOT run.
