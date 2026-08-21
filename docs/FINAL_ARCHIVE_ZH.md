# 最终归档：False-Friend Lexical Sharing

**日期**：2026-08-21  
**最终状态**：`ARCHIVED — CONCEPTUAL_IDENTIFICATION_FAILURE`  
**停止阶段**：Gate 1 数据 / causal-control preflight  
**GPU 决策**：停止投入；Gate 2、Gate 3 与机制实验全部取消  

---

## 1. 最终结论

这个项目不再继续。

最终停止原因**不是**：

- “false friends 没有 semantic interference”；
- “模型太小”；
- “训练不稳定”；
- “代码写坏了”；
- “样本量暂时不够，多找几个词就能解决”。

真正的问题是：

> **核心 causal contrast 所需要的对照对象，在当前自然数据与现成 lexical resources 中无法被可靠识别。**

我们想比较的是：

- **semantic-conflict sharing**：两种语言使用完全相同 lexical form，但意义分布发生冲突；
- **semantic-aligned sharing**：两种语言使用完全相同 lexical form，同时意义分布基本一致。

只有这两组都自然存在并可可靠识别，才能把

`shared vs split`

产生的差异解释为“**semantic conflict 是否让 lexical sharing 从 transfer 转为 interference**”。

冻结实现对 EN-DE 数据进行严格 preflight 后得到：

| 阶段 | False friend | 所谓 true friend |
|---|---:|---:|
| 严格 exact-form / single-token 候选 | 65 | 5 |
| 通过自然语料 evidence gate | 24 | 3 |

而存活的 3 个所谓 true-friend control 中：

- `bar`：德语常见义包含“现金 / 裸露”，与英语 `bar` 并非语义对齐；
- `Rock`：德语为“裙子”，与英语 `rock` 不同；
- `intelligent`：是唯一明显干净的同形同义项。

因此严格意义上可用的 semantic-aligned exact-form control 只有约 1 个，远低于预注册最低支持量，也不足以定义稳定的 causal comparison。

这不是一个通过调参数、加 seed 或扩训练规模能够解决的问题。

---

## 2. 原始研究问题为什么一开始看起来成立

项目起点来自一个真实而有吸引力的文献张力：

1. false-friend / cross-lingual homograph 工作显示，同形异义可能导致语言特定的语义判断失败；
2. vocabulary-overlap 工作又显示，跨语言共享 token / lexical form 往往能促进整体 transfer；
3. 因此一个很自然的问题是：

> 同一个共享 lexical form 是否可能在 form level 获益，同时在 semantic level 因意义冲突而付出代价？

为了避免只做 observational benchmark，我们进一步设计了因果干预：

### Shared

`EN exact target -> base row`  
`DE exact target -> base row`

### Split

`EN exact target -> base row`  
`DE exact target -> language-specific alias row`

并把模型大小、参数量、step-0 初始化、训练数据、采样序列、optimizer update、softmax active cardinality 等全部控制一致。

从算法设计角度，这个 intervention 最终已经可以比较干净地回答：

> **共享同一个 lexical row 本身会发生什么？**

但论文真正需要回答的更强问题是：

> **这种影响是否由 cross-lingual semantic conflict 特异性地产生？**

而后者必须依赖一个可信的 semantic-aligned control。最终失败恰恰发生在这里。

---

## 3. 为什么“true cognate”不等于我们需要的 causal control

这是本项目最重要的概念性教训。

### 3.1 Benchmark label 和 causal object 不是同一个东西

StingrayBench 的目标是跨语言 sense / usage evaluation。论文将 true cognates 定义为相似词形且共享意义的词，并且在 EN-DE 中允许 capitalization variation，例如 `arm` / `Arm`。

这对它自己的 benchmark 完全合理：

- 给定某个特定句子；
- 两边都可以构造出该共享意义下的正确 usage；
- 模型需要判断当前上下文中的语义是否合适。

但我们的训练实验不是句子级 benchmark。

我们把自然语料中一个 lexical form 的**所有出现**送入模型。因此真正相关的是：

`P(sense | word, language)`

也就是该词在每种语言中的完整使用分布。

一个词只要存在某个共享意义，就足以成为 benchmark 中的 cognate example；但它未必满足我们 causal control 需要的：

`P(sense | w, EN) ≈ P(sense | w, DE)`。

