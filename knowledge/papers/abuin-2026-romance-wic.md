# Vázquez Abuín, Camacho-Collados & Garcia 2026 — False Friends or Cognates?

- **Paper**: https://aclanthology.org/2026.acl-long.1818/
- **Data**: https://github.com/mrtva/false-friends-vs-cognates
- **Depth**: **S2** (2026-10-13 定向重读 PDF §§2–6、Tables 4–7/10–12、Appendix E/F；原始六个 TSV 与公开 prompt 已检查；不是全文每表复算)
- **Role**: partial-vs-total false-friend naturalistic boundary controls, not a time-ordered revision dataset.

## 1. 背景

与其总假定语言越近迁移越好，近亲语言里越多形近语义异的词，越容易通过错误的 lexeme matching 误导模型。需要一个可以比较 cognates、total FF 和 partial FF 的可解释数据集。

## 2. Idea 来源和尺度（INFERENCE）

前人 WiC 将“两个上下文是相同 sense 吗？”变成可计算标准，FF 研究强调跨语言对应关系。作者把两者结合，跨 GL/PT/ES 建造**跨语言 contextual semantic-equivalence 数据集**，并同时比较 encoder similarity、linear classification、LLM few/zero-shot。这是已有问题的**评价对象重定义和深入边界**，而非模型内部因果证明。

## 3. 核实事实

3 组语言对，每组 auto（来源 Wikipedia 2024 句）和 human-authored 两套，共 **704 word pairs，1,408 sentences**；352+352 等量 cognate/FF，两位 linguists 校验。TSV 列 W1/C1/P1/W2/C2/P2/R/POS，R=1 same sense, R=0 different sense。论文有 total/partial FF 分析，当前公开 TSV **没有该细分类字段**。

方法比较 contextual similarity 阈值、logistic regression 与 LLM multiple-choice（§4）。**并非每个词对 strict same form**（例如 acceso–aceso），也没有“先误导后修正”时间顺序。

## 4. 实验链（INFERENCE）

怀疑 lexical proximity 不保证 semantic proximity → 构建精细化 label 并验证 → 用不同架构/训练策略测试是否在 partial/total sense 更难 → 观察语言距离与 model competence 调节。它使用两类句源以检验结果是否仅是 Wikipedia domain 偏差：这是可迁移到任何 benchmark 的**来源偏差控制**。

## 5. 证据边界

“R=0”说的是**所给两个语境**中意义不同，不是整个人类词典分布无重叠；“partial FF”更不意味着没有任何共享意义。若直接当 exact-form shared/split semantic control，会重演旧项目错误。

## 6. Related-work 距离

Stingray 用语义适切性和 usage correction；这篇聚焦 cross-lingual WiC 的 sense equivalence，提供相似语种词对与经过审核的句子。我们的最小非平凡增量可以是检验其错误解释：区分独立词义访问失败和联合比较诱导的意义变化，并预测何时出现。仅增加 R 任务/模型覆盖不足；也不应把贡献限定成必须完成内部机制定位。

## 7. 自己的区分实验

当前采用[第四轮设计](../notes/ROMANCE_ORTHOGONAL_DESIGN_2026-10-13.md)。共享普通单语机制可以是一种解释，不能自动当作失败；只有声称存在跨语特异性时才必须证明相对于普通歧义的增量。

## 8. 待核查

已核查源 revision a87b73e387a6ef86d0cef7ffe703150905e75d7a：auto-es-pt 的 W1=PT，而 human-es-pt 的 W1=ES。其余 W1=GL。704 行 R 平衡。README/Appendix A 的 auto-es-pt 子类计数相加为305但总行为304，不能自行修复作者的细分类标注。未发现 LICENSE，原文留本地 ignored 数据目录，归档保留哈希/行号。

## 9. 本轮逐实验判断

**作者事实**：LLM 判二元关系并生成解释；主表为 two-shot。公开 Appendix F 展示 GL–PT 一正一负两例，不能假定是其他语言对的原例。零/少样本平均差较小。

**解释边界**：平均增益小不能证明模型主要靠已有知识；示例可能影响类别先验、任务理解或词义粒度且相互抵消。§6 根据解释将部分错误归为跨语言干扰；联合提示中的错误释义不能区分原来不懂和受比较对象诱导。解释也是输出，不是内部计算轨迹。

**INFERENCE / 可迁移设计**：把一个联合比较拆成两次独立释义，再在固定目标上加入配对侧或无关旁例。相比只比较 WiC/WSD 分数，它直接操纵另一实例是否出现。若独立释义仍错，应保留知识/语言识别不足解释；若独立正确而配对后定向改义，才有进一步研究输入干扰的线索。顺序不变性用于寻找待解释对象，不自动等同语义碰撞。
