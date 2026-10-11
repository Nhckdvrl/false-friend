# Cahyawijaya et al. 2025 — Thank You, Stingray (StingrayBench)

- **Link**: https://aclanthology.org/2025.findings-naacl.178/
- **Data**: https://huggingface.co/datasets/StingrayBench/StingrayBench
- **Depth**: **S1** (PDF §§3–4, Table 1, Fig. 3 / tasks and data semantics checked; not every appendix)
- **Role**: natural-word stress-test inventory and clear example of label/estimand mismatch.

## 1. 问题从哪来

大型多语言模型在高资源语种基准可能很强，但跨语言同形词从形式上看似可转移，却隐含目标语言特定的意义陷阱。之前的大 benchmark 很难把这种局部 lexical sense 错误单独取出。

## 2. 创新尺度与 idea 来源（INFERENCE）

作者合理的切入：将 bilingual false-friend 这个**经典心理语言学可解释刺激**变成跨多个语言对的语义诊断题，并量化语言偏向。相对于 general multilingual benchmark，这不是全新模型机制，而是**精细化、可被实例解释的诊断数据设计**。名称 “Stingray” 来源与 local lexical ambiguity 引起的具体 failure 的类比需要从引言追溯，不应臆造。

## 3. 实际数据和任务（FACT）

Table 1：EN–DE 98 true +98 FF；ID–MS 52+134；ID–TL 58+100；ZH–JA 51+114；总 259+446=705。天然 false friend 和 true cognate 标签；§3.2 两种核心任务：semantic appropriateness（哪句话语义合适，允许 “both”）和 usage correction（目标词在句内是否使用正确）。特定的 **错误句子由目标词替换正确表达而制造**；并非全部是纯自然语料的 faithful contextual sense use。

Fig. 3 使用两维语言能力成绩构成 angular language bias 和 magnitudinal comprehension 的诊断空间——有助于区分模型“偏哪一门语言”与“总体能否理解”，但它不是因果机制测量。

## 4. 实验链逆向（INFERENCE）

首先问题是“多语模型单语分数是否掩盖某一语言的 local lexical confusion？”→ 收集不同语对和 matched sense/incorrect usage → 用双任务拆分“选对意义”与“识别错误用法” → 用语言二维 bias 图避免平均数掩盖方向性。作者关心的是诊断、资源语言偏差，而非 token embedding 在训练中的来源。

## 5. 关键边界及旧项目失败

- **true cognate label** 指两个语言在某指定 context 具有共享 sense，不意味着自然文本的完整 P(sense|form,L) 接近。
- EN–DE 例 arm / Arm 在 benchmark 层是可用 cognate pair，大小写规范化成 exact form 会把对象改成德语形容词“穷”。
- 词形可能是不同 tokenizer units，不能把 benchmark 类别变成“同一参数行”的训练干预。
- 带选择题的正确率可能混有语言偏好、翻译熟练度、答案词比较问题。

## 6. 最近邻

Doppelganger-JC 会把意义/上下文/翻译分成三任务；Tanwar 还研究语义约束。这些已经覆盖“LLM 不会 false friends”的主张。我们可复用 Stingray E0 发现/与旧实验核对，但不能发表“新的词义 benchmark”。

## 7. 下一步与反证

从 FF 清单中审查有足够清晰同语言使用和两种任务的词；记录 natural/corrupted 标志，再进行任务层面的两两对照。若 false-friend 的劣势在 **同语言频次、普通歧义和多任务能力控制后**消失，则不再讨论特有语义竞争。

## 8. 待核查

对每个语对的目录/JSON 字段做自动+抽样人工数据审计；确认使用许可，不使用其 common list 作为训练 matching gold；原库中特殊词义混并错误保留在 [docs/LEGACY_RECORD.md](../../docs/LEGACY_RECORD.md)。