因此：

> **“true cognate”这个文献类别，不自动等价于“same exact form + matched semantic distribution”这个实验对象。**

这是本项目最根本的 identification mismatch。

### 3.2 EN-DE 的 orthography 条件进一步恶化问题

StingrayBench 对 EN-DE 允许大小写差异。可是我们的 causal intervention 要求**完全相同 surface form / token row**。

例如：

`English arm` ↔ `German Arm`

在 benchmark 语境中可以是共享“手臂”意义的 cognate pair。

但如果为了满足 exact-form intervention，把它拆成 `arm` 这个 surface，然后去德国自然语料中搜索 `arm`，得到的常见词义是德语形容词“贫穷的”。

于是原本的 true cognate 被我们人为转换成了 semantic collision。

这说明 orthographic normalization 不是无害工程处理，而会改变 lexical identity 与语义。

### 3.3 `en_de_common_words.csv` 也无法完成语义核验

冻结执行中进一步检查发现：

- `en_de_common_words.csv` 的 98 行里，`Meaning in L1` 与 `Meaning in L2` 98/98 逐字相同；
- 多行 gloss 实际包含两个语言意义的并集，例如 `arm, poor`、`rock, skirt`、`bar, in cash` 等。

因此这些列不能被当作“两种语言分别经过独立核验的 semantic label”。

它们不能用于证明：

> 两个语言中该 lexical form 的意义分布真正一致。

所以问题不是某一行 parser 写错，而是**resource semantics 与我们的 causal-control semantics 不一致**。

---

## 4. 严格冻结版本实际发生了什么

最终 audit-v2 冻结实现为：

`d055f1e0976b0b5cc2ef3bf681cdd197c5317c97`

服务器端在不修改 `scripts/`、`src/`、`tests/`、`configs/` 的情况下执行：

```bash
python scripts/prepare.py \
  --output data/processed/en_de \
  --max-pairs 1000000 \
  --min-target-occurrences 20

PYTHONPATH=src pytest -q
python scripts/preflight.py --data data/processed/en_de
```

结果：

```text
strict Stingray targets before corpus filters:
  false_friend = 65
  true_friend  = 5

targets after evidence gate:
  false_friend = 24
  true_friend  = 3
```

Preflight 正确返回：

```text
FAIL: only 3 lexical items for true_friend (<10)
PRECHECK FAIL: do not allocate GPUs until fixed
```

`pytest`: **8 passed**。

因此正式冻结实现**没有启动任何 GPU scientific training**。

这个 stop 是正确行为，不是未完成工作：preflight 的目的本来就是在昂贵训练之前发现 causal object / support 不成立。

---

## 5. 先前 10-run 结果为什么全部作废

项目过程中曾经跑过 5 seed × shared/split 共 10 次训练，并得到过机器判决：

`KILL_CORE_FORM_ONLY`

那一批结果**不能作为任何正式科学发现引用**。

有两个独立原因。

### 5.1 实现版本不一致

旧训练使用 commit：

`d8d1b18cf2aa0d2718218775b780adc84f9470a1`

它从较早的 `d8860ba...` 分叉，并没有包含最终 audit-v2 的关键 causal-loss hardening。

尤其缺少最终版的 **one-in / one-out softmax normalization**。

旧 split 模型训练时，base 与 alias 同时处于 softmax 中并互为 negative class；这会人为促进两个 lexical rows 分离。即使 evaluation 后来把 `P(base)+P(alias)` 合并，训练阶段已经发生的梯度污染无法被恢复。

因此旧结果中的强 form benefit 不能解释为 clean lexical-sharing effect。

### 5.2 运行时改变了 true-friend 定义

旧执行第一次严格准备时 true-friend 数量不足。为了通过 preflight，运行时曾把 capitalization-different cognate pair 拆成独立 surface candidates，以增加 control 数量。

这改变了科学对象。

例如 `arm/Arm` 被拆后，小写 German `arm` 不再是原来的“手臂” cognate，而是“贫穷”的另一个词。

因此旧结果的 FF-vs-TF specificity 对照被污染。

### 5.3 旧 FF-only 数字只能作为失败诊断，不是结果

旧无效实现里，24 个 FF 的 diagnostic signal 是：

