# ARXIV-RATE-01：Provider Access 与 Query Recall 分层审计

日期：2026-09-14

## 1. 结论

本轮没有运行完整 workflow，也没有进入 Query 层修复。完成 provider single-flight 和 BOOTSTRAP-ASYNC-01 后，最小 live smoke 在 Case A（已知 arXiv ID）即以 `ReadTimeout` 失败；没有收到 HTTP response，故 Atom feed 和 entry 均不可判定。Case B/C 按 Gate 合同未发送。

当前唯一有效结论是：

```text
arXiv provider access = FAIL
structured query recall = NOT_MEASURED
query layer decision = NOT ALLOWED
Run E = NOT RUN
```

这也修正 Run D 的表述：Run D 的 arXiv successful search executions 为 0，观测到 `429 / ReadTimeout / CircuitOpen`，不是稳定的 `HTTP 200 + EMPTY`，所以不能称为“arXiv 零召回”。

## 2. 实现

### Provider single-flight

提交：`beef156 fix(arxiv): serialize provider search lifecycles`

新增全进程共享的 arXiv search gate。ResearchTask 和 bootstrap coroutine 仍然可以并行，但每个 `ArxivSearchTool` execution 从以下阶段开始独占 gate：

```text
circuit permission
→ 等待限速
→ HTTP request
→ retry/backoff
→ HTTP retry
→ 返回或最终失败
```

不同 `ArxivSearchTool` 实例共用同一个 gate；另一个 execution 不能在前一个 execution 的 HTTP 在途期间进入，也不能插入其 retry/backoff 链。half-open probe 同样受此 gate 保护，排队调用只会在 probe 完成后重新检查 circuit。

### BOOTSTRAP-ASYNC-01

提交：`9117eba fix(bootstrap): offload synchronous provider calls`

移除了先求值再 `_await(...)` 的调用形式。`ReferenceBootstrapService` 的 `resolve_identifier` 与 `search_known_item` 现在复用 StructuredRetrieval 的 `_invoke_provider`：

- 原生 async provider 在 event-loop thread await；
- 同步 provider 通过 `asyncio.to_thread` 执行；
- 同步函数若返回 awaitable，回到 event loop await。

bootstrap 仍保留 `max_concurrency` 调度；实际同步 arXiv search 进入 worker thread 后，再由全局 single-flight gate 串行化 HTTP 生命周期。

## 3. 最小 Smoke 合同

命令：

```bash
python scripts/arxiv_rate_smoke.py
```

固定三层：

| Case | Query | 目的 |
|---|---|---|
| A | `id:1706.03762` | 已知 ID，验证 provider/网络 |
| B | `ti:"Attention Is All You Need"` | 已知精确英文标题，验证 known-item/title search |
| C | `abs:"music structure analysis" AND abs:"similarity statistics" AND abs:"fine-grained attention"` | Run D 的真实 SearchPlan strict query |

每一层依次检查：

```text
HTTP 200
→ Atom XML 可解析
→ entry 数量
→ 已知项是否匹配
```

A 不是 `VALID_HIT` 时短路 B/C；B 不是 `VALID_HIT` 时短路 C。只有 A/B 均通过且 C 为 `HTTP 200 + 可解析 + 0 entry` 时，`query_layer_decision_allowed=true`。

## 4. Live Smoke 结果

执行环境允许外网访问，配置为：

| 参数 | 值 |
|---|---:|
| endpoint | `https://export.arxiv.org/api/query` |
| min interval | 4 s |
| timeout | 20 s |
| max retries | 1 |
| max retry delay | 5 s |
| retry budget | 45 s |

| Case | HTTP | Atom | Entry | 结果 |
|---|---|---|---|---|
| A：known ID | 未收到 response | 未测量 | 未测量 | `ReadTimeout` / `PROVIDER_ACCESS_FAILURE` |
| B：exact title | 未发送 | 未测量 | 未测量 | `SKIPPED_UPSTREAM_GATE` |
| C：Run D query | 未发送 | 未测量 | 未测量 | `SKIPPED_UPSTREAM_GATE` |

A 已包含 1 次有界 retry，最终仍为 ReadTimeout。因为连 HTTP status 都没有得到，不能讨论 Atom、entry 或查询策略。

机器可读现场：`docs/experiments/ARXIV_RATE_01_2026-09-14/smoke_result.json`。

## 5. 测试

- arXiv provider、single-flight、retry/circuit/config 定向测试：30 项通过；
- bootstrap 与 StructuredRetrieval 异步边界：19 项通过；
- smoke Gate 离线测试覆盖：
  - A/B hit 后 C `200 + EMPTY` 才允许 Query 层判断；
  - A HTTP 429 时 B/C 短路；
  - A HTTP 200 但 Atom parse failure 时 B/C 短路。
- arXiv、bootstrap、StructuredRetrieval、adapter 与配置注入相关回归：81 项通过。

涉及 `asyncio.to_thread` 的测试在允许线程调度的环境执行；命令沙箱会在该边界阻塞。

全套回归除 6 项既有环境跳过外，仅有一个与本项无关的既有失败：`tests/test_browser_playwright.py::test_fetch_collects_rendered_content_and_applies_limits` 的 `_Chromium.launch` mock 不接受运行环境自动注入的 `proxy` 参数。ARXIV-RATE-01 相关测试没有失败。

## 6. 后续 Gate

保持当前顺序，不启动 Run E：

1. 先恢复 Case A 至 `HTTP 200 + Atom parsed + expected entry`；
2. 再验证 Case B 的精确标题命中；
3. 然后才发送 Case C；
4. 仅当 C 为 `HTTP 200 + Atom parsed + 0 entry`，才调查中文 term、`ti/abs/all`、strict/medium/broad、alias/fallback 等 Query 策略。

在 A/B 通过之前，任何“arXiv 零召回”或“SearchPlan query 质量差”的判断都没有有效实验依据。
