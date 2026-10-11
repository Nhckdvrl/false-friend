# Kallini et al. 2025 — False Friends Are Not Foes

- **Link**: https://aclanthology.org/2025.findings-emnlp.1153/
- **Depth**: **S1** (核对 PDF §§2–7、Table 1、Fig. 2、Appendix F 词表规模表；不等于读完附录)
- **Lineage**: vocabulary overlap controversy → controlled bilingual LM experiments → semantic similarity of shared tokens.
- **Role**: route B's nearest strong baseline; old training proposal originated here.

## 1. 研究共同体的问题（FACT）

跨语言模型是否应该共享词表？旧文献对“共享锚点促进 transfer”与“同 form 不同义造成 interference”有混合结论；不同 tokenizer 的压缩率、频次、语言远近很难比较。本文避免直接给“词典式 false friend 错误率”下定义，而是改变 overlap 集合，在多个语言对训练受控模型。

## 2. Idea 起源与创新尺度（INFERENCE）

从 previous vocabulary-overlap analysis 的争论出发，作者很可能意识到 **overlap 的质量比 overlap 的数量更有解释力**；于是把“是否共享”分解为 shared tokens 的 contextual semantic similarity 高/低。相对 Conneau 类“即使不共享词表也能 transfer”工作，它不是证明 overlap 必要，而是问在同类模型里共享何种 token 更有益。相对传统 FF 词表，它的单位是 subword token，不要求 natural sense inventory 对齐。创新属于**受控训练 + 表征和 downstream 的相互验证**，不属于新的词义判断 benchmark。

## 3. 实际实验（FACT）

将英语分别与 ES/DE/TR/ZH/AR/SW 配对，CCMatrix 的双语训练样本，统一基于 XLM-R tokenizer 重映射。四种设置：Full, High-similarity, Low-similarity, No Overlap；中间层 contextual similarity 分析 + English fine-tune → L2 XNLI/XQuAD。Table 1：No Overlap 在多数 L2 transfer 显著更弱，High 和 Full 通常最佳；低相似度共享仍常比完全无 overlap 好。Fig. 2 发现某些 distant pair 的 low-sim shared token 变得“看似语义接近”。

**重要非同构**：High-/Low-similarity 的有效词表规模相同，但 Full/No Overlap 的大小和总模型参数不同（Appendix F）。因此 **Full vs No** 不是全参数等量的完美单因素干预；语义类别的处理也不等于 FF 独立测量。

## 4. 实验链的逆向推演（INFERENCE）

旧相关工作问“overlap 有没有用”；第一层实验控制训练语料和 remapping，观察全局迁移 → 但提升能否来自 **语义锚点而非词形频率**？所以按 contextual meaning 拆 High/Low → 发现低相似 token 有时导致反向表示相似 → 可是表示错位是否破坏真正任务？于是测 downstream L2 tasks → 得到**全局迁移与部分错误几何可并存**的张力。然而由于高低 token 的覆盖分布及整体参数差异，这一结果仍不能精确定位局部损害或 global benefit 的机制。

## 5. 证据边界与可复现资产

- “any overlap helps”是这些受控语言对、架构和测试的总体经验结论，不是数学定理。
- 不等于“false-friend 语义理解未受损”，因为 XNLI/XQuAD 总分可以掩盖少量词上的坏处。
- 表征相似度不能直接证明某 token 的 wrong sense 被用作决策。
- **旧 false-friend 项目的反面教材**：直接把 low-sim 类当 natural conflict 与 true friend control，构造了不匹配的 causal object。

## 6. 最近邻距离与可发展问题（INFERENCE）

相对本论文真正新增一步的候选不是再测“词表共享好不好”，而是问：全局 transfer 的收益是否仍在 **固定词表大小、参数数量、单词累计频率、tokenizer segmentation、语义关系和语料难度**后出现？若出现，是否可以用 **跨语言连接结构（anchors 拓扑/coverage）**预测，而不是单个 token 的语义相似度？

## 7. 区分性实验与反证

训练小型人工平行语义世界，分别操纵：正确锚点、随机错误锚点、共享但无跨语言语义信息的锚点。严格等参等数据并对齐 output softmax。预测：语义桥解释需要正确语义锚点优于等频的随机锚点；单纯共享参数解释则不那么依赖语义匹配。**杀死 B**：一旦匹配有效容量与频率，低相似重叠比无共享再无收益，且没有能够跨配置预测的机制性量。

## 8. 未决

复核官方代码中 remapping、embedding tie/untie、active vocabulary 和每种 setting 的 softmax policy；核实 low/high 频次完全覆盖匹配是否可能，不能从论文里的“controls for frequency”推断完全识别。
