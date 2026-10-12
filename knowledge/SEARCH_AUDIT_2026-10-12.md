# 文献入口与录用状态核查：2026-10-12

## 本轮检索顺序

1. 多语言 LLM 综述：Yuemei Xu et al. arXiv2404.00929v3，Yuzhuang Xu et al. arXiv2405.10936v2，用于语料/对齐/推理/评测地图，不当作最新模型事实。
2. 原有直接近邻与公开数据：词形共享、词义语境任务、概念/语言干预、表示发展、心理语言学原理论。
3. 最新 NeurIPS2026 官方目录与原文；随后 ACL/EMNLP/AAAI 的强关联工作，以及跨领域测量/干预方法。
4. 对未能取得正文的条目，只登记入口和不知道的内容，不扩写成机制总结。

## 2026 NeurIPS 核验

官方来源：[Downloads2026](https://neurips.cc/Downloads/2026)，不是仅依赖论文标题上的自称录用。目录包含论文与会议活动，不能把所有目录条目默认归为主会或oral。

| 条目 | 本轮实际证据 | 可使用范围 |
|---|---|---|
| Capturing In-Context Learning Dynamics with Task Operators | 官方目录条目；[作者原文](https://arxiv.org/pdf/2610.01054)方法、结果、图表与局限已读；[作者发表列表](https://www.cs.virginia.edu/~az9eg/website/publications.html)列NeurIPS2026 | 机制与方法比较；不标oral/获奖 |
| The Fractured Interlingua: Geometric Bottlenecks in Cross-Lingual Knowledge Editing | 官方目录标题可查，本轮未可靠取得正文 | 仅邻域线索，不引用实验结论 |
| FACBench: A Benchmark for Formal-Anchor Collisions in Multilingual Mathematical Grounding | 官方目录标题可查，本轮未可靠取得正文 | 仅潜在近邻，不假定任务/数据/结果 |

这不是“已精读全部NeurIPS2026”。本项目不为了凑20–30个oral名称而引入不相关CVPR/具身任务；优先那些能改变本问题设计的论文。以会场/强组筛选提高输入质量，但用正文证据评估结论。

## 可核验的优秀范例标签

[de Seyssel等 EMNLP2025 ABX](https://aclanthology.org/2025.emnlp-main.1210/)官方 Anthology 标注 **SAC Highlight Award**。可以据此标优秀案例，不能把SAC Highlight写成Best Paper。

[NeurIPS2026评审指南](https://neurips.cc/Conferences/2026/ReviewerGuidelines)承认原创性的更深理解和具有实质意义的负结果；修复方案不是所有负结果工作的必要条件。我们的应用：不是任何失败都可成论文，而是有效设计改变了一个重要、此前不清楚的判断。

## 检索词与遗漏风险

使用 multilingual LLM survey、cross-lingual word meaning/false friends、semantic availability versus use、language-specific output、bilingual representation ABX/SAE、activation patching controls、multiple-choice calibration、ICL task operator 等组合。近期会议目录与论文版本会变化；后续论文写作前需重新核查正式状态和新近邻。

本轮以原始论文为技术证据，不把二手社交讨论当结果。原文访问受限的外围条目保留 catalog 状态，明确不构成主张支持；不通过降低标准或伪造精读来“清零阅读债务”。
