# Vázquez Abuín, Camacho-Collados & Garcia 2026 — False Friends or Cognates?

- **Paper**: https://aclanthology.org/2026.acl-long.1818/
- **Data**: https://github.com/mrtva/false-friends-vs-cognates
- **Depth**: **S1** (PDF §§2–5, Table 2, repo README and TSV rows checked)
- **Role**: partial-vs-total false-friend naturalistic boundary controls, not a time-ordered revision dataset.

## 1. 背景

与其总假定语言越近迁移越好，近亲语言里越多形近语义异的词，越容易通过错误的 lexeme matching 误导模型。需要一个可以比较 cognates、total FF 和 partial FF 的可解释数据集。

## 2. Idea 来源和尺度（INFERENCE）

前人 WiC 将“两个上下文是相同 sense 吗？”变成可计算标准，FF 研究强调跨语言对应关系。作者把两者结合，跨 GL/PT/ES 建造**跨语言 contextual semantic-equivalence 数据集**，并同时比较 encoder similarity、linear classification、LLM few/zero-shot。这是已有问题的**评价对象重定义和深入边界**，而非模型内部因果证明。

## 3. 核实事实

3 组语言对，每组 auto（来源 Wikipedia 2024 句）和 human-authored 两套，共 **704 word pairs，1,408 sentences**；350+ 等量 cognate/FF（论文 Table 2 为 352+352），两位 linguists 校验，对 total/partial FF 的细分很关键。TSV 列 W1/C1/P1/W2/C2/P2/R/POS，R=1 same sense, R=0 different sense。

方法比较 contextual similarity 阈值、logistic regression 与 LLM multiple-choice（§4）。**并非每个词对 strict same form**（例如 acceso–aceso），也没有“先误导后修正”时间顺序。

## 4. 实验链（INFERENCE）

怀疑 lexical proximity 不保证 semantic proximity → 构建精细化 label 并验证 → 用不同架构/训练策略测试是否在 partial/total sense 更难 → 观察语言距离与 model competence 调节。它使用两类句源以检验结果是否仅是 Wikipedia domain 偏差：这是可迁移到任何 benchmark 的**来源偏差控制**。

## 5. 证据边界

“R=0”说的是**所给两个语境**中意义不同，不是整个人类词典分布无重叠；“partial FF”更不意味着没有任何共享意义。若直接当 exact-form shared/split semantic control，会重演旧项目错误。

## 6. Related-work 距离

Stingray 用语义适切性和 usage correction；这篇聚焦 cross-lingual WiC 的 sense equivalence，提供相似语种的清晰词对与经过审核的自然句。我们的可行额外价值只能是**机制可证伪**，不是增加 R 任务/模型覆盖。

## 7. 自己的区分实验

从原始数据按 exact form、同词性、词频、partial-vs-total 分层提取，检查 R=0 的语义对比是否在不同判断任务一致。**杀死机制主张**：同语普通 WiC 同等困难，并不存在跨语言 lexeme collision 的增量损害。

## 8. 待核查

每个 TSV 的语言方向与 R/POS 的 source provenance；人标 vs auto 评估时层级抽样，不要合并成独立随机行；预先确认允许派生和再发布的数据许可。
