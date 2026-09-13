# Part 1 Phase 2：统一修复 Backlog

所有条目共享以下基线：

- Run ID：`run-a27befb0e6b445778d8c3422fd4f71f6`
- Git Commit：`0b3c266c9c6fcd445fecb1c45cb00e4a90a4e7a9`
- Paper Input SHA256：`89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66`
- Runtime Root：`outputs/MF2033k6lC/runtime/run-a27befb0e6b445778d8c3422fd4f71f6/`

## BUG-001：标准 PaperInput 配置未执行实际 Reviewer 裁定

### Priority
P0

### Status
CONFIRMED

### Evidence
- Point ID：NP-1、NP-2
- Runtime Artifact：`stages/0014_review_evidence/output.json`
- Diagnostic Artifact：`diagnostics/reviewer.json`
- Config：`fixtures/experiments/run_a/effective-config.json` 中 `reviewer.enabled=false`

### Symptom
review stage 正常返回，但两个 point 都只有 `insufficient_evidence` 占位 review，verdict/reason/confidence 为空，Reviewer LLM/Reader 调用均为 0。

### Expected
标准全量 PaperInput Pipeline 应明确执行实际 Reviewer，或明确规定该入口不包含 Reviewer；不能把占位输出当成已完成裁定继续形成强结论。

### Actual
工作流继续通过 Gate A/B、综合与渲染，并以 Runtime SUCCESS 结束。

### Failure Layer
Configuration / Workflow

### Root Cause
默认冻结配置明确设置 `reviewer.enabled=false`；这是 Reviewer 未调用的直接原因。产品层应默认启用还是应阻断下游，当前契约为 `UNKNOWN`。

### Impact
全部 point 与最终报告；关键裁定角色没有执行。

### Reproduction
用 Run A fixture 和配置执行 PaperInput Pipeline，检查 stage_0014 与 reviewer diagnostic。

### Proposed Fix Scope
先定义标准入口的 Reviewer 启用/禁用契约和 fail-closed 行为；涉及配置默认值、workflow routing 与验收测试。本条不处理 Reviewer→Report schema 映射。

## BUG-002：Reviewer 结果未进入 Coordinator/NoveltyReport/Renderer

### Priority
P0

### Status
CONFIRMED

### Evidence
- Point ID：NP-1、NP-2
- Runtime Artifact：`stages/0014_review_evidence/output.json`, `stages/0017_synthesize_report/output.json`, `stages/0020_render_report/output.json`
- Diagnostic Artifact：`diagnostics/reviewer.json`
- Business Artifact：`novelty-reviews.json` 两条 insufficient；`report.json` 两条 strong

### Symptom
Reviewer 状态为 insufficient、verdict 为空时，最终报告仍独立给出两个 `strong` 结论，Renderer 原样展示。

### Expected
最终报告结论必须受权威 Reviewer 裁定约束，并保留可追溯的 verdict/reason/highly_relevant_works；不足证据不得静默变成 strong。

### Actual
`_synthesize_report()` 不向 Coordinator 传 novelty_reviews；NoveltyReport schema 与 Renderer 输入也没有闭合该业务链。

### Failure Layer
Workflow / Schema / Agent / Renderer

### Root Cause
Reviewer→Coordinator 调用契约缺失、NoveltyReport 未承接 Reviewer 语义、Renderer 不读取 reviews 均已确认。`novel/partially_novel/not_novel` 与 `strong/partial/weak/insufficient` 的权威语义和映射仍为 `UNKNOWN`。

### Impact
最终报告核心结论可能与审查裁定冲突，影响整个实验有效性。

### Reproduction
比较同一 Run A 的 `novelty-reviews.json`、`report.json` 和 rendered Markdown；检查 workflow synthesis 参数。

### Proposed Fix Scope
先决定 Reviewer 是否为新颖性裁定唯一业务真值，再闭合 Reviewer→Coordinator/Report Schema（P0-A），最后闭合 Report→Renderer（P0-B）；禁止先硬编码枚举映射。

## BUG-003：arXiv 内部全失败却被 database_search 标记为 SUCCESS/EMPTY

### Priority
P0

### Status
CONFIRMED

### Evidence
- Point ID：NP-1、NP-2
- Task ID：全部 4 个任务
- Tool Call ID：`tool_0003`, `tool_0009`, `tool_0018`, `tool_0030`, `tool_0036`
- Runtime Artifact：相应 `tools/*_database_search.json`
- Diagnostic Artifact：无专用 Search diagnostic；`summary.json` Tool 表显示 9 次 EMPTY、0 FAILED

### Symptom
30/30 arXiv internal execution 失败（25 timeout、5 HTTP 429），但 5 个外层 Tool Call 全部是 execution_status SUCCESS、business_status EMPTY、succeeded true。

### Expected
后端全部失败应结构化暴露 FAILED 或明确的 degraded/error 状态，不能与真实零命中合并。

