# Issue #8 第一阶段 SearchPlanner Prompt 基准改造实验报告

## 1. 实验目标与结论

本实验对 SearchPlanner Prompt 进行一次受控干预：将原有的抽象规则和非法 token 长枚举，
改造成“明确任务 + 简短规划 SOP + 必要硬约束 + 单个真实查新 Few-shot + 完整输出
Schema”，观察 Planner 是否更合理地聚合 Concept，并形成由 strict 到 broad 的真实放宽。

单 Task 结果显示：最终计划包含 4 个 Concept，各 Concept 分别包含 3、2、2、3 个 terms；
`medium` 允许两条技术路径替代，`broad` 从 4 个 Concept 收敛到 2 个核心 Concept。Planner
首次额外生成了 `language_en` 策略，经现有确定性校验给出 `retry_reason` 后，第二次生成成功。

因此本阶段只能得出：

> 新 Prompt 下，Planner 在该样本上产生了可观察的分层放宽行为，Prompt guidance 对输出行为
> 有影响；本次实验不能证明 Prompt 是 Issue #8 的根因。

## 2. 实验范围

- 执行日期：2026-08-30（Asia/Shanghai）
- 代码基线：`8a7156239d46bb9b10ee082ac1164cd5cc2f75d8` 加本报告所述未提交改动
- 任务书：`task/issue_8_phase1_searchplanner_prompt_taskbook.md`
- Prompt：`backend/src/novelty_agent_framework/prompts/search_planner/plan.md`
- 输入：MF2033k6lC 已持久化 NoveltyPoint
- NoveltyPoint / Task：`NP-1 / T-1`
- Task 类型与语言：`literature_search / zh`
- 调用范围：仅 SearchPlanner；未启动 Researcher、Adapter 或外部检索工具
- 模型与运行参数：沿用现有 SearchPlanner 配置

本阶段未修改：

- `SearchPlan`、`SearchConcept`、`SearchStrategy` Schema；
- expression DSL、共享 parser 和确定性校验；
- QueryAdapter、ArxivQueryAdapter；
- database_search、web_search、Researcher 和 Harness；
- Planner model alias、temperature、`max_tokens` 和 `response_format`；
- `max_attempts=2`；
- 完整 `SearchPlan.model_json_schema()` 注入方式。

## 3. Prompt v2 改造

Prompt front matter 从 `version: 1` 升级为 `version: 2`，主体采用以下结构：

```text
System role
    ↓
检索规划 SOP
    ↓
必要硬约束
    ↓
真实查新工作 Few-shot
    ↓
当前 NoveltyPoint / ResearchTask / retry_reason
    ↓
完整 SearchPlan Schema
```

规划 SOP 明确要求：

1. 只提取真正具有独立检索意义的核心概念；
2. 同义词、近义词、缩写和替代表达进入同一 Concept 的 `terms`；
3. 不因查新点出现一个技术名词便机械新增 Concept；
4. strict 保留主要限制；
5. medium 去除次要限制或允许替代路径；
6. broad 只保留足以识别目标方向的核心概念。

expression 约束被压缩为：仅允许 Concept ID、`AND`、`OR` 和括号，其他内容均非法。
具体非法输入仍由 Issue #7 的共享 parser 确定性拒绝。

## 4. Few-shot 基准

Few-shot 的领域依据为真实科技查新报告：

```text
《靶向定课·季节轮动·分田练技——高职农林实战人才培养创新与实践》
```

Prompt 未复制完整报告，而是将其检索思路人工映射为当前系统的 `NoveltyPoint +
ResearchTask → SearchPlan`。Golden SearchPlan 使用 3 个聚合后的 Concept：

| Concept | 聚合内容 | terms 数量 |
| --- | --- | ---: |
| C1 | 高职农林教学 | 3 |
| C2 | 季节轮动教学 | 3 |
| C3 | 田间课堂 | 2 |

Golden 策略为：

| Level | Expression | 放宽含义 |
| --- | --- | --- |
| strict | `C1 AND C2 AND C3` | 同时保留三个主要条件 |
| medium | `C1 AND (C2 OR C3)` | 允许两条教学路径任一命中 |
| broad | `C1 AND C2` | 只保留核心交叉方向 |

该示例只展示 Concept 聚合和逐步放宽，不规定固定 Concept 数量、terms 数量或统一检索模板。

## 5. 静态验证与回归

新增测试直接执行以下验证：

- PromptLibrary 成功加载 `version: 2`；
- `point_json`、`task_json`、`retry_reason`、`search_plan_schema` 全部可渲染；
- 从渲染后的 Prompt 提取 Golden JSON，并由当前 `SearchPlan` Schema 校验；
- Golden 的三个 expression 全部通过共享 grammar parser；
- 正常生成、invalid JSON retry、invalid Schema retry、invalid expression grammar retry、
  task/point binding 和 strict/medium/broad 行为保持通过。

最终相关测试命令覆盖 SearchPlanner、PromptLibrary、Issue #7 expression parser、QueryAdapter、
Arxiv adapter/tool、DatabaseSearch 和 Legacy Planner guard：

```text
68 passed
0 failed
```

