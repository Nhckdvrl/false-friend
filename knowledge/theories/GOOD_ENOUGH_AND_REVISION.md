# Good-Enough、lingering misinterpretation 与 noisy-channel：别再发现一次同样的现象

阅读状态：Christianson 2001 与 2009 主要依据出版摘要（S3）；Paape & Vasishth 2026 依据公开摘要（S3）；Clark et al. 2026 [CoNLL PDF](https://aclanthology.org/2026.conll-main.25.pdf) 方法、结果与讨论被本轮核查（S1，非全部附录）。

## 科学问题从哪儿来？

经典增量理解默认“在晚证据到达后推翻初始错误解释”。Christianson 等 2001 用问题验证提出更不整齐的图景：局部错误主题角色分配可能残留在最终解释中。[论文](https://doi.org/10.1006/cogp.2001.0752)。之后对任务本身引起的答案偏差有争议，2009 年另用 paraphrasing 复核 lingering effects：[研究](https://pubmed.ncbi.nlm.nih.gov/19210099/)。

**创新尺度**：不是“人有错误”，而是打破“成功重分析 vs 完全失败”的二分，用多种互补测量说明部分修正。这里真正值得学的是 **下游问题分别针对正确和错误解释**，不是借用 garden-path 这个名字。

Clark et al. 2026 在 noisy-channel garden-path 中操作前文可能的错误位置和后文违背预期的词，使用 mouse-tracking for reading 分析回视目标，并拿受控的后验错误概率解释为什么读者回到有可能错的地方（§§2–4）。[PDF](https://aclanthology.org/2026.conll-main.25.pdf)。

Paape & Vasishth 2026 则把是否走上 garden path 与条件性 reanalysis cost 区分，用 latent-process modeling 检验语境和重分析结构：[论文](https://doi.org/10.1016/j.jml.2026.104748)。

## 研究启示

- 最终回答对不代表内部已经彻底改写，也不代表存在“同一错误意义仍被激活”。
- 如果怀疑旧解释残留，要求**两类不同目标的后续语义推断**：一种反对旧错误，一种确认新解释，并确保不只是复制词汇。
- 人类实验的反应时、回视、问答/释义可以证实不同部分；LLM 没有自然的读者回视，因此不能直接把 attention map 解释成眼动。
- 需要普通一语言 ambiguity/garden-path 作机制对照，才能指称 cross-lingual specificity。

## 对旧路线 A 的威胁

“先误导后纠正仍留错误”已经是成熟认知理论；2025–2026 的 LLM garden-path 工作也已在问类似问题。如果没有 **跨语言同形碰撞对一般语言歧义无法解释的独特附加作用**，路线 A 应停止，而不是追加更多 prompt。

## 需要重新读

深入读 Christianson 2001 全文及 2009 paraphrase 方法；CoNLL 2026 与 2024 对“选择性重新分析”持不同证据时，应区分**材料、阅读范式、估计目标**，不能伪造逻辑冲突。
