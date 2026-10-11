# BIA+：从词形识别到任务决定的分离（理论卡）

**Primary**: Dijkstra & van Heuven, *The architecture of the bilingual word recognition system: From identification to decision*, *Bilingualism: Language and Cognition*, 2002. [Publisher / DOI](https://doi.org/10.1017/S1366728902003012). **阅读深度**：S3（官方摘要、背景论文讨论；原文全文本轮未获取），不得冒充作者原文全部细节。

## 为什么会出现 BIA+？（INFERENCE，结合摘要与 BIA 历史）

旧 BIA 描述跨语言非选择性词形激活，但仅有字形竞争不能解释语音/语义、任务规则和句子上下文所造成的种类不同的效应。BIA+ 通过拓展多层 lexical representation，同时**区分 identification system 与 task/decision system**，避免把“按哪种语言作答”的任务控制直接等同于词汇识别。

**尺度**：这是对已有双语词汇识别理论的理论结构扩展，非一个评测指标。它重要的是拆解解释，非预言所有同形异义词都会慢。

## 对当前模型研究启发

- 实验上区分：语言归属识别；当前上下文中的 sense recognition；按照指定目标语言生成词形/翻译。
- 错误可能停在识别层，也可能发生在答案/任务选择层；仅终端正确率无法识别。
- 语言文字本身提供的句法/语义约束和外部任务说明是不同可操纵变量。
- 可以设计同一句子、同一个目标意义，在不同输出任务（sense MCQA / paraphrase / translation）下的 crossed contrasts。

## 重要的拒绝推论

BIA+ 是关于**人类读词过程**，有真实反应时与神经行为数据；标准 decoder-only Transformer 不等于级联的人类词汇识别网络。不能凭 probe 出来某个语言 logit 就命名“language node”，也不能称模型内部竞争是人类眼动干扰的同构。

## 可转成竞争假设的测试

H-identification：同一个目标语境在不用生成目标词、只做二选一意义任务时也经常出错。
H-decision：意义任务稳定正确，只有要求改变输出语言/复制原词时错误。
**强对照**：多种任务验证语义；不是用输出 “room/cream” 单个 verbalizer 定性。

**Related work 距离**：Tanwar 已继承双语 lexical access 框架，Doppelganger 已做多任务，Dumas/Körner 已能分别改变概念与输出语言。要新颖，须再提出被这些论文忽略的、可预测的**内部/任务阶段关系**。这是 S1/S2 论文阅读的来源追踪，不是空白声明。
