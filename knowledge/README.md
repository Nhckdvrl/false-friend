# Research Knowledge Base / 研究知识库

**研究资产，不是论文清单。** 最后审计：2026-10-11。此仓库仍处于 *hypothesis-development*；尚无新项目的科学实验结果。

## 学术工作流

阅读 → 分离作者主张与我们的推理 → 逆向重建 idea 生成 → 对照最近邻文献 → 解释每一个实验解决的缺口 → 提取可复用的设计原则 → 产生候选问题 → 事先写下足以否决自己的实验 → 才考虑实现。

**不把阅读量、笔记长度、实验数量当作科学贡献。**

## 入口

- [PAPERS_INDEX.md](PAPERS_INDEX.md) — **所有相关论文的索引、实际核验深度和笔记链接**。文献索引 != 全部精读。
- [CONCEPT_MAP.md](CONCEPT_MAP.md) — 跨论文的命题、证据张力、认识空白及其反例。
- [CITATION_LEDGER.md](CITATION_LEDGER.md) — 核心断言对应具体论文、章节、页码；历史错误纠正。
- [PAPER_NOTE_TEMPLATE.md](PAPER_NOTE_TEMPLATE.md) — 必须分析 idea 起源、尺度、related-work 距离、可证伪的区分性实验。
- [theories/](theories/) — BIA+ / Good-Enough / measurement vs causal identification：不是照搬人类理论。
- [papers/](papers/) — 阅读后独立的论文资产；结论和 **我们推测的作者思路**明确分开。
- [ideas/](ideas/) — 三条路线的重新定标、实验缺口与反证对照。
- [data/DATASET_ATLAS.md](data/DATASET_ATLAS.md) — 真实数据资源、标签语义和适用任务。
- [RESEARCH_AGENT_PROTOCOL.md](RESEARCH_AGENT_PROTOCOL.md) — 给后续本地 Agent 的检索、建模和停止协议。

## 阅读标记（强制）

- **S1 methods/results inspected**：本轮核对过论文正文关键的引言、方法、重要实验或表/图、讨论/局限；**不代表通读每个附录**。可写明确的实验分析笔记。
- **S2 targeted/partial**：核对过正文/部分方法/结果或网页全文，仍有关键段落未核实；未核实处必须逐条标记。
- **S3 metadata/abstract**：只确认摘要、书目信息或历史注记；**不可写作精读，不可推出未验证的机制结论**。
- **S0 to-read**：尚待查阅，只有导航作用。

所有重建的 idea 来源均标为 **INFERENCE（我们的推测）**，不能假装作者亲口解释了自己的创意来源。每份 S1/S2 笔记需标清“已查证的证据 / 推测 / 反例 / 比最近邻多走的一步 / 下次要验证什么”。从不把相关性自动解释为因果。

## 使用规则

1. 讨论词汇共享，先读 Kallini + Škrjanec + 本仓库 2026-08 历史失败记录。
2. 讨论局部同形词错误，先读 Stingray + Tanwar + Doppelganger-JC + Abuín。
3. 讨论激活与机制，先读 Dumas + Körner + Ravisankar，以及对 patching 替代解释的控制。
4. 讨论后文纠正，必须同时读 Good-Enough / garden-path 的人类与 LLM 工作；**不是新领域**。
5. 设计新实验先填写最强竞争解释与失败条件；测试不同任务的输出不可以混为同一个“语义正确率”。
6. 文献发现新近先例时，主动撤销或降低当前 idea 的 novelty claim。改结论，不做防御性修补。
7. 历史精读笔记不得凭空补齐：在索引中诚实标记未充分查阅。

## 这次重构没有做的事情

没有下载或再分发大篇幅论文 PDF；仅链接原始论文。没有做真实模型推理或跑训练；没有生成新实验发现。持续扩充笔记时应使用合法原文来源并避免长段直接复制。
