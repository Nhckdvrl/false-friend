# Zhang & Nanda — Towards Best Practices of Activation Patching in Language Models: Metrics and Methods

**来源**：[原文2309.16042](https://arxiv.org/pdf/2309.16042)。S1：主要方法、factual recall/IOI对照、Fig3–5与§§3–6/8讨论；未重做27页实验。此条不凭印象添加会议奖项。2026-10-12。

## 背景和 idea 来源（INFERENCE）

因果patch已被广泛用于定位知识/电路，但“选什么corruption、输出测什么、替换几层”常被当实现细节。作者以已研究任务和既有电路作参照，把这些实现自由度本身变成可测试对象。创新是揭示**同一种工具为什么会生成不同机制叙述**，而不是另造一个神经结构。

## 已核验实验（FACT）

比较Gaussian noising与对称token替换、probability/logit difference/KL类度量、单层与窗口patch及不同污染token。噪声会破坏一些原有内部行为；输出概率接近零时可能漏掉负向组件；窗口效果不能视为单层效果相加。不同被替换信息也会改变定位图。

## 实验链与推断上限

首先保持任务不变、仅改方法，显示结论敏感；再看已知组件和注意行为，解释为什么某种corruption不再是同一计算问题；最后把度量的数学地板/饱和效应和定位解释联系起来。这比“我们的heatmap不一样”更进一步。

作者实验主要是特定decoder与任务，建议不是所有架构保证。主要方向是clean激活放回corrupted运行；反向干预的含义不同。多个位置共同替换的效果，也不能记在一个组件账上。

## 对false-friend机制研究的实际要求

若要比较两个词义，使用有可解释替代义的自然donor优于随意加噪；但语法、位置、语言和答案词都可能同时变。至少报告原行为、干预结果、无关语义保持、相反方向，以及两种合理输出读出。不要把一个归一化恢复率直接等同“完整因果中介”，尤其分母很小或原ICL效果为负时。

**下一实验**：相同sense不同语言donor与相同答案label不同sense donor若给出相同救援，语义转移解释就不足。若不同corruption只是追踪不同信息，则应明确两个估计对象，而非选择更漂亮的图。
