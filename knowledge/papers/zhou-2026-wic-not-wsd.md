# Zhou 等 2026 — WiC粒度、知识与比较：本轮最接近的新工作

Yi Zhou, Kiamehr Rezaee, Danushka Bollegala, Mohammad Taher Pilehvar, Jose Camacho-Collados. *WiC is Not WSD: A Study on LLMs and Lexical Ambiguity Resolution*. [arXiv v1](https://arxiv.org/abs/2609.20593)、[HTML](https://arxiv.org/html/2609.20593v1)。2026-09-17发布；arXiv comments由作者报告Accepted to AACL2026(main)，此处未据正式会录独立核验，不称ACL/EMNLP/NAACL主会论文。2026-10-13 **S2**定向读§§4–6、Table1–5、Limitations；未核代码、未穷尽附录或视觉核Fig2。

## FACT

英语实验比较WiC有/无义项、有/无CoT、WSD及用两个WSD结果外部比较得到WiC。粗粒度来自20词；细粒度另由WordNet构造。提供义项平均改善，但Table3的Mistral小模型CoT条件存在反例，不是每模型每条件都改善。作者承认义项同时提供语义信息。人工只抽查模型错误，先重标原题再看输出；报告粒度分歧、错误识别、错误决定等。分解收益依模型而异，不能当普遍原理。[§§4–6](https://arxiv.org/html/2609.20593v1)

## Idea Genesis / Experimental Reasoning INFERENCE

可重建的链条：WiC低分但WSD较好→可能缺少语义知识，也可能缺少应使用的区别标准，或比较本身困难→补充相同义项集合，外部比较独立WSD决定，再重标模型错例。这比只比较两个benchmark总分更接近解释。它与我们刚观察的否定偏向和情境细分非常近，必须更新最近邻距离。

仍需分清三个因果对象。给义项同时改变知识可得性、粒度和任务形式；作者已承认，不能假装这是我们首次指出。将最终比较交给外部程序，移除了模型的比较计算，而不仅是“教模型分步”；成功不能证明模型原本自然执行相同分解。基于生成解释分类错误，也受回答后合理化或解释本身错误影响；它是有价值的行为证据，不是内部处理轨迹。

平均WSD正确率与WiC正确率不宜直接做差称比较开销：WiC需要两个局部判断，错误相关性和两个错义可能偶然相等都会改变期望。其WiC-through-WSD逐例结果比这个总分差更有信息量。我们可以报告独立两个局部判断均有支持的子集，并同时保留全体，以免选择成功例造成偏差。

## 最近邻距离与最小非平凡增量 INFERENCE

本项目已经没有“首次发现独立选义好而联合比较差”“首次发现WiC过度细分”“首次用义项改善WiC”的位置。AACL录用声明并不使解释成为终点，20词和错误抽样也不能据此判定作者结论无价值。对齐更强证据的办法是控制解释中的关键变量。

本轮新增问题是：**已独立生成的两份意义描述固定，加回原始语境还能否改变关系决定？** 这试图区分额外知识/粒度锚点与情境比较的影响，不只是把英语实验搬到跨语数据。若加回产生差异，仍需排除长度/信息位置、错误释义、读出极性和原标签争议；只有能预测未见词族/任务，才可能超出已有认识。[冻结的加回设计](../notes/AM2ICO_GLOSS_ADDBACK_DESIGN_2026-10-13.md)。

本地设计自身随后发现目标列表不对称，已经[补做严格匹配](../notes/AM2ICO_TARGET_RESTATEMENT_DESIGN_2026-10-13.md)。另外，[Liu等EMNLP2022](liu-2022-context-word-bias.md)已讨论语境有害与相关实体混淆；不能仅以加回变差宣称新的语义干扰现象。
