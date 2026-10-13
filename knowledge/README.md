# 当前工作空间的研究知识库

**位置固定：Nhckdvrl/false-friend/knowledge/**。更新2026-10-13。

## 读什么、为什么

先读 [领域画像](FIELD_GUIDE.md) 和 [实验设计的来源与尺度](EXPERIMENT_DESIGN_LESSONS.md)，再按 [分类论文索引](PAPERS_INDEX.md) 找到与下一实验最近的两三篇。机器可检索原始登记为 [sources.tsv](sources.tsv)，历史40条索引的不可静默漏收快照在 `history/INDEX_BASELINE_2026-10-12.txt`。

精读笔记在 `papers/`、理论在 `theories/`；每份区分作者事实和我们的来源推演 INFERENCE、具体基线/对照、尚成立的竞争解释、相邻研究与最小非平凡增量。仅检索/摘要了解的资料也全部登记在 [有边界的来源卡](catalogue/SOURCE_CARDS.md)，**不是伪装成已精读论文**。

[最新会议检索审计](SEARCH_AUDIT_2026-10-12.md)区分NeurIPS目录确认、真正读到原文、仅题名候选和奖项。ABX的SAC Highlight可核验；其他未证实的oral/best paper不标注。

## 状态的真实含义

- S1：主方法/结果与相应关键图表有阅读记录，不等于所有附录重算或实验复现。
- S2：定向正文/综述/方法教程阅读，明确使用范围。
- S3：只到摘要、元数据、公开资源或历史导航，不能支持细致机制断言。
- S0：仅题名/目录候选，不知道的内容不猜。

登记 `origin=current` 是本轮新读/补读，`inherited` 是前轮已存在资产，本轮整理并不假称全部重新读；`catalogue` 是受限导航。按版本和实际证据升级，不按笔记字数或模型自信升级。

## 地基与探索分工

[HANDOFF](../HANDOFF.md)和[实验组合](../experiments/EXPLORATION_PORTFOLIO.md)给本地 Agent 一个可研究的问题和多种高信息量操作，而不是预设唯一发现。Agent应持续读论文、用结果更新领域图谱、主动替换更好的实验。数据审核和prompt偏置控制不要挤占整个科学主轴。

所有具体数值主张应追到原文或不可覆盖的本仓库证据；原模型试跑的持久化数值和哈希在 [evidence/](../evidence/README.md)。失效的A/B/C故事保留历史但不再构成工作队列。

## 一致性维护

```bash
python scripts/build_knowledge_index.py
python scripts/check_knowledge.py
python scripts/query_knowledge.py --query 'word sense' --limit 8
```

新增/改读一篇后更新 sources.tsv、笔记和必要的领域画像；生成索引与受限来源卡。自动检查只保证条目覆盖、路径/来源/状态一致，不宣称文章真实或idea好。严肃的质量判断仍需对照原文和实验。
