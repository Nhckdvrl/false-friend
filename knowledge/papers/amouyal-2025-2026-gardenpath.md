# Amouyal et al. 2025/2026 — LLM garden-path comprehension and comparative difficulty

- **2025**: https://aclanthology.org/2025.acl-long.403/
- **2026**: https://aclanthology.org/2026.acl-long.1040/
- **Reading**: 2025 **S2** (paper abstract/HTML main findings and related discussion; full PDF not fully inspected); 2026 **S1** (PDF key tasks, hypotheses, Tables and discussion; appendices not exhaustive).
- **Family**: incrementality / reanalysis / task dependence; threat to route A.

## 从人类的自然问题开始

Garden-path 句子开始支持一个局部可接受的错误句法解释，后续语段否定该解释。*Why are garden-path effects hard?* 在人类研究里不是新问题，旧模型早已有 syntactic reanalysis, good-enough and noisy-channel theories。AI 成长后，一个有价值的问题是：**在同一设计下，哪些结构同样困扰人和 LLM，哪些结果是不同测量任务带来的？**

## Idea 来源和与 related-work 距离（INFERENCE）

2025 的作者并非寻找“LLM 第一次在 garden path 出错”，而是借助心理语言学构造**两个可解释的比较变量**：句法复杂性以及 human/LLM 之间的 error-pattern correlation。通过 comprehension questions 与 paraphrasing/text-to-image 任务避免单一问答评分偏差。2026 扩展到更多结构/规模和复杂度条件，研究系统比较条件边界。相对纯 surprisal 理论，这是跨**理解正确性**的直接检验。

## 实验链的认知作用

- 简单问题“LM 会错吗？”无法解释，所以在多个结构上测出错分布。
- 但回答选项会污染 comprehension accuracy，所以增加 paraphrasing / text-to-image 复核（2025 摘要/结果报告）。
- 同类错误是否来自结构/条件的 complexity？2026 的多结构材料让泛化可检查。
- 即便行为像人类，也不证明 LLM 的训练或内部 reanalysis computation 等价人类。

## 对当前 A 路线的直接否定性挑战

只要论文故事是“先入为主，后证据导致难理解”，这两篇已经提供很强的最近邻。提出跨语言 FF 的价值必须能区分 **语言形式碰撞专有机制** 与 **一般 GP/词义歧义**，且维持相同最终语义、任务负担、提示长度。否则只是新材料在老现象上重复。

## 真正需要的对照

构造四象限：有/无 cross-lingual collision × 有/无 prior-misleading history；加 ordinary within-language polysemy/garden path。测非词形复制的下游语义推断。在 effect 存在之后才有理由做表示/干预。

## 实验杀线

cross-lingual × history 交互置信区间围绕零，或所有错误都能由普通难度/句子位置解释；则不要叙述 cross-lingual revision mechanism。

## 阅读债务

2025 full PDF 需后补；2026 对人类研究的 construction/annotation bias 和不同语言的 validity 不适宜直接借用。
