# 查新点的保守删除与逐项覆盖账本

本项针对两个已有代码/历史反例：同 claim 的增量候选通过 `setdefault` 聚合，后来的不同 technical_features 会丢失；形式合法的重复映射允许删除 DSGNN 框架并以 Sketch-DBH 代表，却没有保留其技术机制。

已加入默认开启的 `point_extractor.conservative_dedup=true` 和独立覆盖账本。不同 claim 的等价关系仍由模型提出，Harness 不通过关键词、大小写折叠、相似度或名称包含关系证明技术等价。无法机械证明内容保留时，候选保持待核查研究范围，不把多保留的点当作已确认独立贡献。

## 行为与边界

- 每轮原候选保留原始字段、稳定 occurrence ID 与 hash。同 claim（只去掉首尾空白）的聚合对中英文 technical_features 和 source_locations 做稳定并集；原有中英文 claim 变体仍在账本，冲突英文声明标 pending，不能被首项选择掩盖。
- 首轮一次返回的同 claim 多条候选及补核增量也走同一保留逻辑。不再只修复某一种重试分支。
- 合法删除映射先通过原索引/代表/理由契约，再检查：claim 字面相同；已提供的英文 claim 不丢失；源候选有非空技术特征；中英文特征均在代表中逐字保留。通过只证明字面内容保留，`semantic_equivalence_verified=false`。来源位置合并保留。
- 不满足条件的删除不执行，保留 proposal、coverage_proof、pending_indices。不同 claim 即使有相同特征或模型理由，也不能靠这些字段获得机械删除授权。此保守策略可能留下语义重复的候选并增加下游待核查范围；既有调用/检索预算仍约束执行。
- 无技术特征的实验描述不凭点数获得“独立贡献已确认”：`final_points[].status=pending_technical_features`，`independent_contribution_confirmed=false`。点数达标仍只是原计数诊断。
- 原有最多 5 次提取/去重/补核调用上限不变，没有增加语义核验调用、无限补点或强模型回退。

配置 `false` 可复现原来的映射删除决策，但覆盖账本仍显示候选/feature 丢失或未证实映射，不能标为完整。该开关不撤销同 claim 并集修复；因此它是删除策略消融，不是恢复整份旧源码。

## 账本契约

实现位于 `core/point_coverage.py`；`agents/point_extractor.py` 在提取成功或异常退出时构建 `last_trace.coverage_ledger`。

| 字段 | 含义 |
| --- | --- |
| `candidates[]` | 每个 generation/coverage 原候选、原字段/hash、最终点 ID 或明确 pending 状态；非法/超数量批次原候选也保留待核查 |
| `features[]` | 每个原中英文特征 occurrence 的文本、来源候选、最终点 ID；不从另一个无关点借用相同文字来掩盖丢失 |
| `source_units[]` | digest 中逐条 claimed_contributions 与有界作者贡献原文片段；记录字段/区间、原文和 hash |
| `final_points[]` | 最终重编号点的机械状态；无特征和未解决删除单独标记；不确认独立贡献 |
| `candidate_features_preserved` | 已记录 feature 是否均在对应最终点字面保留，不能替代来源/语义覆盖 |
| `source_coverage_status` | 只有整条 source unit 与最终 claim/feature 字面相同才记 literal_text_retained；其他为 pending_source_alignment；无明确作者单元为 unknown_no_explicit_author_units |
| `coverage_complete` | 仅指所提供 digest 与已记录候选的机械账本无未决项；不证明论文总体贡献完整或技术语义正确 |
| `semantic_coverage_verified` / `independent_contributions_confirmed` | 始终 false；不让确定性字符串规则冒充语义裁定 |

未解决的 source unit 保留 Unknown/Pending，不通过 model source_locations 标签或关键词匹配认定覆盖。`unseen_full_text_coverage_verified=false` 明确当前 digest 未展示正文不在已验证范围。生成错误及补核错误保留在账本，不被后续有结果掩盖。若去重模型调用失败，已生成候选仍可追到 pending，而非从诊断中消失。

有未决项时，外层 trace 为 `scope_status=pending_coverage`、`coverage_complete=false`。工作流/报告的绑定由主任务另行接入；本分项不直接修改其文件。

## 固定历史 holdout

[可移植 fixture](../../../tests/fixtures/extractor/historical_dedup_20260924.json) 原样抽取 09-24 `run-f41ac741...` 的四候选、原 digest，以及首轮真实 Qwen 新映射协议输出。保留原始文件路径与 SHA-256；候选去重输入 SHA-256 仍为 `a1ffb46772154fcb1ff7e043f63cb8ba8c37c503dd4f00a2fd9a0b8dc989f464`。没有修改候选、特征、源材料或模型提出的 `2→1`、`3→4` 反例。

[离线重放脚本](replay_point_coverage_offline.py) 把相同固定响应送入生产提取器的两个策略，结果见 [summary.json](point_coverage_holdout/summary.json)。所有返回都来自本地 fixture，真实 LLM/网络/检索调用均为 0。

| 指标 | 旧映射策略 false | 保守策略 true |
| --- | ---: | ---: |
| 最终候选数 | 2 | 4（原四项） |
| 删除编号 | 2、3 | 无 |
| 待核查删除编号 | 无 | 2、3 |
| 原始中英 feature occurrences | 24 | 24 |
| 未在最终对应点保留的 feature | 12 | 0 |
| coverage_complete | false | false |
| semantic_coverage_verified | false | false |
| 固定替身响应次数 | 3 | 2 |

替身次数差异来自旧策略删除后触发既有补核，不是新模型调用量改善的实测。多保留两项只证明原候选和特征未被该删除动作移除，不能证明四项均独立、有原文语义支持或已形成 Evidence。作者声明/源片段对齐仍显示 pending，未把“保留”称为“已证明完整”。

## 回归与交付

`tests/test_point_coverage.py` 覆盖同 claim 增量、单轮重复、补核增量、文字子集可保留、不同 claim/缺失特征/英文冲突/大小写变化不可证明、无特征候选、作者原文未决、历史反例、去重失败及超数量原候选留账。原 `test_point_extractor.py` 的三项旧删除策略测试显式使用 `conservative_dedup=False`；新默认的保护由单独测试证明，未把新默认改回旧删除行为。

定向 **54 passed**，见 [point_coverage_tests.log](point_coverage_tests.log) 与 [JUnit](point_coverage_tests.xml)。命令：

```bash
/home/lya3106643285/miniconda3/envs/Novelty-web/bin/python -m pytest \
  tests/test_point_coverage.py tests/test_point_extractor.py \
  -o addopts='' -q \
  --junitxml=docs/experiments/20260927_harness_config_closure/point_coverage_tests.xml
```

`git diff --check` 通过。配置接线由配置子任务负责；全套集成测试由主任务汇总。本项未更改 prompt 模板、论文输入、Evidence/Reviewer 标准，也没有进行真实模型实验。
