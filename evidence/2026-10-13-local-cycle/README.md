# 2026-10-13 本地研究证据

科学解释与边界见[研究更新](../../knowledge/notes/LOCAL_RESEARCH_UPDATE_2026-10-13.md)，设计见[执行前方案及追加纠正](../../knowledge/notes/INITIAL_LOCAL_CYCLE_2026-10-13.md)。此目录保存原始数值的版本化副本；源语料完整输入保留在本地 `runs/`，不整包发布第三方词典/题库。

每个模型目录包含原始candidate NLL及分解、空输入NLL、逐位置完整词表label logp、生成文本/token及截断、model/tokenizer/source/code版本、统计、局部Agent评读及所有raw文件hash。`trials.jsonl`的源句/候选已替换成hash；不能将这些hash当作可单独运行的题库。`code_snapshot.py`是对应实际执行版本，当前scripts可能已有后续修正。

源数据：`https://github.com/0017-alt/Doppelganger-JC`，commit `eb1c4f3f17403af238046bf218dc49643bc2e2e2`。版本化builder从固定源仓库恢复材料；source/input的hash在manifest与raw_provenance中。模型来自本地缓存，不认证Llama镜像与Meta原权重的逐字节一致性。

复核和重建入口（使用已有conda环境，非系统Python2.7）：

```bash
/home/xiang/miniconda3/envs/verl-clean/bin/python -m scripts.build_doppelganger_followup_v1
/home/xiang/miniconda3/envs/verl-clean/bin/python -m scripts.build_doppelganger_followup_v2
/home/xiang/miniconda3/envs/verl-clean/bin/python -m scripts.build_semantic_category_controls
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/analyze_doppelganger_diagnostics.py runs/2026-10-13-doppelganger-llama8b runs/2026-10-13-doppelganger-qwen14b-v2
/home/xiang/miniconda3/envs/verl-clean/bin/python -m pytest -q
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/check_knowledge.py
```

新source clone放到 `data/raw/Doppelganger-JC` 后，须checkout上述SHA；runner验证原版本。运行命令/资源配置见相应manifest，原文源prompt通过 `scripts/audit_doppelganger_source.py` 核对。

包含Qwen首次`FAILED_VERIFICATION_BEFORE_SCORE_WRITE`记录；这是工程中断，不是负科学结果。新实验含歧义原句/null gold，不把它们计入准确率。报告样本数以词族为单位；Agent评读不是人类gold；原协议分数不是内部机制证据。

目录中的 `semantic-v2-*` 为明确意义最小对，`category-control-*` 为检查设备分类失败的后验普通词对照；`pair_summary.json`保留整对成功与全词表格式审计。`semantic-followup-*` 是此前v1，不与v2混为同一冻结协议。v1/v2的原句和派生材料按builder重建；category-control材料为本地新写。
