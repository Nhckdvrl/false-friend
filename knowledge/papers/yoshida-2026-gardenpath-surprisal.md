# Yoshida et al. 2026 — An Existence Proof for Neural LMs Explaining Garden-Path via Surprisal

- **Source**: https://aclanthology.org/2026.acl-long.1694/
- **Reading**: **S1** (PDF key objectives, training design, results/limitations; appendices not all reviewed).
- **Relevance**: methodological model of **reversing an overclaimed impossibility**.

## 1. 背景矛盾

Naturalistic human reading times often correlate with surprisal; however, off-the-shelf neural LMs underpredict the very large slowdown at syntactic disambiguation in garden-path sentences. Some took this as evidence surprisal theory itself cannot explain such effects. But this confuses **a psychological functional hypothesis** with **the predictive competence of a particular approximating LM**.

## 2. Idea 生成逻辑（INFERENCE）

作者重新审视“理论不成立”这一断言的量词：它声称 **没有一种 neural LM surprisal** 能匹配 garden-path RT 吗？如果是，任何 one counterexample 就足够反驳。这导致不需要发明更复杂人脑架构的构造性测试：让 LM 专门学会 GP 的预测分布，再看 held-out human RT 能不能匹配，同时检测是否失去 general LM quality。

**尺度**：不是再次测 GP 的 accuracy，而是**对上一代证据所能支持的理论否定作出逻辑校准**，给出 existence proof。Cho 式成熟科研不一定是组件干预，也可以是找到前人推断中的量词问题。

## 3. 实验逻辑

训练前直接测试: off-the-shelf surprisal underpredict GP; 但不能排除参数化模型的预测不足。
Constructive: fine-tune LM on GP sentences to produce more humanlike surprisal trajectories.
Validation: hold out GP items, test RT prediction and naturalistic RT as well as general LM ability，避免把训练数据记住。
Result: fine-tuned models can account for GP slowdowns in held-out stimuli, and still perform on naturalistic reading data.

## 4. 解释边界

这证明“存在一个 neural LM，其 surprisal 能解释这些 RT”而非“人类 processing 只由 surprisal 决定”。微调可使 proxy 更贴近观察，但不能自动证明心理机制，也不能由它否认人类 reanalysis 等其他理论。

## 5. 本项目最有价值的启示

**先检查结论的逻辑量词/identification**。旧 FF 的共有 token 与 FF categories 不可互换；同样“models don't revise”也可能只是某个 *evaluation task/prompt* 不会展示修正。与其抢新领域，不如用一项构造实验测试一种广泛的因果不可能断言。

## 6. 反证与剩余

若强 claim 为“无论什么格式都不能在后证据理解准确”，一个用干净语义测试展示成功重分析的 existence counterexample 就能反驳。缺口：是否预测现实预训练模型中的失败边界，或只是训练了一个人为代理。
