# Kitamura, Huang & Aizawa 2025 — Doppelganger-JC

- **Paper**: https://aclanthology.org/2025.ijcnlp-long.96/
- **Code/data**: https://github.com/0017-alt/Doppelganger-JC
- **Depth**: **S1** (原有 §§1–5/Fig.2；2026-10-13 定向补读 Appendix H/M/N、Tables 21–24，审计并本地复核 Type-1 源码；非全附录精读)
- **Role**: 可复核的词义/语境/翻译地基；其标签和 shortcut 解释均不限制我们的研究对象。

## 1. 关注的自然问题

中日共享汉字词形非常广泛，大多数共通词有相似意义；在这条有用的规律中，少数词的意义已经分化。模型在翻译时照搬字形，是因为**套用了通常有益的表面捷径**，还是词义能力彻底缺失？

## 2. Idea 起源尺度（INFERENCE）

引言说观察到实际翻译的误用，受到 Tanwar 2025 以及中日共有汉字词研究启发。提出的创新不在更复杂的架构，而在：**把通常不会暴露的 shared-form shortcut 放大成可审查的局部任务**。比 Stingray 多走一步的是特别分离 word-meaning / word-in-context / sentence-translation，且检验共享 POS 对 shortcut 的关系。

## 3. 论文事实

§3 的数据流水线图（Fig. 2）：日语词表 JKVC → 查跨语言意义集合、自动生成目标句/真实译文/三个误导译文 → 母语者核查 → 词义、上下文、翻译任务。论文分析将包含错误跨语言同形字串的译文作为 homograph shortcut 之一，观察部分模型的强错位及 POS 相关性。

实际 GitHub 的 questions/jp_zh/homographs.py 样本字段包括 target-sentence, target-meaning, correct, wrong1–3 和 English reference；词表文本划分 homographs 与不同语言的 unique meanings。**这比抽取字典释义后人工凑几个句子更接近可执行基线**。

## 4. 逆向实验链（INFERENCE）

从实际复制例子出发，比较孤立词义、语境意义、候选翻译，并补充自由生成；再检查 POS 等相关因素。主表的 translation 是候选评分，不能把三任务排序直接重建为生成时的知识→使用流水线。*这些任务并不直接定位造成捷径的层与操作*。

## 5. 证据边界

- 如果 model 选 wrong translation，可能只是在输出侧复制容易的字串，不能认定 reading sense 是错的。
- 语义/翻译任务都用选择项，候选概率、option phrase-length、语义相似度可能成为偏置源。
- 样例多数经自动生成再人工核验；词频、真实分布和 item independence 仍需要研究者复核。

## 6. 最近邻

Körner 2026 也讨论 patch 后避免复制而非理解改善。仅并列翻译和意义准确率、或增加一次 patch，增量不充分；这不意味着该对象已经解释完毕。质量与完成度对齐 ACL/EMNLP/NAACL 主会，尤其 Dumas/Wang 的干预链，同时独立检查它们的控制与泛化证据。

## 7. 下一步

使用真实的 word-in-context 与 translation 题对比；另加 **和 copy 不相关的下游语义推断**，并匹配无歧义翻译、普通多义、答案长度和词形复制偏向。若所有看似“意义竞争”的效应都只来自自由翻译/候选字串，则路线 A 的内部词义冲突叙事不成立。

## 8. 2026-10-13 原文与源码纠正

Appendix H 已有独立 MCQA 与循环轮换；本项目不能以此自称新设计。Appendix M 是去掉定义换行的结果，匹配当前公开源码；Appendix N 已含 Qwen2.5-14B，因此本轮两个模型都是既有模型的本地复核。

Type-1 共464词族，WM各464，JP语境/翻译462、ZH455。公开 WM loader 缺自身词字段，本地仅用字典键补齐；其余11048个原评分字符串逐项与源 runner 一致。整段 token 平均 NLL、候选条件 NLL、显式 chat 与自由生成不是同一测量。

两模型六项分数均接近对应附录（Llama最大差0.65pp、Qwen0.45pp），但使用 Llama 镜像、批量 bf16 等差异，不能称逐 bit 忠实复现。新词义问答更好不证明内部知识完全存在；生成同形不证明错义；源“完全异义”分类也不可直接升格为句级互斥 gold。详见[方法审核](../notes/DOPPELGANGER_METHODS_AUDIT_2026-10-13.md)、[自由翻译评读](../notes/FREE_TRANSLATION_REVIEW_2026-10-13.md)与[本轮研究更新](../notes/LOCAL_RESEARCH_UPDATE_2026-10-13.md)。
