# 文献与研究资产总索引

<!-- GENERATED: edit knowledge/sources.tsv then run scripts/build_knowledge_index.py -->

共 **56** 个来源条目。S0: 2 / S1: 27 / S2: 4 / S3: 23。

**登记齐全不等于全部精读。** S1为有主方法/结果阅读记录，S2为定向正文，S3仅摘要/元数据，S0仅题名。
`current` 是本轮补读或新读；`inherited` 保留前轮已有笔记，不假称本轮全部重读；`catalogue` 是有边界的导航。

从 [领域画像](FIELD_GUIDE.md) → [实验设计来源](EXPERIMENT_DESIGN_LESSONS.md) → [本地交接](../HANDOFF.md) 进入当前工作。
机器可检索 [sources.tsv](sources.tsv)；未精读资料的已知范围与禁用推断在 [来源卡](catalogue/SOURCE_CARDS.md)。

## lexical-sharing

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P001 · [Kallini et al. — False Friends Are Not Foes (Findings EMNLP 2025)](https://aclanthology.org/2025.findings-emnlp.1153/) | S1 / inherited | [记录](papers/kallini-2025-vocabulary-overlap.md) | 原笔记记录主实验、词表对照和参数/频次边界；本轮整合而非重新复现 |
| P002 · [Škrjanec et al. — Is Cross-Lingual Transfer in Bilingual Models Human-Like? (CMCL 2026)](https://aclanthology.org/2026.cmcl-1.10/) | S1 / inherited | [记录](papers/skrjanec-2026-human-like-transfer.md) | 原笔记：共享词形surprisal和累计频次；不可当作sense使用测量 |
| P009 · [Brillant & Pinter — Tokenizing Crosslingual Homographs (arXiv 2026)](https://arxiv.org/abs/2607.17689) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p009) | 语言条件分词是相关干预入口；本轮全文访问失败，不推断效果大小与因果充分性 |
| P021 · [Conneau et al. — Emerging Cross-lingual Structure (ACL 2020)](https://aclanthology.org/2020.acl-main.536/) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p021) | 共享词表非跨语言迁移必要条件的背景入口；本轮未重读完整原实验，具体结论回原文 |
| P022 · [Limisiewicz et al. — Vocabulary-overlap study (Findings ACL 2023)](https://aclanthology.org/2023.findings-acl.350/) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p022) | 不同任务对词表重叠的作用可能不同；保留旧索引导航，未核实全文不作定量支撑 |

## lexical-diagnostics

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P003 · [Cahyawijaya et al. — StingrayBench (Findings NAACL 2025)](https://aclanthology.org/2025.findings-naacl.178/) | S1 / inherited | [记录](papers/cahyawijaya-2025-stingray.md) | 原任务标签/人工错误语句/语言偏差；不等同自然完整sense分布 |
| P004 · [Tanwar et al. — Multilingual LLMs Struggle to Link Orthography and Semantics (arXiv v2)](https://arxiv.org/abs/2501.09127) | S1 / inherited | [记录](papers/tanwar-2026-orthography-semantics.md) | 继承正文与源码审计；Q1级联、来源标签与语法风险不是已证实内部机制 |
| P005 · [Kitamura et al. — Doppelganger-JC (IJCNLP 2025)](https://aclanthology.org/2025.ijcnlp-long.96/) | S1 / inherited | [记录](papers/kitamura-2025-doppelganger-jc.md) | 继承三任务、同形复制与数据方法分析；原分数和我们的改编读出分开 |
| P006 · [Vázquez Abuín et al. — False Friends or Cognates? (ACL 2026)](https://aclanthology.org/2026.acl-long.1818/) | S1 / inherited | [记录](papers/abuin-2026-romance-wic.md) | 继承正文和六TSV审计；R标签只对应给定上下文，不是总体词典分布 |
| P007 · [SemCog Bench (arXiv 2026)](https://arxiv.org/abs/2606.13218) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p007) | 已知公开数据入口和阿拉伯语—希伯来语任务；本轮未可靠获取全文，不据此提出机制结论 |
| P008 · [Uban et al. — Friend or Foe? Semantic False Friends across Romance Languages (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.773/) | S1 / current | [记录](papers/uban-2025-semantic-false-friends.md) | 本轮阅读数据/标注层级、静态和上下文分布方法、主要结果；非所有附录 |

## human-theory

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P010 · [Marecka et al. — False friends or real friends? (Cognition 2021)](https://doi.org/10.1016/j.cognition.2020.104477) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p010) | 人类L2形式/意义学习背景；原文细节未精读，不外推人类与LLM同构 |
| P011 · [Winther et al. — Cumulative Frequency Can Explain Cognate Facilitation (CogSci 2021)](https://repositories.cdlib.org/uc/item/5d39q2k1) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p011) | 累积词频是形式促进的竞争解释来源；定量设定未独立重核，不当作语义理解证据 |
| P013 · [Dijkstra, van Hell & Brenders — Sentence Context Effects (Bilingualism 2015)](https://doi.org/10.1017/S1366728914000388) | S1 / inherited | [记录](papers/dijkstra-van-hell-brenders-2015-sentence-context.md) | 上一轮笔记已从S2升级S1：材料方法排除完全同形目标用于语言辨识；人类RT非LLM语义logit |
| P014 · [Biloushchenko, Dijkstra & Sandra — List composition and task demands (Bilingualism 2026)](https://www.cambridge.org/core/journals/bilingualism-language-and-cognition/article/effects-of-list-composition-and-task-demands-on-interlingual-homograph-processing-in-unbalanced-trilinguals/4920AF0BB80130ACC9AB4D7388965015) | S1 / inherited | [记录](papers/biloushchenko-dijkstra-sandra-2026-task-list-homographs.md) | 继承六实验和task/list交互分析；不等同模型内部词义门控 |
| P024 · [Dijkstra & van Heuven — BIA+ (2002)](https://doi.org/10.1017/S1366728902003012) | S1 / current | [记录](theories/BIA_PLUS.md) | 本轮原文主要§3–4.7与Fig2、部分作者回应；语言节点不必先于词汇识别，理论不等于全实现 |
| P025 · [Christianson et al. — Thematic roles assigned along garden paths linger (2001)](https://doi.org/10.1006/cogp.2001.0752) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p025) | 残留误解经典背景；只保留已确认主题，不补写未核验实验量或效应 |
| P026 · [Christianson et al. — Paraphrase follow-up (2009)](https://pubmed.ncbi.nlm.nih.gov/19210099/) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p026) | 用释义而非单个问答检测残留误解的背景；原全文未精读，不作模型同构证据 |
| P027 · [Tarin et al. — Cross-language contextual interference (Bilingualism 2026)](https://doi.org/10.1017/S1366728925000380) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p027) | 眼动和语境干扰背景，保留已检索来源；词频/实验结构的强说法需原文依据 |
| P032 · [Paape & Vasishth — Latent-process garden-path study (JML 2026)](https://doi.org/10.1016/j.jml.2026.104748) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p032) | 区分进入garden path与重分析成本的背景入口，未精读不写模型适用定论 |

## cross-domain-methods

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P012 · [Östling & Kurfalı — Language Bias under Conflicting Information (arXiv v2 2026)](https://arxiv.org/html/2604.07123v2) | S1 / inherited | [记录](papers/ostling-kurfali-2026-conflicting-language.md) | 继承证据语言交换对照；冲突事实检索不等于词义冲突 |
| P040 · [Tsujimura et al. — Belief Consistency (ACL 2026)](https://aclanthology.org/2026.acl-long.1860/) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p040) | 信念一致性与推理正确性的邻域资料；旧路线候选，不是现已证明的词义残留机制 |
| P053 · [Kurfalı & Östling — Conflicting-needle study (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.1742/) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p053) | 2026语言交换论文的直接前序；重复/位置/词串影响是竞争解释来源，未完整复读 |

## representation-use

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P015 · [Dumas et al. — Separating Tongue from Thought (ACL 2025)](https://aclanthology.org/2025.acl-long.1536/) | S1 / inherited | [记录](papers/dumas-2025-separating-tongue.md) | 继承概念与输出语言activation交换主文；广义分离已是先例 |
| P016 · [Körner et al. — When Meanings Meet (EACL 2026)](https://aclanthology.org/2026.eacl-long.145/) | S1 / inherited | [记录](papers/korner-2026-when-meanings-meet.md) | 继承训练阶段、polysemy和复制错误类型；patch成功不自动等于理解改善 |
| P017 · [Ravisankar et al. — Can you map it to English? (EACL 2026)](https://aclanthology.org/2026.eacl-long.225/) | S1 / inherited | [记录](papers/ravisankar-2026-english-alignment.md) | 继承实例级alignment与同答案/不同语义donor控制；保留自然机制解释边界 |
| P044 · [Wang et al. — Lost in Multilinguality (ACL 2025)](https://aclanthology.org/2025.acl-long.253/) | S1 / current | [记录](papers/wang-2025-lost-in-multilinguality.md) | KLAR/成功失败轨迹/shortcut主文与Fig5–7；MLM指multilingual，非masked；训练评测独立性需限定 |
| P045 · [Sun et al. — Bridging the Language Gap: Shared Circuits for Multi-Hop Reasoning (AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/40592) | S1 / current | [记录](papers/sun-2026-multihop-access-circuits.md) | 主方法、数据拆分、头微调和迁移表；手工正确内容注入不单独证明无干预可访问性 |
| P051 · [Nie et al. — Language confusion analysis (Findings EMNLP 2025)](https://aclanthology.org/2025.findings-emnlp.37/) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p051) | 补回早期讨论遗漏的语言输出混淆来源；未重新精读，不能据此给后层失败统一结论 |

## representation-measurement

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P018 · [de Seyssel et al. — Discriminating Form and Meaning with Minimal-Pair ABX (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.1210/) | S1 / current | [记录](papers/de-seyssel-2025-abx.md) | 本轮原文方法、zero-effect验证、层/训练及下游相关；官方SAC Highlight已核验 |
| P019 · [Inaba et al. — How a Bilingual LM Becomes Bilingual (Findings EMNLP 2025)](https://aclanthology.org/2025.findings-emnlp.725/) | S1 / current | [记录](papers/inaba-2025-bilingual-sae.md) | 本轮SAE语言/语义指标、训练轨迹和成分注入；激活混语不等于具体sense使用 |
| P052 · [Mukherjee et al. — Bilingual representation changes (arXiv 2026)](https://arxiv.org/abs/2608.26576) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p052) | 补回早期讨论的双语训练表示变化资料；书目信息沿用历史导航，未独立核实完整方法 |

## transfer-controls

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P020 · [Goworek & Dubossarsky — Multilinguality Does not Make Sense (EMNLP 2025)](https://aclanthology.org/2025.emnlp-main.1773/) | S1 / current | [记录](papers/goworek-2025-sense-transfer-controls.md) | 本轮等数据量/目标暴露/zero-shot及任务边界；微调结论不能泛化为多语预训练无益 |
| P023 · [Shao et al. — Bilingual/parallel data contributions (ACL 2026)](https://aclanthology.org/2026.acl-long.1706/) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p023) | 混语/平行训练数据的背景入口；不是当前局部词义机制的直接证据，标题元数据沿用旧索引 |

## human-model-comparison

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P028 · [Amouyal et al. — When the LM misunderstood the human chuckled (ACL 2025)](https://aclanthology.org/2025.acl-long.403/) | S2 / inherited | [记录](papers/amouyal-2025-2026-gardenpath.md) | 继承定向阅读/联合比较，不升格为所有附录已读；多测量garden-path已非空白 |
| P029 · [Amouyal et al. — Humans/LMs on complex structures (ACL 2026)](https://aclanthology.org/2026.acl-long.1040/) | S1 / inherited | [记录](papers/amouyal-2025-2026-gardenpath.md) | 继承主实验/多结构结果；通用重分析不等于cross-lingual特异机制 |
| P031 · [Clark, Levy & Gibson — Targeted regressions in noisy-channel garden paths (CoNLL 2026)](https://aclanthology.org/2026.conll-main.25/) | S1 / inherited | [记录](papers/clark-2026-noisy-channel.md) | 继承人类错误位置与过程观测分析；attention不能直接当眼动回视 |

## experiment-design

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P030 · [Yoshida et al. — Existence Proof for Garden-Path Surprisal (ACL 2026)](https://aclanthology.org/2026.acl-long.1694/) | S1 / inherited | [记录](papers/yoshida-2026-gardenpath-surprisal.md) | 继承constructive counterexample与held-out RT；一个模型代理不足不等于理论不可能 |
| P033 · [Ok & Lee — Lost in the Prompt Order (Findings ACL 2026)](https://aclanthology.org/2026.findings-acl.1921/) | S1 / inherited | [记录](papers/ok-lee-2026-prompt-order.md) | 继承训练格式/忘记选项/因果注意的竞争实验；输入部件顺序不等于生成Q1自我条件化 |
| P036 · [Cho et al. — Revisiting In-context Learning Inference Circuit (ICLR 2025)](https://proceedings.iclr.cc/paper_files/paper/2025/hash/22d4f952efa13970f0b1ffb22170d416-Abstract-Conference.html) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p036) | 高层Encode/Merge/Retrieve-Copy与bypass来源；完整手稿未独立重读，和2026精读范围分开 |
| P037 · [Cho et al. — Task-oriented Information Removal (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/105112d52254f86d5854f3da734a52b4-Abstract-Conference.html) | S1 / inherited | [记录](papers/cho-2025-2026-method-genesis.md) | 继承恢复87页原文后的主文/附录方法/主要表图精读；不称全部图复算或代码复现 |
| P038 · [Yang, Cho et al. — Task Vectors, Learned Not Extracted (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/79ada0f9bc4e41192ad5a80d13c8ca7e-Abstract-Conference.html) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p038) | 任务向量构造与提取的概念背景；本轮未读完整实验，不能充当TO或TVS细节证明 |
| P039 · [Yang, Cho et al. — Localizing Task Recognition and Task Learning (ICLR 2026)](https://proceedings.iclr.cc/paper_files/paper/2026/hash/974726d56a6ddfac48486e57d5e798e4-Abstract-Conference.html) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p039) | 任务识别与学习分解的背景入口，不自动套用到语言/词义模块 |
| P043 · [Xiong et al. — Capturing In-Context Learning Dynamics with Task Operators](https://arxiv.org/abs/2610.01054) | S1 / current | [记录](papers/xiong-2026-task-operators.md) | NeurIPS2026官方目录+作者发表列表核验；§3–4.5、Table1–3、Fig2–3；无oral/award断言 |

## learning-history

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P034 · [Elhady, Agirre & Artetxe — Continued language adaptation (2025)](https://arxiv.org/abs/2506.00288) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p034) | 保留历史schedule/forgetting背景，不恢复已撤销训练路线，不臆造新的路径依赖发现 |
| P035 · [Arnett et al. — Bilingual priming and learning (ACL 2025)](https://aclanthology.org/2025.acl-long.1010/) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p035) | 结构priming与学习顺序的背景；未重新精读，不能等同false-friend局部意义历史效应 |

## survey

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P041 · [Yuemei Xu et al. — A Survey on Multilingual LLMs: Corpora, Alignment, and Bias](https://arxiv.org/abs/2404.00929) | S2 / current | [记录](papers/surveys-2024-multilingual-landscape.md) | v3引言/分类/对齐和bias相关章节；历史地图，不沿用未核验闭源数据比例 |
| P042 · [Yuzhuang Xu et al. — A Survey on LLMs with Multilingualism: Recent Advances and New Frontiers](https://arxiv.org/abs/2405.10936) | S2 / current | [记录](papers/surveys-2024-multilingual-landscape.md) | v2训练/推理/评测分类定向阅读；不是2026最新模型事实或独立因果实验 |
| P056 · [A Survey of Multilingual Knowledge Editing](https://arxiv.org/abs/2505.14393) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p056) | 仅摘要/导航，本轮不借它断言知识编辑机制；当前地基依已读两综述和直接原论文 |

## measurement-methods

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P046 · [Zheng et al. — Large Language Models Are Not Robust Multiple Choice Selectors (ICLR 2024)](https://arxiv.org/abs/2309.03882) | S1 / current | [记录](papers/zheng-2024-pride-selection-bias.md) | §2.4–4、Fig3–4/Table2和PriDe假设；双顺序偏置可能相消，不把单序翻转当新发现 |
| P047 · [Zhang & Nanda — Towards Best Practices of Activation Patching: Metrics and Methods](https://arxiv.org/abs/2309.16042) | S1 / current | [记录](papers/zhang-nanda-2023-patching-methods.md) | §3–6/8与Fig3–5：corruption/metrics/window改变估计对象；不外推所有模型架构 |
| P048 · [Heimersheim & Nanda — How to use and interpret activation patching](https://arxiv.org/abs/2404.15255) | S2 / current | [记录](papers/heimersheim-nanda-2024-patching-interpretation.md) | v1方法解释定向阅读；教程/预印本，不作新的多语实证结论 |

## conference-navigation

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P049 · [The Fractured Interlingua: Geometric Bottlenecks in Cross-Lingual Knowledge Editing](https://neurips.cc/Downloads/2026) | S0 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p049) | 官方目录题名定位；本轮无可靠正文，不引用实验结果，不推定oral/main track细节 |
| P050 · [FACBench: Formal-Anchor Collisions in Multilingual Mathematical Grounding](https://neurips.cc/Downloads/2026) | S0 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p050) | 官方目录题名定位；未读正文，仅提示相邻探索空间，不假设数据/结论 |

## data-resource

| ID / 来源 | 阅读 / 产生轮次 | 资产 | 阅读与使用范围 |
|---|---|---|---|
| P054 · [MCL-WiC — Multilingual and Cross-lingual Word-in-Context resources](https://github.com/SapienzaNLP/mcl-wic) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p054) | 公开来源入口及上下文词义关系任务；不是严格同形/时序修正匹配集，使用许可另核验 |
| P055 · [XL-WiC — Multilingual Word-in-Context resources](https://pilehvar.github.io/xlwic/) | S3 / catalogue | [记录](catalogue/SOURCE_CARDS.md#p055) | 公开基准入口；普通WSD能力参照，不自动匹配false-friend分布 |

## 历史与范围

原先40条索引的完整快照保留在 `history/INDEX_BASELINE_2026-10-12.txt`，检查脚本防止静默漏收原来源。
表内网址重复可以是不同目录题名（例如官方会议总目录）；ID才是唯一主键。
S3/S0不支持细致机制或实验结论；后续真正读到原文时更新记录，而不是把空白写成已知。
目前没有声称已完成整个领域或所有最新会议论文的阅读。正式主张依已核实的原文与独立实验。
