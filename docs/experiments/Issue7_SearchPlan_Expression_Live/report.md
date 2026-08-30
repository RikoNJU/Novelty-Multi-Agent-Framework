# Issue #7 SearchPlan Expression Grammar 单 Task 真实实验报告

## 1. 目标与最终结论

本实验使用真实模型、真实 SearchPlanner、正式 TaskResearcher 和真实 arXiv 检索，验证
Issue #7 的共享 expression grammar，并验证首次 live 暴露出的四项修正：

1. `database_search` 显式告诉模型可用 `source_id`；
2. 数据库返回 `artifact_ids` 后强制优先 Reader；
3. 失败调用不消耗成功调用预算；
4. 实验记录 Planner 原始候选和 `retry_reason`。

实验从 Researcher 注册表中移除了 `web_search` 与 `browser`，只注册
`database_search` 和 `reader`。

最终结论：**Issue #7 Grammar 和上述四项修正均通过真实链路验证；Task 结果仍为
`partial`，原因是模型在两轮“检索→阅读”后没有结束，而是尝试第三次数据库检索，触发
两次成功调用的预算上限。**

## 2. 实验范围

- 最终复验时间：2026-08-30 18:46:42–18:48:18（Asia/Shanghai）
- 代码基线：`1e17ad7d4d4e9f531045f909603a67ba3edd1c10` 加本报告所述未提交修正
- 实验入口：`novelty_agent_framework.experiments.issue7_single_task_database_only_live`
- 输入：MF2033k6lC 已持久化真实论文
- NoveltyPoint / Task：`NP-1 / T-1`
- Task 类型与语言：`literature_search / zh`
- 注册工具：`database_search`、`reader`
- 禁用工具：`web_search`、`browser`
- 外部服务：配置模型 Provider、arXiv API、arXiv 全文获取

## 3. 三轮 live 结果演进

### 3.1 首轮：发现 source 与预算问题

首轮实际轨迹为：

```text
database_search(cnki)  → FAIL，source 未配置
database_search(arxiv) → SUCCESS，4 个候选
database_search(null_catalog) → 被 database_search=2 预算拒绝
```

这证明 Grammar 和 arXiv 编译正常，但暴露了模型猜测 CNKI、失败调用占用预算、数据库返回
Artifact 后未优先 Reader 三个问题。

### 3.2 第二轮：Grammar 拒绝非法候选

第二轮 Planner 两次都生成了包含带引号自然语言的 expression，错误包含：

```text
invalid_expression_grammar: strategy S1:
检索表达式包含不支持的 token："'graph"
```

共享 Grammar 正确阻止非法 SearchPlan 发布。该轮同时发现 Planner 最终失败时实验脚本尚未
及时落盘内存中的候选，因此又补充了失败态遥测，并强化 Planner Prompt 的 DSL 约束。

### 3.3 第三轮：四项修正复验

第三轮 Planner 一次生成成功，Researcher 实际轨迹为：

```text
database_search(arxiv) → SUCCESS，8 个候选
reader(返回的 artifact_id) → SUCCESS
database_search(null_catalog) → SUCCESS，0 个候选
reader(先前返回的另一个 artifact_id) → SUCCESS
database_search(...) → 被两次成功调用预算拒绝
```

第三轮没有 CNKI 或其他未配置 source，没有数据库结果后连续搜索，说明动态工具描述和
Reader 硬门禁均生效。

## 4. SearchPlanner 与 Expression Grammar

最终复验记录了完整脱敏 Planner 候选：

- Planner 调用：1 次；
- `retry_reason`：空字符串，表示首次生成；
- 候选：已保存于 `planner_attempts.json`；
- 敏感键：递归替换为 `<redacted>`；
- 发布策略顺序：`strict → medium → broad`。

| Strategy | Level | Expression | Grammar |
| --- | --- | --- | --- |
| S1 | strict | `C1 AND C2 AND C3` | PASS |
| S2 | medium | `C1 AND C2 AND (C3 OR C4 OR C5)` | PASS |
| S3 | broad | `(C1 AND C2) OR (C3 AND C4)` | PASS |

三条 expression 均只含 Concept ID、`AND`、`OR` 和括号。没有非法 literal、未定义
Concept、操作数/操作符错误、括号错误或不完整 expression。

Planner Prompt 现已明确：

- expression 是严格 DSL；
- 合法示例为 `C1 AND C2`、`C1 AND (C2 OR C3)`；
- 禁止 terms、自然语言、引号、`NOT`、`&&`、`||`；
- 检索词只能放在 `concepts[*].terms`。

