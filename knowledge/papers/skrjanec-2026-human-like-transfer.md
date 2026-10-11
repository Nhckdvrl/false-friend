# Škrjanec et al. 2026 — Is Cross-Lingual Transfer in Bilingual Models Human-Like?

- **Link**: https://aclanthology.org/2026.cmcl-1.10/
- **Depth**: **S1** (PDF 图 1、3、4、§§4–6/频次回归检查)
- **Lineage**: human cognate facilitation / interlingual homograph interference → cumulative frequency hypothesis → controlled bilingual LM word-form overlap.
- **Role**: separates token form fluency from semantic fidelity.

## 1. 领域根本问题

人类双语者对 true cognates 往往有 facilitation，对 false friends 常有 interference。双语 LM 共享 embedding 时会复制人类这样的处理模式吗？此前 Winther 等工作把双语 cumulative frequency 作为关键可能机制，但还需在 controlled false friend overlap 上检验。

## 2. Idea 起源与尺度（INFERENCE）

相较 Kallini 面向 NLP global transfer，作者来自 **computational psycholinguistics**，选择与人类阅读实验直接可对齐的 **surprisal** 和荷英实验句子。前进的一小步是：保持从头训练的双语模型，在四种明确 lexical overlap 条件下，将 shared form 的条件预测效应与词频回归联系起来，跨 human/LM measurement 做可对比预测。这是理论模拟的量化实验，不是开创新 lexical sharing 问题。

## 3. 实际实验（FACT）

Full Overlap / Friends Overlap / False Friends Overlap / Minimal Overlap 四种训练制度（Fig. 1）；语料中有 Dutch/English 重叠形式及 matched control stimuli。§5.1 测 contextualized target embedding vs preceding context；许多条件下上下文表示仍分语言。§5.2 预测给定 preceding context 的 target surprisal，并用 item 随机截距的 mixed-effect 回归，之后加入 **两种语言**的词频。

Figure 4：friends 和 false friends 在相应共享词汇条件下都有 surprisal facilitation；加入累计频次，false-friend 类别效应难以独立维持。注意他们**测的是读到 target word 时的条件概率，不是 target 后面文本的词义连续解释**。

## 4. 实验链逆向（INFERENCE）

先设立 human-likeness 的合理期待：friends 帮助而 FF 干扰。直接复刻读词刺激的 surprisal，发现 FF 也容易预测——与人的行为对比产生冲突；但这可能只是两语言词数累积。接着引入词频阶梯回归，并检查语境与 target 嵌入是否分别保持语言区别。由此新理解：**同形词对 decoder 的表面可预测性可以增强，但模型未必处在可读作 human lexical interference 的计算状态**。

## 5. 证据边界

- “surprisal 下降”是 form 预测改善。没有在每个句子中明确检验目标语义 sense 或下游推断。
- 词频与类别混合、少量 false-friend 原型、双语词类/分布差异限制强因果结论。
- 研究没有证明人类神经层级机制与 LM 的 embedding/softmax 同构。

## 6. related-work 距离

Kallini：任务层面 global transfer；这里：词形 surprisal 与频次、人类阅读。Tanwar/Stingray：意义判断；这里没有完整语义判断。这三个维度形成表面悖论，却**并无严格矛盾**，因为因变量不同。

## 7. 推给自己的实验

先在相同目标出现位置做 form surprisal 与同句 sense discrimination + downstream consequence。必须在同一词、同一语境、同一模型上问“form improves but sense fails?”，但**共现也不是因果**。再用受控 parameter-sharing 实验区分频次共享与语义共享。**杀死故事**：所谓 divergence 只是任务指令能力差异、句子生成不自然、低频/长度污染。

## 8. 未决

复核原始 Dutch-English human stimuli 的授权及词汇类型/频次；若仅转写成英语 prompt 会改变测量对象，不可宣称“复现读时干扰”。
