# Hakaze Cho et al. 2025/2026 — 从常见 ICL 困惑到机制区分的实验逻辑

- **ICLR 2025**: https://proceedings.iclr.cc/paper_files/paper/2025/hash/22d4f952efa13970f0b1ffb22170d416-Abstract-Conference.html
- **ICLR 2026**: https://proceedings.iclr.cc/paper_files/paper/2026/hash/105112d52254f86d5854f3da734a52b4-Abstract-Conference.html
- **ICLR 2026 arXiv**: https://arxiv.org/abs/2509.21012
- **2026 Official code**: https://github.com/hc495/Verb_subspace
- **Reading**: this entry **S3** (official conference abstract and 2026 code README; full 87-page paper presently inaccessible to verified complete reading in this session; method-level discussion is therefore explicitly bounded). **Do not label S1**. Prior discussion of the PDF is not a substitute for page-specific current review.

## 研究共同体的根本矛盾

ICL 可被解释为任务向量、label copying、induction, task recognition/learning。若仅给几个 input-output examples，模型如何在不更新参数的情况下选择正确任务？这不是完全空白的问题：许多路线在相同现象上提供部分解释。

ICLR 2025 的 *Revisiting In-context Learning Inference Circuit* 为 ICL 提出 Encode/Merge/Retrieve-Copy 等操作，并承认有 bypass 路径。它的科学尺度：由单一注意机制叙事升级为**多操作 + 可替代路径**的机制假说，而不是发明一个全新 benchmark。

## 2026 论文 idea 是怎样由矛盾驱动的？（INFERENCE）

如果主流 ICL 视角主要是 demos 带来新的 label/content，为什么**few-shot demonstrations 不包含正确标签时仍可能有效**？这不是“模型很厉害”或“这个 prompt 好用”，而是产生替代理论需求。候选机制：示例不只是添加任务信息，可能通过**移除不相关表征成分**使已有的信息更可访问。

## 重要的实验逻辑（基于作者官方摘要，FACT / INFERENCE 分开）

1. **初始反例**（FACT）零样本 query 的多任务信息混在表征里，使 intended task 难以选定；label missing condition 在若干任务中使简单 copying 解释困难。
2. **构造性充分性**（FACT）用低秩滤波器从表征中选择性移除信息，可以令零样本模型向指定任务输出偏移。**不表示自然模型必然用了这个 filter。**
3. **自然观测**（FACT）用特制几何指标比较实际 few-shot ICL 的表征变化，发现与 task-oriented removal 相容的迹象。
4. **因果必要性**（FACT）识别 Denoising Heads 并消融，干预阻断信息移除后 ICL accuracy 下降，正确标签不在示例中的情况尤为明显。
5. **逆推链条（INFERENCE）** 每层实验都专门弥补上个环节：人工 filter 可行≠LM 自然使用→补自然 measurements；相关表征≠计算必要→做定向消融；最终的机制解释仍有架构/任务边界，并非全部 ICL 解释。

## 为什么这比“多做实验”重要？

作者 **不是为了证明所有实验有正信号而堆更多任务**。先找到已有解释无法充分处理的最小反例，然后构造可分离的因果测量；实验不能支持更强主张时，只保留较弱主张。

可迁移的高阶思路：寻找 **某个旧理论推断所不允许/预测错误的现象**，而不是完全新话题。在本文实例是 label-absence，可能对应我们领域的 global transfer vs local sense collision，但后者还是不同指标、尚不是真正可证伪矛盾。

## 我们下一步必须学习的具体设计而非论文结构（INFERENCE）

若走 A：找到已学会词义、能正确选择终极意义、却在下游后续推断仍受错误来源影响的匹配反例（如果不存在就停止）；先验证是否普通 ambiguity 也有相同残余，再决定是否做内部 patch。**不能**先规定“语言—语义—输出”三个模块，再去找 3 个 probes。

若走 B：找到“错误语义锚点也有收益”的真正对照；设计可实现错误对齐而不改变频次/有效容量的人工干预。构造性成功与自然模型机制必须分开。

## 留给下次的正式精读

2026 87-page paper（尤其训练 low-rank filter 的 supervised objective、metric 的几何与可识别性、ablation 可能的 collateral effect、跨模型效果）；2025 full paper 每阶段反事实对照。官方 GitHub main_experiments.py/encoding_magnitude 文件可帮助追源，但本轮没有跑这些代码；不能从 README 把具体实验描述扩写成未核验“事实”。
