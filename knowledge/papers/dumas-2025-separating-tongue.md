# Dumas et al. 2025 — Separating Tongue from Thought: Activation Patching Reveals Language-Agnostic Concept Representations in Transformers

- **Official**: https://aclanthology.org/2025.acl-long.1536/
- **Reading**: **S1** — PDF experimental setup, results, figures and discussion inspected; no claim of exhaustive appendices.
- **Nearest later**: Körner et al. 2026; Ravisankar et al. 2026.

## 背景与科学对象（FACT）

“LLM 的知识到底以语言特定还是跨语言共享的方式编码？”不是这篇论文第一次提出的。但以表征相似度或多语言 probing 观察到共享知识，并不足以判定模型能否把**同一概念转成另一种输出语言**，也不足以判定概念和语言是否可被分别操作。

## Idea 来源及与先行工作的最小区别（INFERENCE）

直接沿用 activation patching 的因果逻辑，作者可能注意到：现有语言无关 subspace 的证据多数是 **decodability/correlation**，不是成功操纵的实证。因此设计双因素干预：用不同 source/target prompt，使“表达的概念”与“产出语言”可以不同时改变。思想尺度是从“跨语言共享表征存在”推进到**一个可操纵的概念—输出语言分离**，而不是提出一个全新的抽象语义空间。

## 实验与解释链

(1) 控制 source/target 的输入概念、输出语言差异，观察源激活替换后模型是否能在目标语言回答源概念；
(2) 按 token/layer/position 检查干预窗口，与语言方向等相互验证；
(3) 排除干预直接把完整答案字符串照搬出去这种弱解释，并分析失败类型。

成功的 patch 是一个因果充分性证据：某些受干预表征承载了可以改变输出概念的信息。但不能从这个结果推断“概念无语言影响”“所有语言共享一个唯一表示”“语义理解和词形生成完全独立”。

## 最重要的竞争解释

- Patching 可能传了可复制的答案 token、任务格式、句法或 prompt residue，而不只是 concept。
- 任务相对简单，特定 concept/translation 的 result 不保证跨复杂句法、交叉歧义和新词汇泛化。
- 形式上相同的输出语言，不代表词汇层面的语义选择已被单独识别。

## 本项目应当借鉴/不能重做的事

**已占据**：通过 patching 改变 concept 而保留 output language；“语言”和“语义”可以某种程度分离。

**若走路线 A**：先找出**同一交叉同形词**在“语义推断正确、自由输出错误”与“语义推断也错误”两种条件下的必要区分，并设计**同答案不同语义**的 patch 对照。机制声明应限缩到具体任务/层/语言配对。

**拒绝路线的证据**：一种对全部任务同样有效的粗暴 patch 不能识别任务阶段分离；只取得 patch 后翻译正确率提高不构成大于本文的解释尺度。

## 阅读债务

复核文中不同语言对、模型规模、patch 干预位置的完整 Appendix；与 Körner 精确比较 patching 对 synonym/word copying 的排除实验，避免过度同化。
