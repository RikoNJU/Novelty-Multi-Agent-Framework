# 当前错误码与补检／恢复动作码

核查日期：2026-09-28；代码基线：`7e71dc9`。本文记录现状，不表示完整闭环已交付。

**当前有 27 个错误码、13 个恢复动作码；独立的补检原因码目录尚未建立。总图恢复策略会直接生成其中 7 种动作。** 错误事件中的建议动作不等于已执行动作，目录重试上限也不等于总图必然自动重试。

## 错误码（FailureCode）

来源：[定义与目录](../backend/src/novelty_agent_framework/schemas/failures.py)。下表是目录规定，不是全部生产路径的覆盖证明。

| 错误码 | 含义 | 层级 | 允许的恢复建议（首项为默认） | 最多追加重试 | 结论影响 |
| --- | --- | --- | --- | --- | --- |
| `provider.authentication` | 来源身份认证失败 | `provider` | `change_provider`, `manual` | 0 | `limits_coverage` |
| `provider.authorization` | 来源授权不足 | `provider` | `change_provider`, `manual` | 0 | `limits_coverage` |
| `provider.rate_limit` | 来源限流 | `provider` | `retry_request`, `change_provider`, `stop` | 1 | `limits_coverage` |
| `provider.network` | 来源网络故障 | `provider` | `retry_request`, `change_provider`, `stop` | 1 | `limits_coverage` |
| `provider.service` | 来源服务故障 | `provider` | `retry_request`, `change_provider`, `stop` | 1 | `limits_coverage` |
| `provider.protocol` | 来源协议或响应异常；分类不等于根因已定位 | `provider` | `change_provider`, `manual` | 0 | `limits_coverage` |
| `provider.resource_missing` | 来源资源不存在 | `provider` | `change_provider`, `manual` | 0 | `limits_coverage` |
| `provider.unknown` | 来源故障未分类 | `provider` | `manual`, `stop` | 0 | `limits_coverage` |
| `material.unavailable` | 材料不可用 | `reader` | `fetch_fulltext`, `manual` | 0 | `limits_coverage` |
| `material.integrity` | 材料完整性异常 | `reader` | `manual`, `stop` | 0 | `blocks_card` |
| `tool.scope` | 工具访问超出允许范围 | `harness` | `repair_arguments`, `stop` | 1，需改变输入 | `blocks_card` |
| `tool.arguments` | 工具参数不合法 | `harness` | `repair_arguments`, `stop` | 1，需改变输入 | `limits_coverage` |
| `tool.unavailable` | 工具不可用 | `harness` | `manual`, `stop` | 0 | `limits_coverage` |
| `model.timeout` | 模型调用超时 | `model` | `restore_checkpoint`, `retry_request`, `stop` | 1 | `blocks_point` |
| `model.transport` | 模型传输失败 | `model` | `restore_checkpoint`, `retry_request`, `stop` | 1 | `blocks_point` |
| `model.context_limit` | 模型上下文超限 | `model` | `restore_checkpoint`, `stop` | 0 | `blocks_point` |
| `model.context_unavailable` | 上下文计数或准入信息不可用 | `model` | `manual`, `stop` | 0 | `blocks_point` |
| `model.output_schema` | 模型输出不符合结构 | `model` | `repair_output`, `stop` | 1，需改变输入 | `blocks_point` |
| `model.output_reference` | 模型输出引用不合法 | `reviewer` | `repair_output`, `stop` | 1，需改变输入 | `blocks_point` |
| `model.usage_unavailable` | 模型用量不可用 | `runtime` | `none` | 0 | `accounting_unknown` |
| `harness.budget_exhausted` | 执行预算耗尽 | `harness` | `stop` | 0 | `blocks_point` |
| `coverage.not_executed` | 检索未执行 | `researcher` | `research_gap`, `stop` | 0 | `limits_coverage` |
| `coverage.no_match` | 已执行查询没有命中 | `provider` | `replan_query`, `stop` | 0 | `limits_coverage` |
| `evidence.missing` | 证据缺失或数量不足 | `researcher` | `research_gap`, `stop` | 0 | `limits_coverage` |
| `review.missing_features` | Reviewer 技术特征证据缺口 | `reviewer` | `read_artifact`, `fetch_fulltext`, `research_gap`, `stop` | 0 | `blocks_point` |
| `review.summary_failed` | Reviewer 汇总失败 | `reviewer` | `resume_review`, `stop` | 1 | `blocks_point` |
| `execution.unknown` | 未分类执行异常 | `runtime` | `manual`, `stop` | 0 | `unknown` |

