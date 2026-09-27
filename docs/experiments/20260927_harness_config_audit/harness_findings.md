# Harness、Reader、Context 与 Usage 审查

本分项完成于 2026-09-27。已实现并用离线回归验证的内容是 Reader 机械状态复用、未知费用表达、批量 Reader 诊断契约。**没有取得有效的本地 Reader A/B 推理样本，也没有证明 Evidence 产出或任务成功率已经提高。** 其他分项见同目录总报告。

## 1. 原始证据与复现范围

只读统计脚本：[analyze_harness_traces.py](analyze_harness_traces.py)，结果：[harness_trace_audit.json](harness_trace_audit.json)。脚本逐次核对 provider_usage → 保存 tokens → summary；从实际 `run_research_task` stage 输出读取新产生的卡，不把 single-task 工作目录中复制的旧成果算成本轮成果。

| 运行 | 模型 | Researcher 成功 Reader 调用 | 重复区间片段 | 空读片段 | 当次 Researcher 原始卡 |
|---|---|---:|---:|---:|---:|
| 09-16 `run-a8cd308…` | DeepSeek V4 Flash | 14 | 5 | 0 | 4 |
| 09-17 `run-d606cd3…` | DeepSeek V4 Flash | 19 | 7 | 0 | 5 |
| 09-24 `run-33cb3cd…` | Qwen 2.5 7B | 6 | 0 | 3 | 2 |
| 09-24 `run-f41ac741…` | Qwen 2.5 7B | 16 | 13 | 0 | 0 |
| 09-24 `single-T-2-…203926…` | Qwen 2.5 7B | 16 | 0 | 8 | 无本轮 stage 卡结果 |

调用支持一次读取多个片段，故“重复片段”不是“重复工具调用”同一单位。重复判定按 task scope、namespace、artifact 和返回区间；不同任务间重复不在这里合并。上表只统计 Researcher；09-17 Reviewer 另有 `0055_reader.json` 的 EOF 空读。

这些历史运行的代码、检索条件、提取点数量和预算不同，因此属于观察性 failure differential，不能拿卡数差异估计纯模型效应。强模型也会重复读，已足以否定“全由小模型能力不足导致”的解释。

## 2. 重复读取与 EOF：证据、机制与最小修复

### 现象与根因

本地整流程原始路径：`docs/experiments/runtime/MF2033k6lC_2026-09-24/run-f41ac741cf6f49deaa52124ae5b23903/`。

- `tools/0003_reader.json` 与 `0004_reader.json` 分别读取 1,205 和 1,504 字符，`has_more=false`。
- 后续 `0005` 至 `0018` 多次读取同样三个摘要。16 次成功 Reader 仅包含 3 个不同区间，累计返回 17,522 字符，独立文本 3,026 字符。
- `0019_reader.json` 因 Reader 次数耗尽被拒；`stages/0007_run_research_task/output.json` 明确记录预算收尾以及 0 张卡。模型把“Reader 预算耗尽”解释为未获取相关全文，机械重复吞噬了可探索预算。
- 单任务 `single-T-2-20260924T203926Z-ab2ff0e7/tools/0011_reader.json` 至 `0018_reader.json` 在 8 个摘要已经返回 `has_more=false` 后各续读一次，全部空文本。

修改前 `core/tool_call_harness.py` 只缓存成功的数据库请求，没有 Reader 已读区间或 EOF ledger；所有 Reader 都递增执行和字符预算。`ReaderTool` 的 Researcher 分支把空读统一记为成功，没有 Reviewer 已具备的 `read_status=artifact_eof`。`_build_context` 仅累积消息，模型需要反复从历史重建机械状态。

### 已落地行为

`ToolCallHarnessConfig.reuse_reader_results` 和 `TaskResearcherConfig.reuse_reader_results` 默认 **false**；父级统一 Harness 配置可以透传此开关。默认保持旧的执行调度，便于消融。

启用后：

