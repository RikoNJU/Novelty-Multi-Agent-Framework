# PERF-001：arXiv 检索性能 Run C 审计

## 1. 结论

结果：`PASS（结构性关闭）`。

PERF-001 的三条因果链均已关闭：

- 同步 provider I/O 已移入 worker thread，真实 arXiv outer call 出现跨 ResearchTask 重叠；
- transport/provider failure 不再触发语义 fallback，每个失败 outer call 只产生 1 条 FAILED `SearchExecution`；
- arXiv retry 成本有界，连续最终失败会打开线程安全熔断器，后续调用能够 fast-fail。

Run C 总时长从问题 Run 的 `1,362.539 s` 降至 `183.200 s`，减少 `86.56%`，约为原来的 `1/7.44`。该总时长对比受 SearchPlanner 产出任务数不同影响，因此只作为辅助结果；PERF-001 的关闭依据是可直接观察的控制流和并发结构变化。

## 2. 实现提交

| 阶段 | Commit | 内容 |
|---|---|---|
| Phase A | `3f8b326` | sync search/metadata/full-text provider I/O 移出 event loop |
| Phase B | `672ea75` | provider failure 后停止剩余 query fallback chain |
| Phase C | `0f239b9` | transport retry、总预算、线程安全 circuit breaker |

## 3. Run C 冻结身份

| 项目 | 值 |
|---|---|
| Paper ID | `MG19333vrw-debug-full-20260907` |
| Run ID | `run-5f78c1dade354974856fb7270ec04c89` |
| 入口 | `paper_input` |
| PaperInput | `outputs/MG19333vrw-debug-full-20260907/paper-input/others/paper.json` |
| PaperInput SHA-256 | `183b58191547b78b92ec264d24c1abc5429d1637fbd74bbf7af8f40678cc69f4` |
| Git commit | `0f239b91484cc8d11a61b2e263714b087675d6b1` |
| 最大轮数 | `1` |
| 最大并发 | `4` |
| 模型 | `openai_compatible / deepseek-v4-flash` |
| API endpoint | `https://api.deepseek.com` |
| 开始时间（UTC） | `2026-09-14T04:23:09.443677+00:00` |
| 结束时间（UTC） | `2026-09-14T04:26:09.768435+00:00` |
| Runtime duration | `183,200 ms` |
| Run status | `SUCCESS` |

arXiv 有效配置：

```text
timeout_seconds=20
max_retries=1
max_retry_delay_seconds=5
retry_budget_seconds=45
min_interval_seconds=4
circuit_failure_threshold=2
circuit_cooldown_seconds=60
```

临时 API Key 只通过 `/tmp/deepseek_api_key` 注入单次进程；Run C 完成后该文件已删除。Runtime 和审计文档均不包含 Key。

## 4. 问题 Run 与 Run C 对照

问题 Run：`run-269799e73e0d4e60b84543f854691c6b`。

| 指标 | 问题 Run | Run C | 观察 |
|---|---:|---:|---|
| total wall-clock | 1,362.539 s | 183.200 s | 减少 86.56%，约 7.44× 加速 |
| `run_research_task` critical path | 1,234.325 s | 44.880 s | 约 27.5× 加速 |
| `database_search` calls | 9 | 5 | Run C：3 arXiv + 2 null_catalog |
| failed outer calls | 5 | 3 | Run C 三次均保持 FAILED |
| failed `SearchExecution` | 30 | 3 | 减少 90% |
| execution / failed outer | 6 | 1 | 达到 Phase B 目标 |
| fallback after transport failure | 5 个 outer 均存在 | 0 | 达到 Phase B 目标 |
| failed outer duration sum | 1,223.675 s | 74.668 s | Run C 两个长调用存在重叠 |
| cross-task arXiv overlap | 基本无 | 约 35.3 s | 达到 Phase A 目标 |
| circuit-open fast fail | 无 | `tool_0008`，outer 11 ms | 达到 Phase C 目标 |
| Reader / Evidence | 0 | 0 | 仅观察，不是 PERF-001 强制标准 |

## 5. Run C `database_search` 时间轴

