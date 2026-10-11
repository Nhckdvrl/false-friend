# Körner et al. 2026 — When Meanings Meet: Investigating Cross-Lingual Concept Representations

- **Official**: https://aclanthology.org/2026.eacl-long.145/
- **Reading**: **S1** — PDF introduction, model/stage interventions, central results, manually inspected translation categories (§5.3) and Figs. 4–5 / Table 2. Appendix not exhaustively checked.
- **Role**: strongest threat to “sense-vs-output” novelty; read before proposing any activation-patching experiment.

## 研究问题及历史位置

Dumas 已说明翻译时对输出语言和语义进行一定独立操纵的可能；但**这种 language-agnostic 共享概念何时形成，以及不同语言概念怎样随训练变得互通**，没有得到具有 checkpoint 动态的机制解释。跨语言对齐的静态探针也难告诉我们因果生成结果的变化。

## Idea 来源与尺度（INFERENCE）

这篇论文与前一篇的距离非常短：不是“第一次找到 cross-lingual concept space”，而是把 **单点 activation patching 变成沿训练过程的因果发展追踪**。核心设计来自 Dumas 的 concept-transfer 操作 + 可用的 EuroLLM checkpoints。这是**补足机制的时间尺度**（training time）及具体反例类型；不需要发明一个模型。

## 作者实验链（已核验结果 + 逆推）

1. **从静态可操纵到动态发生**：对 EuroLLM 系列的多个训练 checkpoint 做 concept patch，观测跨语言翻译/概念转移在何阶段出现。仅 checkpoint 的存在不能说明机制，故要考查概念交换的下游响应。
2. **形成的究竟是 shared semantic space，还是 prompt/form shortcut？** 文中将 translation output 的不同错误进行人工归类，报告 synonym / hyper-/hyponym / wrong sense / copying 等，并展示被称为“进步”的 patch 事实上可能只是**不再原样复制多语言同形词**。
3. **多义词的挑战**：如法语 *tour*，某些设置无 patch 输出 *tour*，patch 后输出 *tower*。这说明结果变好可能来自 sense/lexicalization 改变，而非“跨语言翻译理解突然发生”。

这组反例的价值不只是结果数值，而是教我们：**若不复核成功案例的错误类型，就会把一个较窄的行为修正描述成宏大的概念语义机制。**

## 本论文没有解决 / 本项目最短增量

该文确有实质 polysemy/homograph 机制案例，但没有像 Good-Enough 风格那样，固定最终正确意义、系统操纵早期误导与晚期反证，并结合**非翻译性下游推断**与普通单语歧义对照来估计不同错误来源的交互。这个差距是候选延伸，不等于绝对无人研究。

## 强制反证

- 如果所谓 concept patch 对“正确 sense 选择”完全没有独立贡献，而只阻断了 copying，路线 A 不应讲“隐藏语义竞争”。
- 如果新实验不额外揭示**什么条件下** patch 的意义效果和输出效果反向变化，也不能宣称比该论文更深刻。

## 资源/后续债务

核对 model/tokenizer checkpoint SHA、patch source-context alignment、不同语言翻译词的词性。未来如果 E4 用 patch，必须重做该论文的 error-category baseline，否则新结果近乎只是在本论文 appendix 中加实例。