1. 成功读取的完整原始 provenance 留在原始 observation；每轮额外展示已读区间、namespace、read_id、has_more。
2. 完全相同且全部成功的请求复用原文本和句柄，标记 `reused_result=true`。不再次执行 Reader，不增加执行/字符预算，不重复制造 trusted read 或 Evidence。
3. 已有非空读取确认当前 Artifact 末端后，起点在末端或之后的请求返回 `artifact_eof`，不再执行 I/O。EOF 不等于整篇论文已验证，也不等于整篇论文都已读。
4. 事实按 `(namespace, artifact_id, read_id)` 保存，EOF 按 `(namespace, artifact_id)` 隔离。模型参数没有 namespace 时，只在已知归属唯一时推断；存在歧义则实际执行工具。
5. 尾部先读后读取未读前段、不同区间、重叠区间、其他 Artifact 均保留；混合 EOF 与新片段的 batch 不整批丢弃。
6. 缓存作用域仅一次 Harness invocation；失败请求与部分失败 batch 不缓存；缓存只用真实 provenance 完整的 Reader 结果。
7. 重放原有非空内容只解除其对应的必读 Artifact 约束；空 EOF 状态不能解除未满足的必读约束。

Researcher Reader 的空读也增加明确 `artifact_eof` 状态。此字段是兼容性扩展；旧字段和原文保持不变。

**限制：** 重放仍消耗一次模型 turn，会把原文再送入累计历史，不能据此声称降低 token。反复调用模型仍可能用尽 `max_turns`；已专门测试这种模型仍会预算终止。混合 batch 中已有片段暂未细分复用；不做任意区间拼接，以免产生伪造 read_id/provenance。该改动改善机械执行语义，尚未证明模型行为改善。

## 3. Evidence 形成与持久化仍存在的缺口

`workflows/research_task.py::_research` 只在 Harness 最终响应解析为 `ResearchFinishDraft` 之后调用 `EvidenceCardBuilder.build`；中途工具回合没有提交部分卡的动作。Harness 异常时 `_partial` 保留 trusted reads/bundles，但返回零 Evidence/card。

这里不能简单说“读取成果完全丢失”：Runtime 已逐次持久化工具观察、request 与 response，部分结果里也保留 reads。真正缺失的是**已经完成语义比较的局部卡无法在任务结束前通过验证并提交**。最终 JSON 失败/上下文溢出可能让本轮全部语义工作无法转成可审 Evidence。

下一步可验证方案：增加任务内有界 `submit_evidence` checkpoint，仍通过原 Builder 的引文、namespace、work、hash、point 绑定核验后幂等保存；Reader 不得自动把全文或关键词匹配转成卡。固定故障注入点，证明“已验证卡可恢复、未验证草稿不升级、无材料仍未知”。本轮没有修改 Evidence 语义或 Reviewer 标准。

## 4. Context：已经定位，尚未解决

`core/tool_call_harness.py::_build_context` 保留所有 user/assistant/tool 消息；新 Reader ledger 只是附加状态，不是压缩策略。`ModelProfile.context_window` 没有在该循环里约束输入加输出空间。

明确原始失败：

- `run-33cb3cd33cca4fb28f4a2bd454c2179a/llm_calls/0018_local-qwen2.5-7b.json`：服务返回 HTTP 400，32768 窗口收到 **57360 input + 4096 completion = 61456**。
- `single-T-2-20260924T203054Z-de022d8d/llm_calls/0001_local-qwen2.5-7b.json`：当时服务窗口 8192，收到 **4193 + 4096 = 8289**，第一次调用即失败。
- 本地成功整流程 Researcher 最大 41 条消息、单次 13,471 输入 token；本轮累计 Researcher 输入 207,796 token。历史强模型 09-16 Researcher 最大单次 33,137 输入 token，某些轨迹在 32768 服务窗口上本就不成立。

这属于模型能力之外的可验证 Harness/配置责任。建议先在 dispatch 前结合冻结的模型窗口、输出 reservation 和准确 tokenizer 做界限检查；超界要记录 `CONTEXT_LIMIT_EXCEEDED` 与当前 task/phase，而不是尝试后再把 HTTP 400 当语义失败。随后做保留原文出处的 task projection，原始轨迹保持完整，模型视图可去掉已覆盖工具全文但保留候选、read_id、验证卡、未决特征和剩余预算。压缩与重试策略必须用固定 Artifact/输入做新消融，本轮没有未经验证地截掉 Evidence。

## 5. Token 与费用

上述 6 份运行共 **242 次模型调用**，逐次 provider_usage → normalized tokens → summary 的 Input/Output/Cached/Reasoning/Total 核对无数值差异。异常调用没有 provider usage 时记录 unavailable；不能把缺失当实际零消耗。cached/reasoning 是子集，不另加到 Total。

原始缺陷：单请求 8192 窗口失败的运行，`usage_unavailable_calls=1`、`amount_rmb=0`，但 `cost_completeness=COMPLETE`。汇总原先仅检查 `unpriced_calls`，未检查 unavailable/incomplete usage。