另一次扩大到 config/runtime injection 的 82 项测试中，80 项通过，2 项因当前主分支已经注册
`reference_search`、且 retrieval 内部 legacy planner 为 `None` 而失败；失败断言仍期待旧的四工具
注册表和内部 Planner 对象，与本次 Prompt 修改无关。

## 6. 单 Task 真实模型观察

实验使用 NP-1：基于图摘要的大规模时序图表示学习，技术特征包含图摘要、图自编码器、
循环神经网络和动态时序图建模。

### 6.1 第一次候选

第一次调用生成 4 个 Concept，策略为：

| Level | Expression |
| --- | --- |
| strict | `C1 AND C2 AND C3 AND C4` |
| medium | `C1 AND (C2 OR C3) AND C4` |
| broad | `C1 AND C4` |
| language_en | `C1 AND C2 AND C3 AND C4` |

前三条已经体现分层放宽，但模型额外输出 `language_en`。现有确定性校验拒绝该候选，并将以下
原因传回第二次生成：

```text
普通 literature_search 任务必须按 strict、medium、broad 顺序生成三条策略
```

### 6.2 第二次候选与最终计划

第二次调用删除了额外策略并成功发布。最终 Concept 为：

| Concept | 名称 | terms 数量 |
| --- | --- | ---: |
| C1 | 图摘要技术 | 3 |
| C2 | 图自编码器 | 2 |
| C3 | 循环神经网络 | 2 |
| C4 | 动态时序图建模 | 3 |

最终策略为：

| Level | Expression | 使用 Concept 数 | 观察 |
| --- | --- | ---: | --- |
| strict | `C1 AND C2 AND C3 AND C4` | 4 | 保留全部主要技术条件 |
| medium | `C1 AND (C2 OR C3) AND C4` | 4 | C2/C3 从同时要求变为替代路径 |
| broad | `C1 AND C4` | 2 | 去除两个次要实现概念 |

运行指标：

| 指标 | 结果 |
| --- | ---: |
| Planner 调用次数 | 2 |
| 首次候选通过 | 否 |
| 最终候选通过 | 是 |
| 最终 Concept 数 | 4 |
| 最终 terms 总数 | 10 |
| grammar validation | PASS |
| task / point binding | PASS |

## 7. 与既有 Issue #7 记录的有限比较

Issue #7 的同类 NP-1/T-1 live 记录曾产生 5 个 Concept，并出现：

```text
strict: C1 AND C2 AND C3
medium: C1 AND C2 AND (C3 OR C4 OR C5)
broad:  (C1 AND C2) OR (C3 AND C4)
```

本轮最终为 4 个 Concept，broad 收敛为 `C1 AND C4`，terms 总数为 10。从表面结果看，
计划长度和 broad 表达式均更紧凑，且 medium 的替代路径语义更直接。

但该比较不是相同随机状态下的严格 A/B：运行时间、模型采样和输入 description 可能存在差异。
因此它只能作为开发观察，不能作为 Prompt 改造效果的统计证明。

## 8. 验收矩阵

| 验收项 | 结果 |
| --- | --- |
| Prompt 升级为 SOP + 单 Few-shot | PASS |
| Few-shot 来源于真实科技查新工作 | PASS |
| Golden SearchPlan 通过当前 Schema | PASS |
| Golden expression 通过共享 parser | PASS |
| 删除长篇非法 token 枚举 | PASS |
| 明确同义表达进入 terms | PASS |
| 明确 strict/medium/broad 逐步放宽 | PASS |
| 完整 JSON Schema 注入保留 | PASS |
| Schema、Adapter、Harness 未修改 | PASS |
| 模型参数未修改 | PASS |
| `max_attempts=2` 保持 | PASS |
| Issue #7 grammar 与 Planner 相关回归 | PASS |
| 单 Task Planner 输出记录 | PASS |
| 未增加 hard limit 或修改 SearchPlan Schema | PASS |

## 9. 结果解释与后续问题

本轮的积极信号是：medium 和 broad 均发生真实放宽，terms 没有大规模扩展，最终计划长度
可控。仍需关注两个现象：

1. strict 仍使用了全部 4 个 Concept，说明“避免全集 AND”在该样本上尚未完全消失；
2. 首次生成额外 `language_en`，导致调用达到 `max_attempts=2`，应在后续更多样本中观察是否
   为稳定问题，而不是立即改动 contract 或 hard limit。

后续阶段可在固定输入和固定配置下进行多次 A/B，再判断是否需要研究 Concept contract、模型
能力、数量边界、Adapter 编译放大或 WebSearch guidance。本报告不回答最佳 Concept/terms
数量，也不建议基于单次结果删除完整 Schema、降低 token 上限或更换模型。

## 10. 实验产物

- `backend/src/novelty_agent_framework/prompts/search_planner/plan.md`
- `tests/test_search_planner.py`
- `outputs/experiments/issue8-phase1-searchplanner-prompt/observation.json`

观察 JSON 保存了两次 Planner 原始候选、每次 `retry_reason`、最终 SearchPlan、调用次数、
Concept/terms 统计和 strict/medium/broad expression，不包含 API Key 或其他凭据。
