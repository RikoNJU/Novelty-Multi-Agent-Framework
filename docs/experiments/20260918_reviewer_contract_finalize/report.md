# Reviewer 输出契约与预算收尾核对报告

## 机制结果

RC-01 已由生产路径复现并修补：前轮 L0 的模型可见完整结果 schema 包含 `review_evidence`，模型填写后被程序拒绝。本轮单卡和汇总使用不同的严格 Draft schema；预检检查了实际渲染的 schema，且任何可达 `$defs` 均不包含 `ReviewEvidence`。合成非法旧输出仍被拒绝；脚本模型的单次结构纠错使用同一个 Draft schema 后可以完成。此处验证的是输出协议，不是模型服从率。

RC-02 的精确边界已由共享 Harness 的生产函数测试：已返回 3,397 字符、限额 8,000 时，合计申请 6,000 字符会在执行前拒绝，模型收到申请 6,000、剩余 4,603 的工具反馈；随后可缩小请求。第 4 次成功工具调用后，第 5 次不再派发，预留的一次无工具收尾使用 Reviewer Draft 指令，未出现 Researcher 的 `cards=[]` 要求。普通 Researcher 的既有预算回归仍通过。

RC-03 的 `ToolCallBudgetExhausted` 及被包装的预算异常现在按类型归为 `budget_exhausted`；结构和引用错误仍为 `technical_error`。RC-04 仍区分读取观察、模型选择的 read_id 和 Harness 登记的 ReviewEvidence：脚本模型在预算收尾中引用真实正文 read_id 后，单卡可登记准确原文并传给汇总；非法或未引用的读取不会自动升级。现有 Debug 导出测试验证了独立位置的原文、响应附件和关联记录。所有单卡均为运行失败时，汇总不再消耗模型调用。

## L0′/L1′ 实际复验

用户在本轮另行授权后，按固定 NP-3 两卡运行了一次成对 Reviewer-only 复验。第一对两组均形成合法单卡结果，随后执行第二对与各自汇总；未启动 Planner、Researcher、检索或全文重新获取。两组每张卡与汇总的结构校验均通过：**合法单卡 4/4，合法汇总 2/2，输出契约越权 0 次，格式纠错 0 次，预算收尾 0 次**。这些是执行与引用结构结果，不是技术语义正确率。

| 指标 | L0′ 摘要 | L1′ 摘要＋正文 |
|---|---:|---:|
| 模型调用 | 7 | 9 |
| Reader 工具调用 | 4 | 6 |
| 返回字符／去重覆盖 | 4,423／2,710 | 11,997／11,997 |
| 登记 ReviewEvidence | 3 | 7 |
| 单卡结果 | 两张 `reviewed` | 两张 `reviewed` |
| 汇总标签 | `novel` | `partially_novel` |
| Runtime 估算费用 | ¥0.1758768 | ¥0.1936944 |

合计 **16 次模型调用、估算 ¥0.3695712**，从首个请求到末个响应约216秒，低于预检冻结的24次／¥1上限；外部检索或文献获取为0。原始调用、输入、Reader 范围、输出及费用见 `trials/np3_postrepair_pair_20260918/`，结构化统计见其中 `observations.json`。L1′ 的2PS方法片段为正文 Artifact `art_ebc47b0e70f5b363f3d871f2` 的 `[16701,18701)`；WStream 算法前段为 `art_239d9f203a9c73612f1cbbaa` 的 `[16004,18004)`。另外还读取了页面开头和2PS相关工作段；这些不自动成为核心方法的支持证据。

## 引用审计与语义限制

**实际付费汇总输入没有显示任何新登记正文 quote。** 单卡使用 `read_citations` 登记了 L1′ 的7条 ReviewEvidence，但 `feature_comparisons.evidence_refs` 与相关文献引用仍全部指向原摘要 Evidence。旧 `_compact_summary_rows()` 只把被这些字段引用的 ID 放入 `key_quotes`；Runtime 的 `summary_result.rows` 证明两组实际发送的关键摘录都只有原摘要。最终结构化 Review 和本地报告虽然携带7条新证据对象，不能据此声称汇总模型读过这些正文。此问题在付费运行后才由逐项回读发现。

本轮已离线修正装配：将单卡**明确选择并经 Harness 登记**的 ReviewEvidence 也加入汇总 `key_quotes` 与允许引用集合，未自动添加未被选择的全部 ReadObservation。`posthoc-summary-assembly.json` 显示修补后的投影在 L1′ 可携带7条新证据、L0′携带3条；标记为 `sent_to_model=false`，**不冒充已运行的汇总输入或新模型裁定**。新增测试直接验证该路径。

逐条检查 Runtime 工具事件还发现：若单次 Reader 结果同时附带空的 `material_catalog`，旧计数器先看到空列表，会把**非空读取**的 `business_status` 误记为 `EMPTY`。原始 `read_result` 的文本与范围仍在，故上表字符数按实际范围重算；本轮离线修正计数优先级并增加回归。已归档的付费事件不被事后改写。

模型语义也有可复查的过度推断。L0′ 的 WStream 卡仅凭摘要所述窗口划分策略，把未提及的 CMS、最小堆和常数时间查询判为 `contradicted`；2PS 卡虽将F1–F4列为 `unknown`，仍给出 `novel`。L1′ 的2PS方法段确有 `int[] d` 的局部描述，可支持该步骤数据结构的有限比较，却不能证明整篇没有同时采用 CMS 或最小堆；其 F1–F3 `contradicted` 仍只引用摘要 ID。WStream 的算法前段对窗口和元数据有描述，但“采用窗口策略”本身不排除其他机制。两组最终标签不同是一次观察，不能归因于正文带来正确判断，也不构成独立金标准。

本地用生产 `bind_reviews_to_report()` 与 Markdown Renderer 对实际两组汇总各生成了一份 NP-3 演示报告；`report-binding/` 内的摘要来自各自本次 Reviewer 输出，并标明仅为单点局部报告。L1′报告可以定位7条新证据 ID，但原付费汇总没有看到这些正文 quote。前端页面未启动，页面端到端展示未验收。下一步边界集中在模型为特征比较选择正确原文引用，以及正文摘录进入真实汇总后的语义复验；本次不通过重新调用来重置实验预算。
