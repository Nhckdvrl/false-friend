# Gate 1 状态报告：冻结实现下无法运行

**日期**：2026-08-21
**代码**：`d055f1e`（audit-v2 最终冻结实现，未作任何修改）
**结果**：**preflight FAIL，未分配 GPU**
**先前那批结果的判决**：`INVALID_GATE1_IMPLEMENTATION_MISMATCH`

---

## 1. 结论

用最终审计冻结的实现严格执行 Gate 1 数据准备，真朋友对照组只剩 **3 个词**，低于预注册要求的 10 个。`scripts/preflight.py` 返回：

```json
{
  "status": "FAIL",
  "relation_counts": { "false_friend": 24, "true_friend": 3 },
  "problems": ["only 3 lexical items for true_friend (<10)"]
}
```

```
PRECHECK FAIL: do not allocate GPUs until fixed
```

按仓库规则「preflight 失败则不得分配科学 GPU」，**本次没有启动任何训练**。Gate 1 在当前对照集下**不可裁决**，Gate 2 / Gate 3 自然也不启动。

---

## 2. 先前那批结果为何作废

在此之前曾有 10 次训练（5 seed × shared/split）跑出 `KILL_CORE_FORM_ONLY`。**该判决无效**，两个独立的致命问题：

### 2.1 跑错了版本：缺少 one-in/one-out softmax

那批训练的 commit `d8d1b18` 不是 `d055f1e` 的后代。二者的 merge base 是 `d8860ba`，`d8d1b18` 落后最终版 24 个 commit。

旧训练代码直接用普通 GPT-2 交叉熵：

```python
loss = model(input_ids=batch, labels=batch, use_cache=False).loss
```

base 行与全部 alias 行同时存在于 softmax 中。而最终审计版实现了 `apply_causal_vocab_mask()`（`src/false_friend_lab/remap.py`），每个位置 active class 数恒为 `base_vocab_size`：

- shared：全部 alias 屏蔽；
- split 的 DE exact target：对应 alias 放进来，配对的 base 行屏蔽掉（one-in / one-out）。

后果：旧 split condition 中 base 与 alias 互为 negative class，英语位置 `base↑ alias↓`、德语位置 `alias↑ base↓`，等于人为施加了一个把两个词汇行推开的额外训练信号。因此旧结果中那个「非常强、5/5 种子一致」的 form benefit（`Δsurface = −0.144`）**至少部分可能来自 duplicate-output competition**，而不是共享表征本身提高了形式预测。评估阶段把 `P(base) + P(alias)` 相加救不回训练期已经被污染的梯度。

### 2.2 对照组的科学定义在运行中被改动

第一次严格准备得到 24 FF / 4 TF，按预注册应当输出 `INCONCLUSIVE_INSUFFICIENT_LEXICAL_SUPPORT`。当时为了让 preflight 变绿，修改了目标提取逻辑：把 `arm` / `Arm` 拆成两个独立的候选词形分别去语料里找，从而把真朋友数量凑到 16。

**这个修改是错的。** 拆分在假朋友臂保语义（`angel` / `Angel` 拆开后两个仍然都是假朋友），但在真朋友臂破语义：德语自然语料中的小写 `arm` 是形容词「贫穷的」，与英语 `arm`（手臂）不是同一个词位。这等于亲手造出一个假朋友放进对照组。同批混入的还有 `Labor`、`fallen`、`costs`、`log`、`dance` 等。

StingrayBench 原论文允许 EN-DE 存在大小写差异（`arm`-`Arm`），对该 benchmark 没有问题；但本项目的因果问题是 **exact same lexical form / same token row sharing**，两个定义不一样。该修改已完整回退，当前 `scripts/prepare.py` 与 `d055f1e` 逐字一致。

---

## 3. 严格定义下对照组的真实规模

| 阶段 | 假朋友 | 真朋友 |
|---|---|---|
| 严格单 token 候选 | 65 | **5** |
| 通过语料证据门槛（EN/DE 各 ≥20 次） | 24 | **3** |

存活的 3 个真朋友，以及 StingrayBench 给出的词义 gloss：

| 词 | gloss | EN 计数 | DE 计数 | 语义判断 |
|---|---|---|---|---|
| `bar` | bar, **in cash** | 871 | 165 | 德语 `bar` = 现金/赤裸 → **语义上是假朋友** |
| `Rock` | rock, **skirt** | 254 | 312 | 德语 `Rock` = 裙子 → **语义上是假朋友** |
| `intelligent` | intelligent | 176 | 71 | 干净 |

**3 个对照词里只有 1 个语义上真正成立。**

---

## 4. 更深一层的问题：对照集本身不适配

这不是提取逻辑的 bug，回退修改也解决不了。核查 `data/en_de_common_words.csv` 发现：

- **98 行中 `Meaning in L1` 与 `Meaning in L2` 全部逐字相同**（98/98）；
- 其中 9 行的 gloss 含逗号，形如 `arm, poor`、`rock, skirt`、`bar, in cash`、`log, lied`、`costs, taste`、`bug, bow [of a ship]`。

