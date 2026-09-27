# 3.2 / 3.10 调用前机械状态投影闭环

日期：2026-09-28。范围为 `core/tool_call_harness.py`、`tests/test_context_projection.py` 与离线归档；未调用真实模型，未修改 ContextAdmission 或 Evidence 原文。

## 审查结论与最小实现

原 Harness 已有完整 assistant/tool 轨迹、Reader 缓存状态和部分预算提示：Reader 提示依赖 `reuse_reader_results`，预算提示依赖 finalization/report 开关；没有每次调用都可见的 Provider 历史失败、持久化 checkpoint 边界和统一任务状态。因此新增独立的 `runtime_state_projection: false` 开关（默认兼容；schema/factory/TaskResearcher 由协作代理接线）。

启用后，每个 exploration/finalization 模型请求只插入一条 `MACHINE_RUNTIME_STATE` system 消息；下一次调用重新投影，不将状态消息写回长期 trace。不新增模型调用、不概括论文内容、不裁剪任何原始 user/assistant/tool 消息。状态来自本次调用的实际计数器和已发生 observation：

- 探索模型调用、工具调用、Reader 字符与各工具的剩余预算；最终收束是否在 max_turns 内明确显示。该 Harness 不拥有全局 RuntimeBudget，投影明确标记其为外部预算，避免捏造剩余量。
- Reader 按 namespace / artifact ID / SHA 隔离，记录去重范围；非空成功读取才建立已知尾部。读到尾部不等于已读前段；空读取不证明全文尾部；不同版本不合并。
- Provider 最新结果和历史失败/部分失败数量同时保留，后续成功不抹掉 first/last failure。成功执行返回零候选与 Provider 失败明确区分，均不推断语义上的“无匹配文献”。
- 必读 artifact IDs；成功且 durable 的 Builder checkpoint 和卡 ID。字段明确为 `builder_provenance_only`，Validator/Reviewer accepted 与语义充分性均为 Harness 未确定。
- invocation / paper / run / point / task / attempt 标识；状态对象只存在于单次 run 的局部变量。串行复用及并发同实例调用均隔离。

预算终止仍保留 trace 与此前 checkpoint；另修正 Reader 实际返回字符超出契约时先记录其真实 observation、再结束预算，避免已经发生的读结果从 Harness trace 消失。

## 可复查结果

`context_projection_tests.log` / `.xml`：**100 passed**（新增 12 项，连同 Harness、Reader 集成及 ContextAdmission）。覆盖预算计数、Provider fail→success、durable 边界、EOF 前段与 namespace、实际 research_task.attempt 位置、串行/并发隔离、预算 finalization、Reader 返回量超限、30 次重复读取长轨迹，以及带状态的最终序列化输入仍接受调用级精确计数与预发送拒绝。ContextAdmission 注入的是明确声明的 fixture token 数，没有把字符数冒充真实 tokenizer 计数。

`probe_context_projection_offline.py` 固定工具/模型响应，唯一区别是 projection 开关；完整 before/after 请求在 `context_projection_offline/{mixed,long}_{off,on}.json`，汇总及源码 SHA 在同目录 `summary.json`。

| 离线轨迹 | off / on 模型 fixture 调用 | off / on 物理工具调用 | on 单请求状态条数 | 原始非 system 历史 |
| --- | --- | --- | --- | --- |
| 失败→成功→读取→checkpoint→EOF replay | 6 / 6 | 4 / 4 | 始终 1 | 逐条一致 |
| 同一读取重复 30 次后结束 | 31 / 31 | 1 / 1 | 始终 1 | 逐条一致 |

长轨迹 Reader 范围/EOF 状态在首次读后不再膨胀，30 次工具消息仍完整保留。最后完整上下文的序列化字符数从 off 32,800 到 on 34,137；这是新增状态的可观察开销，**不是节省 token 的实验结果**。mixed 为 3,590 / 6,268 字符。所有字符数仅作归档体积度量。重复工具模型仍会用完模型轮数，max_turns 负责有界停止；上下文增长仍由既有 ContextAdmission 在真实调用边界测量和拒绝，projection 并未解决模型语义策略或长历史压缩。

## 复现

```bash
/home/lya3106643285/miniconda3/envs/Novelty-web/bin/python docs/experiments/20260927_harness_config_closure/probe_context_projection_offline.py
/home/lya3106643285/miniconda3/envs/Novelty-web/bin/python -m pytest tests/test_context_projection.py tests/test_tool_call_harness.py tests/test_reader_tool_call_harness_integration.py tests/test_context_admission.py -o addopts='' -q
```

本项可验收的是显式机械状态、原文/轨迹保留与有界行为；没有声称该开关改善真实模型卡片质量、减少调用或完成完整文献覆盖。
