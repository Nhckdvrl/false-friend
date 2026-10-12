# 持久化证据：历史试跑，不是机制结论

这里把此前只留在会过期的GitHub Actions附件中的小模型结果保存在当前工作空间。没有在本轮新增模型实验，也没有重新人工审核其词义标签。

## 可复查资产

[36个评分记录](2026-10-12-cpu-pilots/score_matrix.json)按列保存：`source_id, host_language, cue, correct_as_a, logp_A, logp_B, correct_minus_foil_margin`。三个词ID261/genial、264/blank、272/stark，全部为高语义约束；模型Qwen2.5-1.5B-Instruct，checkpoint/tokenizer `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`。记录的是完整词表归一化下两个选项token的log概率，不是潜在词义后验。

[原六次生成](2026-10-12-cpu-pilots/generation_outputs.json)是Qwen2.5-0.5B-Instruct、checkpoint `7ae557604adf67be50417f59c2c2f167def9a775` 在source ID180/brand上的程序试跑。含明显目标词误认与德语名词大小写风险，不可用于语义机制推断。

[来源、版本和哈希](2026-10-12-cpu-pilots/provenance.json)保留原zip/member哈希、原运行/代码版本及重新构建输入所需来源。为了避免未经许可复制第三方语料，持久副本不整包再发布原句和词典定义；保留逐例ID、prompt哈希、模型输出和数值，按固定source/code版本重建。

## 正确权重

18组成对条件中7组单顺序语义偏好符号改变，14组两顺序差异超过2 nats。它们说明必须检查读出偏置，却不能单独推翻平衡选项估计。固定A/B偏置在双顺序均值中可以抵消；内容×顺序交互以及独立语义结果才是下一步问题。

全部双顺序均值为正，只能描述这三个手选词/这个小模型/这组未独立审核的定义，不能宣称原论文方向效应已被否定。完整历史分析见 [PILOT_FINDINGS](../experiments/PILOT_FINDINGS_2026-10-12.md)。

后续科学运行须用不同run目录、保留词汇族、源样本/派生标注版本、完整prompt与失败，不覆盖本记录。CI会校验保留数值的哈希与重新计算的诊断统计；它不证明原数据的语义有效性。