结论影响：`limits_coverage` 限制覆盖范围；`blocks_card` 阻断单卡；`blocks_point` 阻断查新点；`accounting_unknown` 用量核算未知；`unknown` 影响未确定。协议还允许 `blocks_run`，但当前目录没有条目采用它。

错误事件还记录对象范围、证据引用、因果事件和重试约束。尚未完成全部 27 类生产发出路径及真实恢复覆盖验收；此前审计中 `model.usage_unavailable` 仅见目录定义。

## 补检／恢复动作码（RecoveryAction）

来源：[恢复策略](../backend/src/novelty_agent_framework/core/recovery_policy.py)、[工作流](../backend/src/novelty_agent_framework/workflows/novelty.py)、[工具范围约束](../backend/src/novelty_agent_framework/tools/recovery_registry.py)。

| 动作码 | 用途 | 总图直接生成 | 当前条件或边界 |
| --- | --- | --- | --- |
| `retry_request` | 重试原来源请求 | 是 | 仅网络、限流、服务故障；没有替代来源时按点和来源最多追加一次，沿用原计划 |
| `repair_arguments` | 纠正工具参数 | 否 | 目录建议；不由 plan_recovery 自动调度 |
| `repair_output` | 纠正模型输出或引用 | 否 | 目录建议；不能据此声称单卡失败已自动纠错 |
| `change_provider` | 切换检索来源 | 是 | 已尝试查询全部技术失败；只使用显式配置且未使用的替代来源 |
| `fetch_fulltext` | 获取已有记录的全文 | 是 | 语义缺口且已有记录缺全文；绑定来源及记录，每次最多 4 条 |
| `read_artifact` | 补读已有材料 | 是 | 绑定明确材料和命名空间；避免重复恢复读取 |
| `replan_query` | 重新规划查询 | 是 | 查询成功但零候选；交由模型规划新方向 |
| `research_gap` | 针对未解决缺口补检 | 是 | 证据数量或语义缺口仍未解决；补检不保证产生有效证据 |
| `resume_review` | 恢复 Reviewer 核验／汇总 | 否 | 部分独立恢复机制存在，但总图不自动生成该动作 |
| `restore_checkpoint` | 从检查点恢复 | 否 | 部分独立检查点机制存在，但总图不自动生成该动作 |
| `manual` | 人工处理 | 否 | 目录建议或终态定义；不允许追加执行次数 |
| `stop` | 停止恢复 | 是 | 轮数／预算上限，或不支持继续的技术阻塞；保留未解决状态 |
| `none` | 不采取恢复动作 | 否 | 目录终态定义；不允许追加执行次数 |

## Reviewer 补检请求现状

| 字段 | 当前用途 | 尚存缺口 |
| --- | --- | --- |
| `reason` | 自由文本补检原因 | 不是统一的补检原因码 |
| `missing_aspects` | 缺失方面，传入恢复决策及定向任务 | 仍需验证后续补检是否真正解决缺口 |
| `suggested_focus` | 模型建议的补检方向 | 当前没有独立传入 RecoveryDecision 的路径 |
| `missing_feature_ids` | 恢复策略从逐特征比较提取的缺失特征 | 不是 Reviewer 请求里的原因码；当前读取 unknown／partially_supported |

## 当前验收边界

- 总图的语义补检条件显式检查 `insufficient_evidence` 与 `semantic_evidence`；存在补查请求本身不保证触发恢复。
- 默认替代来源列表为空；`max_rounds=1` 时不会执行第二轮补检。
- 报告保存错误事件与恢复决策，但没有完整呈现每次补检的执行、结果与重新核验关联。
- 单卡运行错误、汇总恢复、研究检查点和总图之间仍有恢复边界；尚不能称端到端自动错误处理已完成。
- 历史离线测试和限定动作验证不等于真实多来源切换及语义补检效果验收。

参考：[既有覆盖审计](experiments/20260928_tool_failure_causality/code_system_status.md)、[本轮实验说明](experiments/20260928_arxiv_web_full_workflow.md)。