也就是说，这两列并不是「各语言各自的意思」，而是**两种语言词义的并集 gloss 被复制进了两列**。该文件因此**无法用于验证语义同一性**。

后果：`en_de_common` 是一个「共享/同源词形」列表，不是经过语义核验的「同义词」列表。无论用哪种提取方式（严格的 `a == b` 也好、拆分词形也好），它都会把两种语言含义不同的词放进真朋友臂 —— 严格版留下的 `Rock` 和 `bar` 就是现成的例子。

**结论：FF-vs-TF specificity 这一项，用 StingrayBench 的 `en_de_common` 作对照，无论如何提取都无法裁决。**

---

## 5. 存活的 24 个假朋友

假朋友臂本身是健康的，24 个词全部通过证据门槛：

`Angel` `bald` `bad` `Bad` `Island` `Lab` `Promotion` `heart` `kind` `Kind` `build` `Bild` `eye` `fast` `art` `Art` `bat` `become` `Brief` `die` `Fund` `half` `hat` `hell`

留出上下文：假朋友 EN 1843 / DE 970；真朋友 EN 119 / DE 48。评估上下文共 2980 个，OOV 比例 0.015%。

---

## 6. 一个仍然值得记录的诊断信号

以下数字**来自无效的旧实现，不构成正式发现**，仅作为先验参考。

在 24 个假朋友自己身上（不依赖被污染的对照组）：

| 指标 | 估计 | 95% CI | 种子一致性 |
|---|---|---|---|
| `Δpost` | −0.011 | [−0.049, +0.025] | 0/5 |
| `Δlocal_post` | −0.014 | [−0.064, +0.033] | 1/5 |

核心假设的**必要条件**是 `shared FF → semantic/contextual cost`，即 `Δpost > 0`。旧实现下不但没看到，方向还是反的。

需要注意的是，旧的 softmax bug 在 split 条件下人为促进了两个词汇表征的分离，如果语义分离确实有价值，这本该**帮助**我们观察到 `Δpost > 0`；结果却是 0/5 种子。这是一个保守方向的论证，会降低对核心假设的信心。

但强度应当收窄：旧 bug 对 `Δsurface` 的污染是**一阶**的（直接作用于目标位置的输出分布），对 `Δpost` 的影响是**二阶**的（须经表征学习传导）。因此这个信号中等强度，不足以单独定案。

无效结果的完整产物已归档在服务器本地 `runs_preauditv2_archive/`、`results_preauditv2_archive/`，未纳入版本库。

---

## 7. 环境与执行记录

### 环境

复用服务器已有 conda 环境 `fgvd`，通过 `--system-site-packages` venv，只把缺失的 `datasets`、`pandas` 装进 venv，不污染共享环境。

- `torch 2.11.0+cu130`，`transformers 5.12.1`，`datasets 5.0.1`，Python 3.12.13

### 本次实际执行

```bash
python scripts/prepare.py --output data/processed/en_de --max-pairs 1000000 --min-target-occurrences 20
PYTHONPATH=src pytest -q          # 8 passed
python scripts/preflight.py --data data/processed/en_de   # FAIL
```

- 代码：`scripts/` `src/` `tests/` `configs/` 与 `origin/main` (`d055f1e`) 逐字一致，无任何本地改动。
- 数据指纹：`2301fe60a6ca10b2d83b538cf1190d89515c10dd3863f8e4785dde823b000c0c`
- schema_version 3，compact_vocab_size 55283，留出平行句对 20411。

### GPU

**本次未分配任何 GPU。** preflight 失败即停止，符合仓库规则。

先前无效的那 10 次运行使用过 `fvcrc20:0-3` 与 `fvcrc21:0-3`（`NVIDIA RTX PRO 6000 Blackwell Max-Q`，启动前均确认空闲），现已全部退出，8 张卡均已释放回 15–18 MiB / 0%，无残留进程占用显卡。fvcrc10/11/12/13/15 当时被其他用户占用，全程未触碰、未 kill 任何进程。

---

## 8. 当前阻塞点

Gate 1 要能裁决，必须先解决真朋友对照组。这是一个需要人来定的科学决策，不应由运行时自行改动筛选规则（上一次正是这样出的错）。

可选方向（均属新的预注册范围，不在本次执行内）：

1. **建立经语义核验的真朋友对照集** —— 离开 `en_de_common`，逐词人工/词典核验德英确为同义且拼写完全一致，凑够 10 个以上；
2. **只裁决 FF-only 必要条件** —— `Δpost^FF > 0` 不依赖对照组，若必要条件不成立即可 kill；此路需要显式修改预注册的判决口径；
3. **接受 Gate 1 在 EN-DE 上不可裁决** —— 记录为数据/设计层面的结果，考虑换语对。

在做出决定之前，不启动任何 GPU 运行。
