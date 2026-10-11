# 观测 → 构造 → 因果 → 预测：不混淆科学证据的类型

| 层次 | 常用操作 | 最多能说什么 | 危险误读 |
|---|---|---|---|
| form | surprisal / token logp | 这个字串在前缀里较易预测 | “模型理解了它” |
| behavior | fixed-answer MCQA logp / free translation | 此任务和候选集合下答案偏好 | “可以读到 P(latent_sense|context)” |
| representation | ABX、probe、geometry | 某些信息在表示中可被某种方法解码 | “这些信息用于生成答案” |
| constructive | filter/split embedding/context replacement | 某个机制**可以实现**此功能 | “未干预模型事实上在使用此机制” |
| causal | 选择性 patch/ablation + reciprocal controls | 改变某些状态影响了输出 | “找到唯一干净模块或明确神经方向” |
| predictive | frozen theory → unseen lexical items & tasks | 有一定独立推广与条件边界 | “没有遗漏的机制或永远普适” |

## Cho 为什么有力量？

Cho ICLR 2026（完整手稿本轮访问受限）的大致证据逻辑为：选择 label-absence 中已有解释困难的现象 → 人工低秩过滤说明信息去除可以支持任务 → 测 few-shot hidden states 是否出现类比的去除 → 进一步消融相关计算检验是否有必要。每一步回答前一步没有回答的事。

但是其论文写法不能原样复制到别的领域。尤其不能先选“在神经元里找某种信息”再反推研究问题；我们应从 **存在 competing behavioral predictions 的关键反例** 开始。

## 设计量化操作时的五个独立性检查

1. 明确观测单位：lexeme/type、context family、model seed，而不是把所有模板重复看成独立。
2. 真实条件不变：词形是否 exact match、POS、语言方向、原语境语义、答案语言、词频、长度；若不能全匹配，设计 factorial 或认定不可识别。
3. **候选分母**：相同给定前缀下概率必须来自相同标准 softmax；禁止旧项目那种按 gold label 变 active vocabulary。
4. patch 的任务标签/答案 token 污染：必须用相同答案但**不同语义**的源例子作控制（Ravisankar 2026 已提供良好先例）。
5. Prefix versus final context：标准因果 Transformer 中后续 token 不会改写旧位置 state；在后文位置出现的解释更新，要与语言身份/recency/词序效应分开。

## 最强的实验不是复杂，而是负结果的明确含义

给每个 Figure 写一句：如果结果是 X，哪个解释被否决？如果结果是 Y，下一步为什么必须做？没有这种答案的实验就是附加 plot，应该删除。
