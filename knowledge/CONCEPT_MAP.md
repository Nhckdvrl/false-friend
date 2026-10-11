# 概念、主张和认识空白的交叉索引（2026-10-11）

## 一张图概括不同论文为何似乎互相矛盾

| 观察层次 | 已有结果 | 允许的推断 | 不允许的跃迁 |
|---|---|---|---|
| **form prediction** | Škrjanec：共享的英荷 false-friend 词形 surprisal 可能下降，频率解释大部分现象 | 形式更可预测；两语言频次影响显著 | 模型正确理解两语言意义 |
| **global transfer** | Kallini：即使低语义相似度共享，整体迁移也常优于无共享 | 词表重叠可能提供总体收益；高语义一致性通常更好 | 低相似共享 *必定* 有益，或不会伤害局部意义 |
| **context/sense behavior** | Stingray、Tanwar、Doppelganger、Abuín：同形异义在具体任务上出错 | 同形、词义、语境关系是弱点 | 原因就是同一 embedding，或存在不可消除的内部竞争 |
| **representation intervention** | Dumas、Körner、Ravisankar：概念、语言输出、任务内容的某些激活可交换 | 有局部因果操纵证据；patching 可改变答案 | 存在独立、唯一的“意义模块”，或 patching 一定修复理解 |
| **incremental reanalysis** | Christianson et al.、Good-Enough、Amouyal、Yoshida、Clark：先入解释、后续反证及修正已是成熟研究主题 | 可以借鉴理解错误的区分性实验 | LLM 的晚提示表现就是人类眼动/阅读时间的同一机制 |

## 因果对象必须拆开

- **Intervention**：严格共享 token ID / embedding；与“自然同形异义”是不同科学对象。
- **Outcome**：词形 surprisal / forced-choice gloss preference / 语义下游推断 / 自由翻译 / 中间表征 / 全局 transfer 必须分别报告。
- **Language identity**：文本语言、提示指定语言、需要的回答语言、目标词的来源语言，不是同一个变量。
- **Lexical form**：完全相同表面字串 vs 近形 / 大小写变体 / 词类变化 / 被拆分的 tokenizer 单元，不是同一个类别。
- **Sense alignment**：有一条相同词义的词典条目 ≠ 两种语料的完整 P(sense|form,L) 分布相等。
- **Representation**：可解码语义信息 ≠ 用于此时此地决策的信息。
- **Decoder timing**：在标准因果 Transformer 中，新增后文 token **不会改写旧位置已计算完成的 hidden states**；但后续位置可经 attention 读取先前激活并重建推断。主张“修正”须锚定 **新位置的下游表征/行为**，不能以旧 token state 被 retroactively updated 为假设。

## 三个紧张关系及其真正的前沿

### T1：低语义质量的 overlap 却提供全局迁移收益？
Kallini 的低相似度 overlap 并不意味着“错误语义也好”；高低 overlap 与天然的频次和语料位置相关，不同 overlap 间词表大小也变化。**可检验问题**：共享的有用性来自语义锚点、共享参数/有效样本密度、还是连接两语言分布的拓扑？不同解释对 **频率/参数/语义映射严格匹配的合成环境**有不同预测。

### T2：模型看起来“懂了词义”却翻译错？
Doppelganger 把任务拆成词义、语境词义和翻译；Körner 明确展示 patching 后同形词不再复制及词义切换。**不可重复发表**：不同任务输出有 gap 或能 patch 好翻译。**可检验问题**：在共享正确语义、多个独立语义下游任务均成功的前提下，有没有可选择性影响词形输出但不影响语义的干预？并与 Ravisankar 的答案标签伪因果控制比较。

### T3：晚证据来了，竞争意义为何仍被影响？
人类 Good-Enough 已提出 lingering misinterpretation；Tanwar 研究高低语义限制，Amouyal 研究 LLM garden path。**不可重复发表**：晚证据/误导后理解正确率下降。**可检验问题**：在词频、绝对和相对位置、文本长度、证据强度、普通同语言歧义、提示任务等控制后，是否尚有**跨语言形式碰撞特异**的残余错误，且能解释下游推断、而非仅答案词复制？

## 四个最危险的“伪认识空白”

1. “不存在同形异义词的跨语言理解 benchmark”——已有多套。
2. “语言与意义在内部可被分离”——Dumas、Körner 已做。
3. “后面的证据可能纠正不了前面的误解”——人类和 LLM garden path 都已做。
4. “共享词表 vs 不共享是否提升 transfer”——Kallini 和 Škrjanec 已做系统操纵。

选题不是在这四句话后加 “in more languages / layers / models”。必须给出**谁与谁的解释不能共存**的实验。