已修复 `runtime_artifacts.py::_summarize_llm_usage`：

- 总计与每模型只要包含 unpriced 或 usage unavailable/incomplete，就为 `PARTIAL`。
- `amount_rmb=null` 表示总 API token 费用未知；`known_amount_rmb` 仅保存已定价小计。完全可定价时旧数字行为保留。
- Runtime Markdown 显示 `Unknown (priced subtotal …)`，不再把未知总额渲染为 0。
- 单次正常/失败/修复请求依旧通过同一个模型 observer 计数；本轮没有扩大或隐藏计费请求。

这里是按配置单价估算的 API token 费用，**不是已核对账单**。本地 GPU 时长、利用率、电力和租赁成本未采集，属于 Unknown，不能从 UNPRICED 或 API 费用推导免费。

## 6. Runtime 诊断契约

`diagnostics/reader_failures.py` 原先只接受顶层 `artifact_id`。生产已支持 `reads[]` batch，成功 batch 被诊断为 `INCOMPLETE_RECORD`；部分 batch 的子项错误也会失真。

已局部更新到诊断 schema 1.1：按原请求 index、read_results、read_errors 逐项解释，保留 batch_index 和具体 Artifact 错误；单读行为保留。`reader_calls` 仍为工具调用次数，新增 `reader_items`，succeeded/failed/incomplete 是片段项数。成功 batch 与混合成功/失败 batch 都有回归。

仍然不把所有错误叫权限：网络/Provider 失败、请求 schema、EOF、预算拒绝、真实 scope 拒绝、内容缺失、UTF-8/哈希不一致有不同恢复含义。完整跨层错误 taxonomy 与恢复决策属于后续扩展，本补丁仅修正本轮有直接证据的机械状态和诊断误报。

## 7. 本地实验与测试边界

隔离脚本：[replay_reader_local.py](replay_reader_local.py)。同一冻结 NP-1、SearchPlan、09-24 数据库候选和原 Artifact；只启用 Reader，使用生产 Prompt、Builder 和 Qwen 模型，组间仅 `reuse_reader_results` 开关。两组预算相同：10 探索轮、8 次工具、64,000 读取字符、max_tokens=2048、temperature=0；额外有生产收尾/格式修复，不做云端回退。

最终状态见 [reader_ab_outcome.json](reader_ab_outcome.json)。第一次 `reader_local_pair/` 两组首请求均 HTTP 502，0 返回 usage、0 Reader。随后显式 NO_PROXY 的 `reader_local_pair_direct/` 也遇本机端点不可达；父代理健康检查同时确认本机没有端口 8000 监听/隧道。保留失败轨迹，不把这类请求计作有效 A/B 样本。本轮不能对卡数、耗时或 token 改善作正面结论；服务恢复后才可重新执行新的 pair。

离线受影响回归 **101 项全部通过**：

```bash
/home/lya3106643285/miniconda3/envs/Novelty-web/bin/python -m pytest -q \
  tests/test_tool_call_harness.py \
  tests/test_reader_tool_call_harness_integration.py \
  tests/test_task_researcher_workflow.py \
  tests/test_llm_usage_tracking.py \
  tests/test_reader_failure_diagnostics.py \
  tests/test_runtime_artifacts.py
python3 docs/experiments/20260927_harness_config_audit/analyze_harness_traces.py
```

关键断言覆盖：执行次数与模型 turn 区分、预算耗尽后合法精确回看、不重复 trusted reads、失败可重试、跨 invocation 不复用、跨 namespace 不复用 EOF、先读尾部后读取前段、混合 batch 不丢内容、必读约束不被空 EOF 清空、重复模型最终仍停止、未知费用不伪装成零、批量诊断不误报。

## 8. 验收结论

- **已验证解决（确定性离线）**：可选 Reader 精确重放与 EOF 状态执行；namespace/必读约束；未知费用汇总；批量 Reader 诊断契约。
- **已有实现但线上效益未验证**：Reader ledger 是否减少小模型反复动作、是否间接帮助 Evidence 形成。
- **仍未解决**：最终响应前 Evidence checkpoint；输入/输出 context 准入；长历史 projection；语义证据状态与恢复决策的统一 Runtime 解释。
- **不能确认属于模型边界**：当前 Reader 循环和证据零产出仍夹杂 Provider 故障、机械状态缺口、上下文超限；不能据历史数据直接把剩余差距归为 7B 固有能力上限。
