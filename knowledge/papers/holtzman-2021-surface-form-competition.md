# Holtzman 等 2021 — Surface Form Competition

**题名与来源（FACT）**：Ari Holtzman, Peter West, Vered Shwartz, Yejin Choi, Luke Zettlemoyer. *Surface Form Competition: Why the Highest Probability Answer Isn’t Always Right*. EMNLP 2021, 7038–7051。[正式条目](https://aclanthology.org/2021.emnlp-main.564/)、[原 PDF](https://aclanthology.org/2021.emnlp-main.564.pdf)。读取日期 2026-10-13。

**范围 S2**：定向读 §2–7，重点 §3 评分定义、§4 实验、§5 COPA Flipped、§6 反例；阅读 Table 1–5 的可提取文本与 Fig. 2–3 图注/相应正文。未审计作者代码，未复算数值，未穷尽附录模板；截图工具未可靠返回所有图像，故不声称完整视觉核验或全部精读。

## 作者事实（FACT）

§3 比较四种候选评分：LM 为条件字符串概率；AVG 为候选 token 平均 logp；UNC 只以任务域短前缀预测候选；PMI_DC 用条件概率除以域先验。§4 在 GPT-2/3、多种任务和提示下比较，PMI_DC 并非处处最优。§5 交换 COPA 的因果两端并改连接词，让不同候选成为前缀、同一个问题成为被评分续文；这时 LM/AVG/PMI_DC 排序相同。§6 讨论 HellaSwag、ARC Easy、BoolQ 例外，以及长度归一化可能部分抵消先验的猜想。以上定位见[原文 §§3–6](https://aclanthology.org/2021.emnlp-main.564.pdf)。

## Idea Genesis（INFERENCE，不重建作者心理）

可恢复的研究推理是：生成一个具体字符串与在给定概念中做选择，目标函数并不一致。若模型为同一概念保留多种表达，稀有但正确的表达会被评分惩罚。因此先提出能在冻结模型上检验的读出变更，再寻找一个改变“哪段是被评分对象”的实验，避免只凭平均提分讲机制。

最近邻距离不在发明 PMI；相对既有的长度归一化、任务校准，它把**同义表达的概率分配**变成解释对象，并尝试以 scoring-by-premise 支撑解释。对我们，重复“校准后更准”仍是现成方法迁移，不能独立成为机制贡献。

## 实验之前还有什么解释？（INFERENCE）

| 操作 | 若候选先验/表面形式是关键，预期什么 | 未被排除的解释 |
|---|---|---|
| LM → AVG | 长短候选带来的部分偏好改变 | token 数也关联内容信息量；平均值并非意义概率 |
| LM → PMI_DC | 问题给正确候选带来的相对提升更有用 | 这也改变了类别先验/关联度，收益不专属于同义词分流 |
| 去问题，仅 UNC | 若仍可选对，标签与候选先验可支持成绩 | null 模板可能失配；UNC 差不证明完整输入做了所需推理 |
| COPA → Flipped | 评分续文相同，续文长度和其域先验不再导致候选间差异 | 连接词、自然度和条件方向也改变；不能看成只切除了一个内部机制 |

关键逻辑：Flipped 中三种方法一致，首先是**同一续文**带来的代数事实。它保证这些评分变换不再区分候选；只有结合真实准确率/逐例变化，才产生行为证据。方法一致本身不识别原模型为何错。贝叶斯反向条件式等价也要求同一个联合分布；将文本改写后反向输入因果 LM，不自动满足此条件。

## 对本项目的可执行影响（INFERENCE / 新实验建议）

当前整段 PPL 包含题干；本论文 AVG 针对候选续文。两者不可直接同名。本轮应并列保存整段、candidate sum、candidate mean、null candidate 分数，再看逐词排序与自由语义输出是否一致。把 null subtraction 命名为某种具体的 PMI 变体之前，必须记录域前缀、求和单位、token 边界，避免把 mean-NLL 差冒充原定义。

不能据这篇文章宣布：低分必然是“会但读不出”，或者 PMI_DC 已消除所有表面形式竞争。后续方法边界见 [Wiegreffe 等 2023](wiegreffe-2023-answer-choice-probability.md)，本轮证据需求见[综合阅读笔记](../notes/SCORING_AND_SEMANTIC_ACCESS_READING_2026-10-13.md)。
