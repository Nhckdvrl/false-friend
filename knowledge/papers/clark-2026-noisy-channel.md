# Clark, Levy & Gibson 2026 — Targeted Regressions in Noisy-Channel Garden-Path Reading

- **Source**: https://aclanthology.org/2026.conll-main.25/
- **Reading**: **S1** (PDF experiment structure, error locations and discussion; appendices not fully checked).
- **Family**: human incremental reanalysis, plausible error correction, eye/mouse movement.

## 背景与问题

晚到的语法/语义不一致可以使读者推翻早期句子解释，但有不同恢复方式：重新解析语法，或推断**输入本身可能带有噪声错误**。如果读者真正做 noisy-channel 逆推，会有倾向回看哪些位置的预测，而不是均匀地回顾全句。

## Idea 起源（INFERENCE）

从 Levy/Gibson 的 noisy-channel 理论，作者识别此前多数结果使用 RT/最终理解分数而难检查“修正针对哪个局部错误”。于是通过设计各个 plausible corruption locus 的材料，让 **人工回视位置** 成为可观测对象。相对 Christianson 2001 的 lingering wrong interpretation，这项更关注**修正过程的目标选择**，从结果转向过程测量。

## 实验链

1. 构造可暂时合规但后期违反预期的句子；可能由先前 typo/word corruption 解释。
2. 实验比较不同潜在错误位置受试者的回视选择 (mouse-tracking reading/targeted regressions)，控制句子分组。
3. 与 noisy-channel 推断中可能错误位置的概率预测对比，发现选择性回视对照关系。

## 强解释的边界

这是人类阅读和 perceptual regressions，不是 Transformer 语言模型的 attention head 或重新写 token；甚至“回到某位置”并不自动证明修正成功，只证明 processing allocation 的位置性。

## 本项目的设计迁移

**学习可检验的中间行为预测**：不光看最终答案对错，还问如果模型怀疑最初的解释不正确，后续 token 对不同语义来源的使用是否有*可独立定义的方向性*。严格承认 LLM 没有原生 mouse revisitation；不能把 hidden-state similarity 当回视。

## 反证

若与语义错配位置无关，所有差异仅由距离/recency/语法类别支配，则“有针对性的跨语言意义重绑定”没有支持。