### Actual
Agent 与 Runtime 看到的是“数据库检索召回 0 个候选作品”，丢失“检索没有成功执行”的业务区别。

### Failure Layer
Tool / Harness / Normalization

### Root Cause
外层 database_search 成功包装了含 failed search_executions 的空 ResearchBundle。网络超时/429 的更深层原因是 `UNKNOWN`。

### Impact
全部任务；数据库证据覆盖为零，且 Runtime 顶层统计会误导基线判断，属于系统性失败与观测失真。

### Reproduction
Single Task 使用 Run A 的任一 point/task SearchPlan 调用 arxiv source；对比外层 tool record 与 `raw_result.payload.search_executions`。

### Proposed Fix Scope
定义 internal execution→Tool observation 的状态聚合规则；保留 EMPTY 与 FAILED 分离，并为 mixed/partial 情况提供明确结构化状态和测试。

## BUG-004：中文任务重复 reference_search 后耗尽预算且零证据

### Priority
P1

### Status
CONFIRMED

### Evidence
- Point ID / Task ID：NP-1/T-1、NP-2/T-1
- Tool Call ID：`tool_0007`, `tool_0027`
- Runtime Artifact：上述 tool JSON 与 `stages/0009_run_research_task/output.json`, `stages/0011_run_research_task/output.json`
- Diagnostic Artifact：`diagnostics/reader.json`（Reader 本身无失败）

### Symptom
两个中文任务均以 partial 返回、零 Evidence/Card；第 5 次 reference_search 在 PRE_TOOL 被 Harness 拒绝。

### Expected
在固定预算内利用已有非空候选进行 Reader/Evidence 构建，或以结构化不足原因结束，不应靠预算拒绝终止循环。

### Actual
NP-1/T-1 已召回 8 条但从未读取；NP-2/T-1 读了 4 条但未产 Evidence；二者最终都再次调用 reference_search 并超限。

### Failure Layer
Agent / Harness

### Root Cause
预算上限和第 5 次调用被拒绝已确认；模型为何重复检索、NP-1 为何不读、NP-2 为何读后不产证据均为 `UNKNOWN`。

### Impact
2/4 tasks，导致全部中文 evidence 缺失，最终报告仅由英文任务支撑。

### Reproduction
用 Single Task 精确运行 NP-1/T-1 或 NP-2/T-1，保持 Run A SearchPlan 与预算配置。

### Proposed Fix Scope
先在 BUG-003 修复后复现；审计 Researcher 状态转移、候选去重、Reader 触发与完成条件，不先扩大预算或调 Prompt。

## BUG-005：Reference Namespace diagnostic 对新 Reader 契约产生假阳性

### Priority
P1

### Status
CONFIRMED

### Evidence
- Point ID / Task ID：所有发生 Reader 的任务
- Tool Call ID：`tool_0010` 等 14 个 Reader Call
- Runtime Artifact：`tools/0010_reader.json`
- Diagnostic Artifact：`diagnostics/reference_namespace.json`（28 errors）与 `diagnostics/reader.json`（14/14 OK）

### Symptom
每个成功 Reader Call 都被 namespace diagnostic 同时报 `namespace mismatch` 和 `invalid namespace`。

### Expected
新 Reader 契约下，应根据 artifact 归属/返回结果 namespace 验证，不应要求已删除的请求参数。

### Actual
resolved arguments 没有 namespace，结果中有合法 `subject_reference`；诊断器比较 `None != subject_reference` 并解析 `ArtifactNamespace(None)`。

### Failure Layer
Harness / Runtime Diagnostic

### Root Cause
诊断逻辑仍假设旧 Reader 请求包含 namespace。

### Impact
current-run reference diagnostic 状态被错误标成 ERROR，产生 28 条噪声，降低 Runtime 证据可信度；业务 Reader 与 6 条 Evidence binding 实际正常。

### Reproduction
对 Run A 执行 `scripts/reference_namespace_diagnostics.py outputs/MF2033k6lC --run-id run-a27befb0e6b445778d8c3422fd4f71f6`。

### Proposed Fix Scope
仅修诊断器契约适配：从 read result/manifest 解析实际 namespace，并增加无 request namespace 的 current-run 测试；不得改变 Reader 业务行为。

## 已关闭/不建 Bug 的已知项

- Reader namespace/artifact lookup：Run A 14/14 成功，Reader diagnostic OK；未复现 KNOWN-02 的业务失败。
- `.txt` artifacts：48/48 manifest artifacts 的 extension/media_type/role 一致，0 integrity failure；Run A 没有证据支持扩展名错误。若产品要求保留原始 PDF，应另立需求而非把本次文本 artifact 当作 bug。
- Renderer 文件生成：成功。Renderer 的问题是 BUG-002 的业务语义输入断链，不是文件写入失败。
