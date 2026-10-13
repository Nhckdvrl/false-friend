# 词义与命题是否被混为一谈？第四轮内的追加预测

**后验来源**：观察到 Romance 人工 `individual`、`independiente` 及 `lavado/lavagem` 的若干交换翻转后提出，不是事前确认假设。原例有语域、否定及细粒度多义竞争解释。CL 2024 Ohmer 的指令/输入分离、ACL 2025 Hwang 的任务切换分析提示：保持输入相同而改变所问的关系，可能比追加提示更有信息。

冻结的新测试：12 个互补状态词对；EN–EN 与 ZH–EN；第一目标的正反词平衡；目标词相同/互补；各句有无否定独立操纵。每个领域明确只有两个互斥穷尽状态，以免“not hot”未必“cold”的自然语言问题污染命题 gold。对同一个输入，分别问两个目标词本身是否同义、两句是否表示同一状态。每词族 64 次，共768/模型，采用自然 YES/NO + 简短解释。公开全部真值因子。该材料是局部审核的构造性诊断，不是自然使用分布，也不测纯词义记忆。

词义 gold 只随目标词改变；命题 gold 还随否定的奇偶性改变。因此，否定恰好一处时两个任务的 gold 相反。若词义回答跟随命题 gold，且同例命题判断正确，支持特定行为上的判断对象混淆；若词义不受干扰，则否定不充分解释原例，应回到自然上下文的绑定/粒度。若命题任务本身也错，应保留逻辑/指令能力不足。不可仅凭两任务回答相同就声称内部模块切换，也不把错误解释当真实计算轨迹。

十二族：active/inactive, enabled/disabled, locked/unlocked, connected/disconnected, present/absent, occupied/vacant, valid/invalid, visible/invisible, legal/illegal, married/unmarried, online/offline, open/closed。互补性由本题明确的二态领域限定；不泛称这些自然语言词在所有语境都严格互补。它们与上一轮职业材料不是同一类关系。
