# 错误码与补检/恢复动作码：实现状态核查

2026-09-28，核查版本 `8fd9c6a`。**已有错误事件体系和部分实际恢复调度；不能称两套完整系统都已验收。** 本次只调查与验证，不修改生产实现。

## 两者当前分别是什么

| 项目 | 已实现 | 仍有边界 |
| --- | --- | --- |
| 错误码 `FailureCode` | 27 类，版本化 `FailureEvent`，含位置/对象范围、原始证据引用、原因关联、重试限制及对结论的影响；接入主要 Provider、Researcher、Reviewer 和报告路径 | 定义数量不等于所有码都有事件生产者。静态检索中 `MODEL_USAGE_UNAVAILABLE` / `model.usage_unavailable` 仅见目录定义，未见生产发出位置；原 Runtime 用量缺失另有自己的状态记录。不能声称所有异常和全部 27 码已统一接入 |
| 恢复动作码 `RecoveryAction` | 13 种，`RecoveryDecision` 保存目标点、来源、材料/记录句柄、缺失特征、原因事件和追加次数；实际工作流、任务和工具 registry 已接入 | 总图 `plan_recovery` 实际产生 7 种动作；不是 13 种都自动调度。部分恢复仍需显式调用独立接口 |
| Reviewer 补检需求 `SupplementRequest` | `reason`、`missing_aspects`、`suggested_focus`，以及 Review 中逐特征比较结果；保留模型语义判断 | 主要是自由文本，没有独立且完整的补检原因码目录。当前确定性路由显式读取 missing_aspects 和缺失 feature IDs，未见 suggested_focus 单独传递至 RecoveryDecision 的路径 |

定义见 [failures.py](../../../backend/src/novelty_agent_framework/schemas/failures.py)，补检语义结构见 [domain.py](../../../backend/src/novelty_agent_framework/schemas/domain.py)。

## 实际自动调度的七种动作

| 动作码 | 触发依据与实际约束 |
| --- | --- |
| `read_artifact` | 已有未读材料，绑定 namespace/artifact，仅允许补读；避免同一材料反复进入恢复 |
| `fetch_fulltext` | Reviewer 有语义缺口，已有记录但缺正文；绑定 Provider 和已有记录 ID，每次最多 4 个 |
| `change_provider` | 已执行查询全部技术失败，存在显式配置且未使用的替代来源；复用原计划 |
| `retry_request` | 没有替代来源时，对网络、限流、服务故障按来源追加一次恢复任务；底层 HTTP 重试与预算仍独立约束 |
| `replan_query` | 成功查询零候选，交给模型重新规划方向；不把零命中当作新颖性结论 |
| `research_gap` | 按仍未解决的点/特征建立后续研究任务，语义选词与技术比较仍由模型负责 |
| `stop` | 轮数/预算耗尽，或技术阻塞、模型/核验中断等条件不支持继续研究；保留未解决状态 |

另外六种 `repair_arguments`、`repair_output`、`resume_review`、`restore_checkpoint`、`manual`、`none` 不由当前 `plan_recovery` 直接生成。部分对应模型/Reviewer/检查点的独立机制，部分是目录建议或终态定义；**有动作名称不等于已有自动执行路径**。静态枚举结果见 [implementation_audit.json](implementation_audit.json)。

调用链为错误/覆盖事实 → [recovery_policy.py](../../../backend/src/novelty_agent_framework/core/recovery_policy.py) → [Workflow 定向任务](../../../backend/src/novelty_agent_framework/workflows/novelty.py) → [RecoveryToolRegistry](../../../backend/src/novelty_agent_framework/tools/recovery_registry.py) → Runtime/报告。不是仅新增枚举，但也不是通用自主修复器。

## 与本次 arXiv 故障的关系

1. 406 在当前分类器中映射为 `provider.protocol`，消息明确注明底层原因未确定。这是操作失败分类，**不是已经查明协议根因**；目录名称容易让读者误解，不能据此跳过网络/上游调查。
2. 查询执行器把首个异常之后的查询标为 `not_run`；当前错误事件可记录为 `coverage.not_executed`。这是错误传播事实，不是“小模型选择不检索”。
3. 总图是否再补检受另一层策略控制：默认 `recovery_provider_order` 为空，不自动换来源；若 `max_rounds=1`，到达轮数上限就不追加第二轮。不能因为存在 `change_provider` / `replan_query` 枚举，就声称这次运行已执行这些动作。
4. 406 不在当前自动重试的网络/限流/服务类别内。没有可用替代来源时会停止；这避免盲重试，但“任何首错即停止整个来源查询链”是否过宽，仍需按错误类型与查询作用域验证。

## 已验证和未验证

本次运行现有 `test_recovery_closure.py` 与 `test_structured_retrieval_tool.py`：**48 passed**，见 [JUnit](contract-tests.xml)。另通过真实执行器完成 24 个无模型、无网络的故障注入对照，见 [调查报告](README.md)。这些证明限定条件下的分类和路由行为。

尚未完成：全部错误码生产覆盖审计、独立补检原因码规范、13 种动作的完整执行覆盖、真实多 Provider fallback 和语义补检效果验收。Reviewer 汇总、Researcher 检查点与总图之间仍有显式恢复边界，不是端到端自动恢复已全部贯通。
