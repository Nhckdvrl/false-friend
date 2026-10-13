# 输出语言 × 词义选择 × 规则应用：完整证据

2026-10-13，三个模型完成初轮；两个模型完成原prompt自由生成追加。研究结论与范围见[结果笔记](../../knowledge/notes/OUTPUT_LANGUAGE_CYCLE_RESULTS_2026-10-13.md)。

本目录五个run均为COMPLETE，包含自写原始材料、全部prompt及其chat渲染、full-vocabulary label logp、非响应/截断、模型输出、执行代码快照、model/tokenizer revision、chat template参数、环境、资源和原始文件hash。共5184标签试次、1824自由生成；这是重复条件计数，不是独立词汇样本数。

- `output-language-*`：每模型1728标签、96生成，288生成均有逐例单Agent非盲评读。Qwen3-32B明确关闭thinking。
- `output-readout-*`：同一题目全部非masked规则提示，每模型768生成；`answer_audit.jsonl`区分限定首token与完整初答，冲突保留为null。
- `raw_provenance.json`：原始路径及本目录文件sha256。自写语料允许完整保留；没有复制Doppelganger/AM2iCo原始语料到此目录。
- `analysis_code/`：本次分析程序及共享bootstrap函数的快照；分析不具有人工语义审核的效力。

重建输入使用仓库中的`build_output_language_cycle.py`和`run_output_language_cycle.py`；执行参数在各manifest。再次运行应使用新目录，不覆盖原run。完整初答解析将多代码第一段保守视为conflicting，不能把正确首字母等同完整推理正确。

目前主要结论是限定首token漏掉部分德语自然回答路径，以及两种强Qwen模型在明确语境下的稳定性。没有语言特定知识门控机制、独立确认结果或论文贡献声明。
