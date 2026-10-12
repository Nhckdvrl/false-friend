# 已完成的第一轮来源/程序审计，以及当前交接边界

**2026-10-12：本文件是历史 sprint 摘要，不是必须执行的研究队列。** 当前自主实验组合见 [EXPLORATION_PORTFOLIO.md](EXPLORATION_PORTFOLIO.md)，正式交接见 [HANDOFF](../HANDOFF.md)。原全文保存在 `knowledge/history/FIRST_PASS_BEFORE_FOUNDATION.txt`，其停止/优先级建议以新主线为准。

## 原始材料与结果

Tanwar源版本 `281a67eac6ddbe5445e1c10277e5833d40d72125` 的三组语言Task3各280行（140/140），上下文标记存在性检查通过。源代码以先回答语言、再解释意义、再判断连贯性的方式生成回答；这可能引入回答级联，尚非其效应的已验证解释。

Romance WiC源版本 `a87b73e387a6ef86d0cef7ffe703150905e75d7a`：704行，332词条字串完全相同，其中189为给定上下文R=0；严格逐字同形且两句中均以独立词出现的R=0为69行、58个语言对/词形单位。这是**源对象结构**，不是全部需要该筛选，也不是69个已独立标注的有效新实验。

原作者70/34等输出类别统计尚未用原模型与原人工分类完成忠实复现。自建二选一英语定义读出不同于作者自由生成协议；不可替代后仍说复现。

## 历史试跑

0.5B的一词六次生成有目标误认和德语名词大小写风险；1.5B的三词36次分数有选项顺序敏感性。详见 [原报告](PILOT_FINDINGS_2026-10-12.md) 和 [本仓库持久证据](../evidence/README.md)。这些小试跑不能选择或否决一个大研究方向。

## 仍可使用的工具

```bash
python scripts/audit_romance_wic.py --source-dir SOURCE_DIR --output outputs/romance.json
python scripts/audit_tanwar_baseline.py --source-dir SOURCE_DATA_DIR --output outputs/tanwar.json
python scripts/audit_tanwar_identifiability.py --source-dir SOURCE_DATA_DIR --output outputs/identity.json
```

这些工具用于检查源数据对象，不证明模型能力。后续优先用能力合适的缓存模型和原任务建立可重复事实，再按问题设计交叉测量和反事实，不继续无限扩展源审计。
