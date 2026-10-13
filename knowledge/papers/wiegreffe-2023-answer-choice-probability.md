# Wiegreffe 等 2023 — Answer-choice probability 与准确率

**题名与元数据（FACT）**：Sarah Wiegreffe, Matthew Finlayson, Oyvind Tafjord, Peter Clark, Ashish Sabharwal. *Increasing Probability Mass on Answer Choices Does Not Always Improve Accuracy*. 正式发表 **EMNLP 2023**, 8392–8417；不是仅有 arXiv 的未审稿文章。[正式条目](https://aclanthology.org/2023.emnlp-main.522/)、[正式 PDF](https://aclanthology.org/2023.emnlp-main.522.pdf)、[arXiv v2 HTML](https://arxiv.org/html/2305.14596v2)、[作者代码](https://github.com/allenai/revisiting_surface_form_competition)。读取日期 2026-10-13。

**范围 S2**：定向读 arXiv v2 §§3–7、Limitations、A.6 Table 8 及部分 Table 9；正式 PDF 核题名/作者/发表信息和 §3–4 定义。Fig. 1/3–6 的图注与正文说明已读，未穷尽附录模型表、未核作者代码、未可靠完成所有图像视觉复查。不同版本未逐字 diff；下列方法定位来自 v2。

## 作者事实（FACT）

§3.2 明确 PMI_DC 是替代评分，不改变模型概率，也不保证等于语义等价类总概率的排序。§4 定义 PMA 为候选原始概率之和，并以余下质量约束 SFC；候选须满足前缀不相交条件。§6–7 比较六模型、三种 QA 数据集、问题/候选格式与示例数量；PMA 增大不保证准确率提高。§7.2.1 分解问题和候选暴露；§7.3 显示 PMI 收益依赖格式和模型。Limitations 承认没有严格可比的 base→instruction 模型对。[原文](https://arxiv.org/html/2305.14596v2)

## Idea Genesis / 最近邻距离（INFERENCE）

前作把提分当作有利于 SFC 的证据。本作最值得学习的一步是：**先为假说指定可观测的限制，再检查消除该限制是否足以让预测变好**。这比再比较一种归一化有更大解释增量。它没有把 SFC 否定为不存在，而是削弱“提分就说明 SFC 得到修复”的单向推断。

可以将实验前的预测写成两条：如果主要是概率泄漏，压低候选外质量应限制它能造成的错误；如果主要是候选内的错误相对偏好，模型完全遵守答案格式也可能持续选错。后者不自动等于知识缺失，还可能是当前提示下的选择、标签绑定或局部推理失败。

## 从界到测量的推导（FACT 定义 + 我们的应用推理）

由原文 Eq. 5–7，令 `p1 ≥ p2` 为该次提示下最高两候选的**原始**概率，`M = Σ p(choice)`，则当

```text
1 - M < p1 - p2
```

候选外的总概率即使全加给第二名，也不能推翻第一名。它是排除某一种排序翻转的充分条件；不满足条件只是仍有可能，不能宣布 SFC 实际造成了错误。PMA 是界所需的量，不是逐例测得的同义词概率。

**本项目应用（INFERENCE）**：对 A/B/C/D 单 token、完整词表 logp，可逐轮计算该界。仅在四标签中 softmax 会人为令 M=1，完全破坏检验。也不能拿四次排列的平均 logp 当作一次真实提示的概率分布。应逐轮报告有效 token、PMA、原始概率差、是否满足界，再汇总同一词的状态。

此外，高 PMA 只说明读出把质量集中到标签；若候选意义不互斥，语义等价类本身就未良好定义。本轮可把这一量称**标签输出空间诊断**；从它外推到日中词义的“全部语义竞争已消失”需要额外假设。

## 不能从论文推出什么（INFERENCE）

改变提示格式同时改变输入和任务适配，因此 PMA–准确率变化不能视为单独操纵 SFC 的干预。模型间 base/instruction 差异也不是严格训练因果比较。PMI 成功可以削弱“原始分数直接代表知识”的读法，却不确证“知识正确、只是输出错”。我们还需要独立生成与语义后果证据，见[本轮综合笔记](../notes/SCORING_AND_SEMANTIC_ACCESS_READING_2026-10-13.md)。
