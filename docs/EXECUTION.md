# 本地执行：原研究复现与新诊断工具分开

主交接：[HANDOFF.md](../HANDOFF.md)。科学实验组合：[EXPLORATION_PORTFOLIO.md](../experiments/EXPLORATION_PORTFOLIO.md)。本文件不是GPU禁止令或必须等人逐步授权的队列；使用用户已批准的空闲资源，先检查实际环境。

## 软件验证

```bash
python -m pip install -e '.[dev]'
python scripts/build_knowledge_index.py --check
python scripts/check_knowledge.py
python -m pytest -q
```

知识检查可保证来源登记、路径和持久试跑数据一致，不能确认实验语义或论文价值。

## 复现原研究

由本地Agent选择最接近当前问题的Tanwar/Doppelganger/Abuín任务，核查作者prompt、metric、模型/tokenizer版本。源数据可支持其原任务，不必伪造两个新reviewer；缺少源评估规则时报告范围，不能自建一个似然分数就称原文复现。

## 仓库现有二选一工具的界限

`scripts/run_behavior.py` 与JSONL schema是**自建诊断工具**，只适配部分语言和单token回答方案，不是整个科研项目唯一入口。示例需 `--allow-illustrative` 且不作科学结论；真实派生题需来源和针对性验证。source已有标签与derived新标签应分开，不要为兼容schema篡改source类别或虚构审查记录。

候选追加导致前缀重新分词时不可直接按旧prefix长度计算概率；当前工具会拒绝，改格式须记录新协议并测试。答案相同、分母不同的gold依赖mask不是标准预测概率。

## 探索环境选择

优先本地缓存、目标语言能力足够且可取logits/hidden states的开放模型；一台节点多组独立实验可并行。精确型号与预算由现场资源、模型语言覆盖及研究目标决定，保存版本。不能以0.5B烟雾测试推断32B模型或整个理论。

实际运行逐例结果、失败、分组、协议变化和资源使用保存到独立run目录；本仓库[evidence](../evidence/README.md)的既有记录不得覆盖。原脚本若不满足当前设计，可主动重写更好实现，只需保持估计对象和复现差异清楚。
