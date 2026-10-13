# 持久化证据：原始结果与解释边界

最新：[第四轮16个完整运行](2026-10-13-romance-scope/README.md)，21,424条自然生成；四模型Romance原任务、旁例、不同语义关系及目标范围，保留新词族预测、失败测量与未全量语义审核状态。[第四轮判断变化](../knowledge/notes/ROMANCE_SCOPE_CYCLE_RESULTS_2026-10-13.md)，[四轮总览](../knowledge/notes/CURRENT_PROGRESS_2026-10-13.md)。

第三轮：[AM2iCo 10个完整运行](2026-10-13-am2ico/README.md)，10368标签试次、2256生成；三模型真实文本目标对照、任务标准、释义与匹配目标列表追加。包含失败设计和后验Agent评读，尚无内部机制结论；[判断变化](../knowledge/notes/AM2ICO_CYCLE_RESULTS_2026-10-13.md)。

第二轮：[输出语言第二轮完整证据](2026-10-13-output-language/README.md)，三个模型初轮及两个模型完整回答追加，共5184标签试次、1824自由生成，16词族重复测量。自写原文与prompt完整保留，单Agent评读不是人类gold；[判断变化](../knowledge/notes/OUTPUT_LANGUAGE_CYCLE_RESULTS_2026-10-13.md)。

第一轮：[2026-10-13本地研究证据](2026-10-13-local-cycle/README.md)，包含Llama8B/Qwen14B原任务复核、新诊断、自由输出、逐例Agent评读和工程失败。研究判断见[研究更新](../knowledge/notes/LOCAL_RESEARCH_UPDATE_2026-10-13.md)。新标签与评读不是独立人类审核，没有内部机制结论。

下面保留此前GitHub Actions附件的小模型历史结果；没有覆盖或重新人工审核这些旧词义标签。

## 可复查资产

[36个评分记录](2026-10-12-cpu-pilots/score_matrix.json)按列保存：`source_id, host_language, cue, correct_as_a, logp_A, logp_B, correct_minus_foil_margin`。三个词ID261/genial、264/blank、272/stark，全部为高语义约束；模型Qwen2.5-1.5B-Instruct，checkpoint/tokenizer `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`。记录的是完整词表归一化下两个选项token的log概率，不是潜在词义后验。

[原六次生成](2026-10-12-cpu-pilots/generation_outputs.json)是Qwen2.5-0.5B-Instruct、checkpoint `7ae557604adf67be50417f59c2c2f167def9a775` 在source ID180/brand上的程序试跑。含明显目标词误认与德语名词大小写风险，不可用于语义机制推断。

[来源、版本和哈希](2026-10-12-cpu-pilots/provenance.json)保留原zip/member哈希、原运行/代码版本及重新构建输入所需来源。为了避免未经许可复制第三方语料，持久副本不整包再发布原句和词典定义；保留逐例ID、prompt哈希、模型输出和数值，按固定source/code版本重建。

## 正确权重

18组成对条件中7组单顺序语义偏好符号改变，14组两顺序差异超过2 nats。它们说明必须检查读出偏置，却不能单独推翻平衡选项估计。固定A/B偏置在双顺序均值中可以抵消；内容×顺序交互以及独立语义结果才是下一步问题。

全部双顺序均值为正，只能描述这三个手选词/这个小模型/这组未独立审核的定义，不能宣称原论文方向效应已被否定。完整历史分析见 [PILOT_FINDINGS](../experiments/PILOT_FINDINGS_2026-10-12.md)。

后续科学运行须用不同run目录、保留词汇族、源样本/派生标注版本、完整prompt与失败，不覆盖本记录。CI会校验保留数值的哈希与重新计算的诊断统计；它不证明原数据的语义有效性。