| Tool | Source | Task | Outer 开始（UTC） | Outer 结束（UTC） | 时长 | SearchExecution | 结果 |
|---|---|---|---|---|---:|---:|---|
| `tool_0004` | arXiv | NP-1/T-2 | `04:25:21.300439` | `04:25:59.461964` | 38.741 s | 1 | FAILED：`ReadTimeout` |
| `tool_0005` | arXiv | NP-2/T-2 | `04:25:21.398055` | `04:25:56.733699` | 35.916 s | 1 | FAILED：HTTP 429 |
| `tool_0006` | null_catalog | NP-2/T-2 | `04:25:57.869182` | `04:25:57.883056` | 12 ms | 6 | SUCCESS + EMPTY |
| `tool_0008` | arXiv | NP-2/T-2 | `04:26:00.379041` | `04:26:00.392148` | 11 ms | 1 | FAILED：`ArxivCircuitOpenError` |
| `tool_0009` | null_catalog | NP-1/T-2 | `04:26:00.513738` | `04:26:00.526872` | 11 ms | 6 | SUCCESS + EMPTY |

`tool_0004` 与 `tool_0005` 在 `04:25:21.398055` 至 `04:25:56.733699` 间重叠约 `35.336 s`。这直接证明一个同步 arXiv 请求等待期间，另一个 ResearchTask 仍能进入并推进自己的数据库调用。

前两个 arXiv 调用都在熔断打开前进入。`tool_0005` 首先完成最终失败，`tool_0004` 随后完成第二次连续最终失败并打开 circuit；约 0.92 秒后的 `tool_0008` 没有发送新的 HTTP 请求，而是以 `ArxivCircuitOpenError` 在毫秒级返回。

两个 null_catalog 调用均为成功执行但零命中，并继续完成 S1、S1-fb1、S2、S2-fb1、S3、S3-fb1 六条放宽链。这说明 Phase B 只截断 FAILED，未破坏 SUCCESS + EMPTY 的 fallback 语义。

## 6. 测试

- Phase A 定向及相关回归：34 项通过；
- Phase B 定向及相关回归：60 项通过；
- Phase C 完整定向回归：101 项通过；
- 三阶段完成后 broad regression：通过，6 项按既有环境条件跳过；
- `git diff --check` 与修改文件语法编译通过。

线程相关测试必须在非沙箱环境执行，因为当前命令沙箱连最小 `asyncio.to_thread(time.sleep, 0.01)` 都无法调度完成；相同测试在非沙箱 Python 环境正常通过。

## 7. 对比限制与非目标

Run C 的 SearchPlanner 对 NP-2/T-1、NP-3/T-1、NP-3/T-2 三个任务连续 3 次返回非合法 JSON，因此只生成并运行 3 个 ResearchTask；问题 Run 运行了 5 个 ResearchTask。故总 wall-clock 的 7.44× 改进不能全部归因于 PERF-001。

以下证据不受该混杂因素影响，仍可直接用于关闭 PERF-001：

- 两个真实 arXiv outer call 的 35.3 秒重叠；
- 每次 transport failure 后剩余 fallback 为 0；
- FAILED execution / outer 从 6 降为 1；
- 连续失败后的 circuit-open 调用在约 11 ms 内返回；
- Runtime 中 ReadTimeout、HTTP 429、CircuitOpen 均保持 FAILED，没有降格为 EMPTY。

Agent 层重复调用、SearchPlanner JSON 稳定性、Reader 对 `artifact_id='none'` 的调用以及最终 0 Evidence 均不属于 PERF-001，本报告不顺手修复。

## 8. 验收判定

| 验收项 | 结果 |
|---|---|
| sync provider 不阻塞 event loop | PASS |
| search / metadata / full-text 统一 async boundary | PASS |
| SUCCESS + EMPTY 才允许 fallback | PASS |
| transport/provider failure 停止 fallback | PASS |
| Runtime FAILED 状态保持真实 | PASS |
| ReadTimeout/ConnectTimeout/ConnectError 有界重试 | PASS |
| HTTP 429/5xx 有界重试 | PASS |
| retry/backoff 总预算 | PASS（45 s） |
| circuit state 线程安全 | PASS |
| cooldown 单 probe、成功关闭、失败重开 | PASS |
| 持续故障 fast-fail | PASS |
| PERF-001 | CLOSED |

## 9. 可追溯产物

Runtime 现场：

```text
outputs/MG19333vrw-debug-full-20260907/runtime/run-5f78c1dade354974856fb7270ec04c89/
```

自动归档：

```text
docs/experiments/runtime/MG19333vrw-debug-full-20260907_2026-09-14/
└── run-5f78c1dade354974856fb7270ec04c89/
```

关键 SHA-256：

| 产物 | SHA-256 |
|---|---|
| Run result | `1f261163ef8a02823a411a1307299cdbe43c8636e488a9d598908e494950eaec` |
| Runtime manifest | `e5c78b04e45f57b6fb654f3f23a4a7f26b68f14680190e6973244c601167ef09` |
| Runtime summary.json | `6fe6791474ee0d8de0360d715eefeed88efa30cc8033bacd273f91a827e854b5` |