| 指标 | 估计 | 95% CI | 方向一致性 |
|---|---:|---:|---:|
| `Δpost` | -0.011 | [-0.049, +0.025] | 0/5 |
| `Δlocal_post` | -0.014 | [-0.064, +0.033] | 1/5 |

这会降低我们对核心假设的主观先验，但**不能用于声称假设被实验否定**。

本项目最终没有得到一场可引用的 Gate-1 hypothesis test。

---

## 6. 为什么不继续“补一个 true-friend 数据集”

理论上可以人工或词典式构造一个新 control：

1. 找到 exact same written form；
2. 确认两边 POS 对齐；
3. 确认 dominant sense 对齐；
4. 检查 secondary senses；
5. 检查两种语言中的 sense-frequency distribution；
6. 匹配总词频与 EN/DE frequency imbalance；
7. 匹配 tokenization；
8. 最好进一步匹配 semantic distance / contextual diversity。

这样也许能得到 10–30 个“干净” controls。

但一旦做到这一步，研究已经从：

> “对一个自然现象做快速、直接、可证伪的 causal test”

变成：

> “先建设并验证一个高度定制的 bilingual lexical-semantic control dataset，然后才能开始实验”。

这违背本项目的选题原则。

更重要的是，随着 control gate 增多，我们越来越难判断：

> 研究的是自然存在的重要 computation，还是研究者为了让某个故事可识别而人为制造的实验对象。

因此不继续人工构造 control。

---

## 7. 为什么不只跑 FF-only necessary condition

一个可能的退路是完全放弃 true-friend control，只对 24 个 strict FF 跑：

`shared vs split`

然后看：

`Δpost^FF > 0` 是否成立。

如果它不成立，可以作为 negative diagnostic；但如果它成立，我们仍然无法回答论文最重要的问题：

> 这个 cost 是 semantic conflict 特异性的，还是任何 lexical sharing 都会产生的 generic effect？

没有 non-conflict control，positive result 无法支持原来的 paper-level claim。

因此 FF-only test 对“kill”可能有信息，对“证明”没有足够 identification power。

在已经发现主 causal contrast 无法自然成立后，再为一个只能单向否证的实验投入 GPU 没有足够价值。

所以不跑。

---

## 8. 为什么不立即换语言对

另一条可能路线是换到 exact orthographic overlap 更多的语言对，例如 Indonesian-Malay。

这确实可能改善“完全同形”这一条件，但并不能自动解决更深的 semantic-distribution 问题：

> 一个 benchmark 条目在某个语境下是 true cognate，不代表该词在两种自然语料中的完整 sense distribution 足够一致，可以作为 no-conflict control。

换语言对还意味着重新处理：

- corpus；
- tokenizer coverage；
- lexical frequency；
- semantic control validation；
- data preflight；
- 整套实验复现。

这已经是一个新的研究项目，而不是当前题目的自然修补。

鉴于当前 hypothesis 的先验也被旧 FF-only diagnostic signal 下调，没有足够理由继续追逐这个故事。

---

## 9. 最终失败类型

最终分类：

`CONCEPTUAL_IDENTIFICATION_FAILURE`

不是：

`HYPOTHESIS_REJECTED`

不是：

`ENGINEERING_FAILURE`

也不是单纯：

`INSUFFICIENT_SAMPLE_SIZE`

原因是：

> **我们要操纵的 causal variable 可以编码，但要与之比较的“semantic-aligned shared-form control”无法从当前自然数据 / public benchmark category 中可靠识别。**

如果一个 causal question 的关键 control 不能自然观察或从现成资源中稳定定义，那么即使 intervention 本身非常漂亮，整个 paper question 仍然不可识别。

---

## 10. 这次最重要的研究方法教训

### Lesson 1 — 先验证 causal object，再写训练代码

以后任何 candidate topic，在实现模型 intervention 之前，先做一个最便宜的 **identifiability preflight**：

- treatment object 是否真实存在？
- control object 是否真实存在？
- 两者是否能用现成数据稳定区分？
- 至少随机人工检查 10–20 个 control examples 是否真的满足论文需要的定义？

如果这一步不过，直接 kill。

本题如果一开始就随机检查 `bar`、`Rock`、`arm/Arm`，应当在第一天结束，而不是写完整训练 pipeline 后才发现。

### Lesson 2 — 文献里的类别名称不能直接当 causal variable

