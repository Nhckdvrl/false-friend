# Ravisankar et al. 2026 — Can you map it to English? Joint role of task and language representations

- **Paper**: https://aclanthology.org/2026.eacl-long.225/
- **Reading**: **S1** — PDF method, results §2–4, Fig. 4/control analysis reviewed. No exhaustive Appendix reading.
- **Nearest**: Dumas, Körner, multilingual NLU activation interchange.

## 背景

当多语言模型在低资源语言 MCQA/NLU 答错，但对应英语问题能答对时，差距是知识缺失还是错误的跨语言激活对齐？仅按语言的均值不能区分 instance-specific 失败。

## Idea 来源和创新尺度（INFERENCE）

把 bilingual alignment 的“距离”从全局 representation similarity 落到**某个待回答实例的误差**，再通过英语 donor → target-language recipient activation patching 检查充分性。它推进了 measurement granularity 与干预因果，非凭空创造新问题。

## 实验链与真正严谨之处

1. 对相同 question content 在英语和其他语言观察层间表征；量化中间层 alignment 与能否答对的关系。
2. 挑出 English 能答对而本国语言答错的情形，通过 activation replacement 看能否挽回 MCQA；观察 layer/position sensitivity。
3. **非常值得模仿的控制**：取答案标签相同但题目**语义内容不同**的 source prompt 来 patch。如果 patch 只是传送那个候选标签，这种错误 donor 也可能“修好”，说明不是真正 task-semantic transfer。

## 边界与 rival

英语 donor 的 patch 可能带来更强 general representation、task-format prior、正确答案标签信号或语言信息；并不自动证明“整条意义对齐路径定位成功”。需要同答案但无语义对应的 donor、双向干预、random vector、无关位置与 semantic inference 对照。

## 对本项目的作用

即便我们观察到 FF 的 semantic judgments 随 patch 变好，不能称“发现 multilingual meaning module”。需要比此工作多一层：**同一个 lexeme 的 competing senses** 是否能被有选择地切换，同时**保持 unrelated semantics / output form invariant**？若不可能，简单 patch 不是有效机制证据。

## 未决

补读完整对照实验统计与 patch 的 token alignment 实现；向数据 schema 添加 donor 原文语义、答案标签与 source-target 同/异义标志。
