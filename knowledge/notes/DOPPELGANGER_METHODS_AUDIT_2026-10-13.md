# Doppelganger Type-1：实现与推断复核

2026-10-13。独立检查本轮 runner、analysis、source audit；只用 CPU 和已保存结果，未改正在使用的推理 runner。本记录是方法审核，不是额外语义标注，也不证明因果机制。

## 1. 已发表协议与复核目标

补读原论文附录 H、M、N，并核对 [正式 PDF](https://aclanthology.org/2025.ijcnlp-long.96.pdf)。H 明确将直接回答选项的 MCQA 实验与 perplexity 方法分开；四次重排使正确答案各处于 A/B/C/D，Table 16 报告输出位置。公开 `calc_ppl*.py` 实现的是后一种分数流程，不能因该源码没有标签就推断作者没有做 MCQA 实验。

当前源码去掉释义换行，应对照 M 的 Tables 21–22。N 的 Tables 23–24 已包含 Qwen2.5-14B-Instruct；这是已发表模型的复核，初始设计对其“独立更强模型”地位的判断需要更新。正文 Tables 3–4 和附录的翻译方向编排不同，必须按表注映射。

Llama Type-1 的数值核对（百分比）：

| 来源语言/任务 | 去换行附录 | 本地 | 差值 pp |
|---|---:|---:|---:|
| JP meaning | 53.88 | 54.0948 | +0.2148 |
| JP context | 67.75 | 68.3983 | +0.6483 |
| JP→ZH translation | 71.43 | 71.4286 | -0.0014 |
| ZH meaning | 31.03 | 31.4655 | +0.4355 |
| ZH context | 63.96 | 63.9560 | -0.0040 |
| ZH→JP translation | 70.55 | 70.7692 | +0.2192 |

附录 Qwen14B Type-1 对照为 JP：60.34 / 64.07 / 74.03；ZH：45.91 / 74.73 / 71.21（meaning / context / 从该语言翻译）。这些是原文数值，不是本地结果。

## 2. 实现结论与真正边界

未发现 gold=0 映射、shifted CE、右 padding 截取、四轮换按内容平均 logp、left-padding 生成或 EOS 截断的致命错误。`score_labels` 先在完整词表计算 log-softmax，再取四标签，因此原始保存值能检验选项总概率质量（PMA）。四轮换并非全部 24 种排列；它控制每个内容各占一个位置，不能消除所有内容间顺序交互。

来源 mock audit 已检验 11048 个完整候选字符串与原作者函数完全一致，WM 仅作已披露的自身词字段修复。词族为 464 个唯一 JP/ZH pair，无重复 item_id、无同一词形跨多个 family。96 族抽样的中文 context/translation 各实际 94 族，不能报告成每格 96。

源数据有四行完全重复候选：JP→ZH 果子（2=3）、前年（0=1）、顾客（0=1）；ZH→JP 老眼（1=2），索引从 0 开始。前年、顾客的源 argmin 遇平分取 0，无法把该行的源标签正确解释为分辨了两个意义。保留原任务行，同时标记重复，语义分析单独审核。

WM 与 context 的两项目标词释义都一致，但因原源码按各自可用词序选邻接干扰项，JP 有 2 行、ZH 有 14 行的其他干扰项变化。因此整体 WM→context 改善并非每行都只操纵上下文。纯粹的上下文对比应先报告候选完全相同的配对子集，变更行完整保留。

跨 token 边界不是罕见事件：Llama 的 JP meaning/context 分别有 1056/1856、1050/1848 个候选把结尾标点与外部收尾引号合并为 token；ZH→JP translation 为 1815/1820。当前 `candidate` 定义是所有与候选字符相交的 token，不能称严格的独立字符串条件概率。Qwen 的对应跨收尾数为 0、0、62/1820。好消息是两个 tokenizer 的全部 11048 组 source/null 候选 token 序列分别完全相同，因此当前 source-null 差值没有额外引入候选 token 集合不匹配。逐项统计见下述 audit。

Llama 144 条生成有 3 条 hit-token-limit：中文 meaning 2 条、JP→ZH translation 1 条；其余 141 条均以配置的 EOS 结束，没有把 padding 当文本或漏记停止。截断输出须保留并标明语义判断的有限性。

## 3. 哪种新观察能支持哪种解释

原裸文本 PPL 与新 chat MCQA 同时改变 chat template、指令、显式来源语言、共同可见选项、答案空间和评分。即使准确率大升，也只能支持“这些条件下正确答案可访问”，不能将全部提升归因于长度或先验，更不能证明自然语义选择机制。

候选平均/总和与原整段平均比较，是同一次前向的读出变化；仍混合了长度归一化、移除前缀项、移除收尾项。null-input 也同时删去词和语境。INFERENCE：若要归因，应先用已有分解逐项计算排名变化，再设计仅改变一个信息源的配对实验；不要将不同读出彼此独立成功次数当作独立知识证据。

Llama 完整词表 PMA 组均值为 0.999858–0.999986，全 2288 条轮换的最高概率首 token 都属于 A/B/C/D；其 chat 结果没有被显著的 off-label 格式失败掩盖。这个判断没有对 A/B/C/D 强制重归一化。仍须看全轮正确、内容稳定、具体误义和自由输出；PMA 不能证明语义正确。

## 4. 数值核验与可重建检查

同一次前向的手工 shifted float CE 应与库 loss 一致，这是实现检验。bf16 batched 与 singleton 前向可能有独立的数值漂移；Llama 首个核验项绝对差 0.000968。Qwen 首次作业触发原 0.002 guard，应归为数值核验失败待查，不能作为科学负结果。保存全部分数后分别报告同前向误差、batch/single 漂移及候选排序是否改变；单个核验项不能给全部样本的误差上界。

新增 CPU 检查入口：[audit_doppelganger_measurements.py](../../scripts/audit_doppelganger_measurements.py)。它读取不可覆盖的 `inputs.jsonl`、可用的 chat/generation 结果与缓存 tokenizer，另写 `measurement_audit.json`，不覆写原推理数据；记录重复候选、边界、source/null token 一致性、上下文候选变化、完整词表 PMA、off-label argmax 与停止标记。Qwen 首次作业的 audit 只含候选材料/边界，不能称已完成 chat 或生成审核。

```bash
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/audit_doppelganger_measurements.py runs/2026-10-13-doppelganger-llama8b runs/2026-10-13-doppelganger-qwen14b
```

代码验证、原分数复核、新读出观察和因果解释是四个不同层次。当前前三层各有上述明确范围；尚无因果机制结论。

## 5. 两模型完成后的数值稳定性与主张复核

追加于 2026-10-13；只读两模型基线完整结果作 CPU 审核，未读取 followup 题的模型结果。Qwen 成功运行目录是 `runs/2026-10-13-doppelganger-qwen14b-v2`，首次失败目录仍保留。

Qwen 的24个同前向 CE 检验误差全部为0；batch/single 最大平均 NLL 差为 **0.0177446157**。6组四候选 sentinel 的两种 argmin 全部一致：JP meaning/context/translation 为 0/1/0，ZH 为 0/0/0。但6组全部来自**同一词族 質問/质问**，仅覆盖6个语言任务格，不覆盖6个独立词族或整个长度分布。Llama 旧核验只有单题单候选的0.000968差，不能补称它有6组排序验证。两个条件下的数值一致性结论范围不同。

保存分数的 top1–top2 平均 NLL 距离小于0.04的行数如下。0.04是看到核验漂移后选择的工程敏感性阈值，**不是误差上界，也不是置信区间**；阈值外不保证永不翻转。

| 来源/任务 | N | Llama <0.04 | Qwen <0.04 |
|---|---:|---:|---:|
| JP meaning | 464 | 44 | 28 |
| JP context | 462 | 53 | 43 |
| JP→ZH translation | 462 | 69 | 55 |
| ZH meaning | 464 | 36 | 19 |
| ZH context | 455 | 52 | 32 |
| ZH→JP translation | 455 | 110 | 63 |
| 全部重复测量行 | 2762 | 364（13.18%） | 240（8.69%） |

因此不能用0.2–0.6 pp的复核差异讲模型机制、版本效果或严格原值不符；逐词近边界反转也应先复算。两个模型与对应已发表Type-1结果接近：Llama六项差距≤0.65 pp，Qwen六项差距≤0.45 pp。这支持本地原任务地基大致复现，不等于已取得同硬件逐样本一致。

稳健的**已保存观察**是很多原PPL错误在chat条件下四轮都选择正确内容，且并不限于上述近边界行。下表括号内为原PPL margin≥0.04的数量，仍不把阈值当误差证明。

| 来源/任务 | Llama 原错、chat全轮正确 | Qwen 原错、chat全轮正确 |
|---|---:|---:|
| JP meaning（96族） | 30（27） | 30（25） |
| JP context（96族） | 19（15） | 24（20） |
| JP→ZH translation（96族） | 3（2） | 7（3） |
| ZH meaning（96族） | 14（12） | 33（30） |
| ZH context（94族） | 21（18） | 16（15） |
| ZH→JP translation（94族） | 4（1） | 4（2） |

这些计数支持“原PPL答错不足以断言该条件下完全不能访问正确意义”；它们不支持“所有意义都已知”或“改评分恢复了同一个自然计算”。Qwen 所有2288个chat首token同样没有off-label argmax，PMA各组均值0.999842–1.000000（末位四舍五入）；两模型的此类差异不主要来自首token没有遵循选项格式。

必须收紧的主张：

- **不存在统一更好的新读出。** Llama中文WM的candidate-mean比source高16.81 pp，Qwen高10.13 pp；但日语或语境未普遍改善，candidate-sum使日语释义跌到约18–24%。source-null的evidence-mean在中文词义/语境提高，而翻译降到约20–38%。不能选一个有利分数当“真实知识”。
- **翻译缺口不能直接叫稳定语义使用失败。** Llama JP→ZH chat内容聚合为66.67%，但全轮正确仅30.21%、四轮内容稳定仅35.42%；Qwen分别82.29%、72.92%、79.17%。两模型程度不同，Llama的大量个例先受选项排列影响。只在位置稳定个例上追加语义审核也必须同时报告全部样本，防止事后选择。
- **很高的null translation标签一致率不证明源语句完全没用。** 它表明候选集合本身携带可利用的形式/流畅度信息；尚未识别哪些来源信息在真实翻译中被使用。
- **两模型整体复制出读出依赖性，不证明同一机制。** 近边界排序、不同prompt信息、原候选标签语义有效性、任务位置稳定性仍是不同问题。

完整计数与sentinel分数分别保存在两个成功运行目录的 `numerical_audit.json`；Qwen成功运行的 `measurement_audit.json` 也已生成。以上审核没有增加GPU运行，不能替代对近边界样本的singleton重算。
