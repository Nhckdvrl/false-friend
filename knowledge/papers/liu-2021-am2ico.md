# Liu 等 2021 — AM2iCo：指定目标与整段主题的区分

Qianchu Liu, Edoardo M. Ponti, Diana McCarthy, Ivan Vulić, Anna Korhonen. *AM2iCo: Evaluating Word Meaning in Context across Low-Resource Languages with Adversarial Examples*. **EMNLP2021主会**，7151–7162。[正式论文](https://aclanthology.org/2021.emnlp-main.571/)、[PDF](https://aclanthology.org/2021.emnlp-main.571.pdf)、[作者资源](https://github.com/cambridgeltl/AM2iCo)。2026-10-13，**S2**：§§2–3及§4对抗/删减输入分析、Table7/8定向阅读；未穷尽迁移实验或复现训练。作者仓库已核README、许可和三语言TSV，revision见实验设计。

## FACT

任务比较跨语言目标词是否指同一实体/概念；Wikipedia链接提供标签，启发式减少粒度争议。人工只抽查部分实例。对抗负例在同一语境中改标相关词，约占数据四分之一。作者以mBERT/XLM-R及训练分类器评估，另训练context-only/target-only基线；不是聊天LLM提示实验。Table7中对抗例增大full与删减输入的差距。[§§2–4](https://aclanthology.org/2021.emnlp-main.571.pdf)

## Idea Genesis 与实验逻辑 INFERENCE

可重建的推进是：模型在WiC分数高，可能来自真正的词义—语境组合，也可能只来自句子主题或词本身。删除输入发现替代策略仍强，于是在语境不变时改变关注对象，使主题策略作出错误预测。这一步的贡献是改变哪些策略能成功，不只是让数据更难。此重建不是作者自述。

但“full领先删减输入”仅排除相应基线的充分性，不足以宣布深层语义理解。训练输入不同会改变分布和优化；对抗负例也可能被目标词不相似识别，需看词级baseline。最有信息量的是同一文本内原词和改标词的逐对决定，而不是一个总分。

## 最近邻距离 / 本项目使用

不能把“目标词换了，模型仍看主题”称为首次发现。我们需要检查它是否在有能力生成模型上仍发生；若发生，进一步问**独立识别了两个指称，却在联合比较时未使用它们**是否成立，并排除标签/粒度错误。独立释义不正确会削弱使用缺口解释；释义正确也不证明内部天然模块分离。

本地预审见到王/Norway的可疑T标签，说明链接跨度和自然词义未必同一对象。保留来源标签作baseline，争议例另列，不事后强行把模型合理答案判错。第三轮只做[目标绑定探索](../notes/AM2ICO_TARGET_BINDING_DESIGN_2026-10-13.md)，不据当前代码宣称已复现论文结论。