## 5. 可用 source_id 修正

`DatabaseSearchTool.description` 不再使用固定类描述，而是在实例初始化时根据实际
`tools_by_source` 动态生成。最终复验中模型收到的描述明确列出：

```text
source_id 只能使用以下值：arxiv, null_catalog
```

最终模型首次调用直接选择 `arxiv`，没有再猜测 CNKI。未知 source 的运行时校验仍保留。

## 6. Reader 优先策略修正

Reader 优先现在有两层约束：

1. Prompt 和 `database_search.description` 明确要求结果含 `artifact_ids` 时，下一次调用必须 Reader；
2. ToolCallHarness 从成功 observation 提取全部 `artifact_ids`，下一次非 Reader 调用或读取不匹配
   Artifact 时抛出 `reader required after database_search returned artifact_ids`。

最终轨迹中两次数据库调用后都紧跟 Reader，门禁行为通过真实模型验证。

## 7. 成功与失败预算分离

Harness 继续用 `tool_calls_used` 记录所有实际尝试，但以下预算只计成功 observation：

- `max_tool_calls`；
- `per_tool_limits[tool_name]`。

因此 source 参数错误、schema 错误或工具执行失败不会吞掉成功检索额度；整体循环仍由
`max_turns` 保持有界，防止无限失败重试。

最终复验没有产生 source 失败，但单元测试已验证“一次失败 + 一次成功”在
`max_tool_calls=1`、单工具 limit=1 下可以恢复并完成。最终第三次数据库调用被拒绝，是因为
此前已经有两次成功的 `database_search`，属于预期预算行为。

## 8. 最终运行指标

| 指标 | 结果 |
| --- | ---: |
| Planner 调用 | 1 |
| database_search 成功执行 | 2 |
| reader 成功执行 | 2 |
| web_search 调用 | 0 |
| browser 调用 | 0 |
| Legacy Planner 调用 | 0 |
| 第一轮 arXiv 候选 | 8 |
| 第二轮 null_catalog 候选 | 0 |
| trusted reads | 2 |
| Evidence / EvidenceCard | 0 / 0 |
| Task 状态 | partial |
| Task 耗时 | 96,195 ms |
| Planner token | 6,659 |
| Researcher token | 31,260 |
| 总 token | 37,919 |

全链路未出现 `unsupported literal token`，没有 strategy 因 Grammar 失败被 Adapter 丢弃，
Legacy Planner 调用为 0，WebSearch/Browser 实际调用均为 0。

## 9. 验收矩阵

| 项目 | 结果 |
| --- | --- |
| 可用 source_id 出现在模型工具描述 | PASS |
| 模型不再猜测 CNKI | PASS |
| Artifact 后 Prompt 要求 Reader | PASS |
| Artifact 后 Harness 确定性要求 Reader | PASS |
| 数据库后实际调用 Reader | PASS |
| 失败调用不消耗成功预算 | PASS（单元测试） |
| Planner 候选脱敏落盘 | PASS |
| Planner retry_reason 落盘 | PASS |
| Planner 最终失败时也落盘 | PASS（代码路径与第二轮问题修复） |
| strict / medium / broad | PASS |
| 共享 Grammar | PASS |
| QueryAdapter 真实编译与 arXiv 执行 | PASS |
| Legacy Planner 为 0 | PASS |
| WebSearch/Browser 为 0 | PASS |
| Finish Draft / EvidenceCard | NOT PROVEN |

## 10. 剩余问题

本轮 `partial` 不再由 source 猜测、失败预算或缺少 Reader 引起。模型已经阅读两份 Artifact，
但仍选择继续检索而非结束并输出 `ResearchFinishDraft`。后续应单独处理 Researcher 的停止策略，
例如在两轮数据库检索和至少一次成功 Reader 后，要求模型基于已有文本生成卡片或明确返回
`cards=[] + no_evidence_reason`。该问题不属于本次四项修正范围。

## 11. 产物

- `outputs/experiments/issue7-single-task-database-only-live/summary.json`
- `outputs/experiments/issue7-single-task-database-only-live/planner_attempts.json`
- `outputs/experiments/issue7-single-task-database-only-live/task_request.json`
- `outputs/experiments/issue7-single-task-database-only-live/task_result.json`
- `outputs/experiments/issue7-single-task-database-only-live/trace.jsonl`
- `outputs/experiments/issue7-single-task-database-only-live/model_calls.json`
- `outputs/experiments/issue7-single-task-database-only-live/effective_config.json`

配置使用项目安全导出，Planner 候选经过递归敏感键脱敏，产物不包含 API Key。
