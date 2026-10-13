# AM2iCo 真实文本目标关系诊断：完整证据

2026-10-13，10个COMPLETE运行；10368标签试次、2256自由生成。三模型初轮与标准追加，两个Qwen释义加回及目标列表纠正。主样本192原文配对、384来源项目、188英语词形族；提示与生成是重复测量，不是独立n。

[研究判断、结果表与局限](../../knowledge/notes/AM2ICO_CYCLE_RESULTS_2026-10-13.md)。这是不同模型与协议下的新诊断，不是原编码器训练结果的忠实复现，也不是全基准成绩。源标签一致率不是独立人类审核准确率。

## 来源与修改

Qianchu Liu, Edoardo M. Ponti, Diana McCarthy, Ivan Vulić, Anna Korhonen. AM2iCo, EMNLP2021。[论文](https://aclanthology.org/2021.emnlp-main.571/)、[作者仓库](https://github.com/cambridgeltl/AM2iCo)，revision `2003865050bc9a9e84f2bcb4979f03734bddab28`。本目录保留作者[README](SOURCE_README.md)与[CC BY4.0许可](SOURCE_LICENSE.md)。仅保存已选记录与派生prompt，没有重新发布整个语料库。

改动为固定hash取样、同原文T/F配对、聊天LLM提示、目标删减、任务定义和释义/目标列表输入条件；原记录、标签、源行号和文件hash保留。后验Agent评读另文件标记，不改原标签。原释义加回含目标列表不对称，后续纠正运行保留它作为失败设计，详见[设计记录](../../knowledge/notes/AM2ICO_TARGET_RESTATEMENT_DESIGN_2026-10-13.md)。

## 目录

| 运行前缀（均2026-10-13） | 模型 | 标签/模型 | 生成/模型 |
|---|---|---:|---:|
| am2ico- | Llama8B、Qwen14B、Qwen32B | 1536 | 240 |
| am2ico-criterion- | 同上 | 1536 | 192 |
| am2ico-gloss- | Qwen14B、Qwen32B | 576 | 288 |
| am2ico-target- | Qwen14B、Qwen32B | 0 | 192 |

每个目录含manifest、完整选中items、trial/generation specs及输出、prompt/输出token IDs、分数（适用时）、summary、代码与评分器快照。`raw_provenance.json`列出原文件路径和逐文件SHA256；模型/tokenizer revision在manifest。部分目录含逐例后验`selected_case_agent_review.jsonl`，没有独立人类金标或总体错误率认证。

`analysis_code/`保存分析脚本与hash，可重算paired decisions、criterion contrasts、自然首答与极性一致性。按词形族bootstrap而非按prompt，原seed与重复次数见代码。脚本中的parent_run首先指本机原run；目标重申分析也支持同层归档目录回退。`archive_manifest.json`登记完整性检查、总数与分析版本。

## 解释限制

Qwen32B在释义追加中478/576次首token argmax不在Yes/No，主要先输出Markdown符号，限定标签分数不代表自然回答。匹配加回结果以实际生成初始明确答案为准；五输入条件×两模型的960回答均可解析，但356段达到128token限制，不把首答分数叫作完整解释准确率。same/different问句是极性对照，不是AB位置交换；平均分掩盖的语义决定不一致另报。

原始训练集标签有跨度、实体和意义粒度争议，后验评读保留这些不利实例。释义固定只说明外部提示内容固定，不证明未干预模型自然使用同一表征。当前没有新内部机制或已确认论文idea。