“false friend”“true cognate”“common word”都是为某个文献任务定义的类别。

实验需要的对象却可能更严格：

`exact same form + matched semantic distribution`。

两者名字接近，不代表数学上是同一个变量。

以后必须明确写：

**paper label → operational definition → causal estimand**

三者是否真正一致。

### Lesson 3 — Benchmark suitability 要按自己的 estimand 审，不按 benchmark 作者的用途审

StingrayBench 对跨语言 sentence-level semantic disambiguation 是合理资源；它不适合本项目，不代表 StingrayBench 有问题。

错误在于我们把：

> “适合测试当前句子的 cognate understanding”

错误外推成：

> “适合作为自然语料训练中的 matched semantic-distribution control”。

以后复用 benchmark 前先问：

> 它到底标注了我需要的 latent variable，还是只标注了一个相关但不同的 proxy？

### Lesson 4 — Gate 越来越复杂是 topic-quality alarm

严格控制本身不是坏事。

但如果为了证明一个简单 claim，不断需要新增：

- sense matching；
- POS matching；
- frequency matching；
- polysemy matching；
- tokenization matching；
- context matching；
- 人工 semantic audit；

那么要重新判断：

> 是实验终于严谨了，还是研究问题本身并不自然？

本题属于后者。

### Lesson 5 — Preflight 不只检查数量，也要检查语义有效性

这次 preflight 在数量上成功阻止了浪费 GPU，这是正确的。

但未来更早的 topic preflight 还应加入人工/语义层审计：

- control 中抽 10–20 个实例；
- 不看 benchmark 名称，只按论文 causal definition 独立判断；
- 只要出现大量反例，就停止。

### Lesson 6 — 阴性实验、无效实验、不可识别实验必须分开

这三种结论完全不同：

1. **Valid negative**：实验有效，假设没有成立；
2. **Invalid experiment**：实现或数据处理违反设计，结果不可引用；
3. **Identification failure**：连能够裁决假设的 treatment/control 对象都无法可靠定义。

本项目最终属于第 3 类；旧 10-run 属于第 2 类。

不要把它们写成第 1 类。

---

## 11. 哪些工作仍然是有效资产

虽然题目归档，以下工程工作仍然正确并可作为未来项目参考：

- exact lexical-occurrence mask；
- pair-level parallel holdout；
- shared/split step-0 tensor identity；
- alias/base one-in-one-out softmax normalization；
- optimizer-update semantics；
- deterministic paired sampling；
- word × seed crossed bootstrap；
- frozen data/config/code/init provenance；
- no-Slurm、one-idle-GPU-per-run 的独立任务执行方式；
- fail-fast preflight philosophy。

这些代码留在仓库中作为**历史实验基础设施**，但仓库不再处于 active research 状态。

---

## 12. Reopen 条件

默认**不 reopen**。

只有出现以下情况才值得把这个问题重新视为新 candidate topic：

1. 出现一个现成公开资源，能够直接提供足量（至少约 10–20 个）**exact same surface + independently verified semantic-aligned** bilingual lexical controls；
2. 不需要我们自己建设大规模 semantic-control dataset；
3. treatment 与 control 在自然语料中仍有足够频次；
4. 可以在开始训练前用一个很小的人工 audit 明确验证 causal contrast；
5. 同时有新的理论 / empirical evidence 显著提高“sharing 会产生 conflict-specific semantic cost”的先验。

否则不要重新打开本项目。

---

## 13. 最终停止决策

**Final decision**：

`ARCHIVED — CONCEPTUAL_IDENTIFICATION_FAILURE`

- Gate 1：未获得有效科学裁决；停止。
- Gate 2：取消。
- Gate 3：取消。
- Hidden-state probes / steering / mechanism experiments：取消。
- `gate1_full.yaml`：不运行。
- 新 GPU 预算：0。
- 旧 `KILL_CORE_FORM_ONLY`：永久标记为 invalid，不得引用为科学结果。

本项目最值得保留的结论不是关于 false friends，而是关于选题方法：

> **在把一个漂亮的现象张力变成实验之前，必须先证明 treatment、control 与 causal variable 在真实数据中是自然、稳定、可识别的。否则后面越精致的 intervention 和统计，只是在一个不存在的对照上做精确工程。**
