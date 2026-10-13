# 第四轮完整证据：Romance、关系对象与目标范围

16个COMPLETE运行，21,424条自然生成。[研究判断与完整结果](../../knowledge/notes/ROMANCE_SCOPE_CYCLE_RESULTS_2026-10-13.md)，[四轮进展总览](../../knowledge/notes/CURRENT_PROGRESS_2026-10-13.md)。

| 运行前缀（2026-10-13） | 模型 | 每模型生成 |
|---|---|---:|
| romance-baseline- | Llama8B、Qwen14B、Qwen32B、Gemma12B | 1,598 |
| romance-exploration- | 同上 | 2,468 |
| lexical-proposition- | 同上 | 768 |
| gloss-binding- | Llama8B、Qwen14B | 180 |
| scope- | Qwen32B、Gemma12B | 864 |

每个运行目录保存manifest、压缩逐生成记录/冻结spec、模型输出token、汇总、原始文件SHA256和执行代码快照。`summary.json`含严格首答、two-shot显式Label敏感性读出、source/polarity/factorial分层与族级bootstrap；范围目录另存配对记录与新/已探索族。`archive_manifest.json`登记归档文件hash、总数与分析代码版本。所有原输出hash和两个执行代码hash已核验，冻结spec与生成prompt逐行一致。

## 来源与限制

Romance来源：[作者仓库](https://github.com/mrtva/false-friends-vs-cognates)，revision `a87b73e387a6ef86d0cef7ffe703150905e75d7a`；[ACL2026论文](https://aclanthology.org/2026.acl-long.1818/)。源目录未发现LICENSE，因此原句和包含源句的prompt不整包再发布。相关记录保留W1/W2、源文件/行号、R及文本/prompt hash，模型生成完整保留；原文可从固定source revision在本地重建。自写职业、状态词、范围材料保留完整prompt。

`source_audit.json`登记六个TSV hash；auto-es-pt与human-es-pt方向不同。原R只定义语境词义等价，不自动提供新释义gold。作者细分类字段不在TSV，未补造它们。

Llama/Qwen14初轮各180条释义评读有单Agent非盲标记；GL bailado一方向预标含糊。其他释义及明确目标追加尚未完成全量语义审核。所有未响应、错目标、截断和负分支保留，不用字符串差异代替词义变化。

## 重算

`analysis_code/`保存使用的分析、构造、归档及执行脚本。压缩JSONL用标准gzip读取；例如在仓库根目录：

明确目标词追加的构造助手在运行后补存为`build_gloss_explicit_binding.py`，已对原180条冻结spec逐字节重建核验；没有把这个补存文件伪称原执行快照。原模型执行的两个代码快照与hash保持不变。

```python
import gzip, json
from pathlib import Path
from scripts.analyze_romance_cycle import summarize

path = Path('evidence/2026-10-13-romance-scope/2026-10-13-scope-qwen32b/generations.jsonl.gz')
with gzip.open(path, 'rt', encoding='utf-8') as stream:
    records = [json.loads(line) for line in stream]
result = summarize(records)
```

词对层级为Romance的语言标记词对族；职业24词形成12关联对；状态/范围按互补词族聚合。bootstrap 4000次、seed20261013。多个任务/极性/顺序/同族句源是重复测量。比较不同范围的正确率并非同一gold下的修复效果，须同时查看gold相反时的响应配对。

当前没有本地activation干预或内部机制结论；高格式解析率也不能认证解释正确性、语义标注或论文贡献。
