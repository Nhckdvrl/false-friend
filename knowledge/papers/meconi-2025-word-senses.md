# Meconi 等 2025 — 自由释义与有限义项选择的证据距离

Domenico Meconi, Simone Stirpe, Federico Martelli, Leonardo Lavalle, Roberto Navigli. *Do Large Language Models Understand Word Senses?* **EMNLP2025主会**，33897–33916。[正式条目](https://aclanthology.org/2025.emnlp-main.1720/)、[PDF](https://aclanthology.org/2025.emnlp-main.1720.pdf)、[代码入口](https://github.com/Babelscape/LLM-WSD)。2026-10-13，**S2**：定向§3误例审查、§4及Table8–11、§6Limitations；未穷尽全部WSD提示表或审计代码。

## FACT

作者比较英语WSD和定义、自由释义、例句生成。生成评估采用Llama3.3-70B与GPT-4o，由专家评分并在100项目子集加入第二评审。自由释义允许good/bad/borderline，未把含糊回答自动计对；Table9的最高98%不是所有数据和模型都98%。例句生成有重复原结构和真正错义两类。全部实验为英语，作者承认提示敏感性。[原文](https://aclanthology.org/2025.emnlp-main.1720.pdf)

## Idea Genesis / Experimental Reasoning INFERENCE

可重建的缺口是：有限WordNet选项选错，究竟是不懂词义，还是规定粒度/候选限制了表现？允许模型用自己的语言表达、再评估例句，是检验“同一失败在另一任务中是否仍存在”的思路。但任务、评价尺度和成功标准一起改变，不是只干预了候选约束的纯因果实验。自由解释正确提供另一访问路径，不自动保证下游推断会使用该义。

对本轮结果尤其有用：独立解释只说“这是句子的主语”或重述原句，不能算意义访问成功。例句结构相同也不应与错义混为一类。我们已经把这两种情况与明确竞争义分开标记。

## Nearest Related Work Distance

“WSD分数低但自由释义好”已由主会论文充分讨论，单把这一差异搬到日中词不够。本项目更有价值的候选增量是：同一实例中，独立访问与联合语义使用之间何时不一致，能否由目标绑定、任务读出或粒度解释，并在新词族作出预测。当前尚无这种机制结论。AM2iCo提供目标更换对照；若独立解释本身不支持目标义，优先保留知识/识别不足解释。
