# Kitamura, Huang & Aizawa 2025 — Doppelganger-JC

- **Paper**: https://aclanthology.org/2025.ijcnlp-long.96/
- **Code/data**: https://github.com/0017-alt/Doppelganger-JC
- **Depth**: **S1** (PDF §§1–5 and Fig. 2, repo README/questions sampled; not all appendices)
- **Role**: route A output-copy rival + reusable multiple-choice cases.

## 1. 关注的自然问题

中日共享汉字词形非常广泛，大多数共通词有相似意义；在这条有用的规律中，少数词的意义已经分化。模型在翻译时照搬字形，是因为**套用了通常有益的表面捷径**，还是词义能力彻底缺失？

## 2. Idea 起源尺度（INFERENCE）

引言说观察到实际翻译的误用，受到 Tanwar 2025 以及中日共有汉字词研究启发。提出的创新不在更复杂的架构，而在：**把通常不会暴露的 shared-form shortcut 放大成可审查的局部任务**。比 Stingray 多走一步的是特别分离 word-meaning / word-in-context / sentence-translation，且检验共享 POS 对 shortcut 的关系。

## 3. 论文事实

§3 的数据流水线图（Fig. 2）：日语词表 JKVC → 查跨语言意义集合、自动生成目标句/真实译文/三个误导译文 → 母语者核查 → 词义、上下文、翻译任务。论文分析将包含错误跨语言同形字串的译文作为 homograph shortcut 之一，观察部分模型的强错位及 POS 相关性。

实际 GitHub 的 questions/jp_zh/homographs.py 样本字段包括 target-sentence, target-meaning, correct, wrong1–3 和 English reference；词表文本划分 homographs 与不同语言的 unique meanings。**这比抽取字典释义后人工凑几个句子更接近可执行基线**。

## 4. 逆向实验链（INFERENCE）

从真实翻译例子中的直接复制出发，先区分 model 对词义是否知道（isolated）→ 在句子下会不会更好（context）→ 真实翻译时是否仍犯错（generation）。错误不完全随机，而与 token form 和共享词性有关 → 提出“捷径”式解释。*但是这些任务并不直接定位造成捷径的层与操作*。

## 5. 证据边界

- 如果 model 选 wrong translation，可能只是在输出侧复制容易的字串，不能认定 reading sense 是错的。
- 语义/翻译任务都用选择项，候选概率、option phrase-length、语义相似度可能成为偏置源。
- 样例多数经自动生成再人工核验；词频、真实分布和 item independence 仍需要研究者复核。

## 6. 最近邻

Körner 2026 在 activation patching 中也明确发现“修复”只是避免复制 homograph。因此 **再做一个修复 shortcut 的 patch 已被双重占据**。如果新研究只把翻译和意义识别行为并列对比，贡献与此文章更近 than novel mechanism.

## 7. 下一步

使用真实的 word-in-context 与 translation 题对比；另加 **和 copy 不相关的下游语义推断**，并匹配无歧义翻译、普通多义、答案长度和词形复制偏向。若所有看似“意义竞争”的效应都只来自自由翻译/候选字串，则路线 A 的内部词义冲突叙事不成立。

## 8. 待核查

实际 GitHub questions Python dict 的每个语对条目数量、许可证、样本来源和 potential duplicate；不是把每种 question variant 当独立 lexical evidence。
