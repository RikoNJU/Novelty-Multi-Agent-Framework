# ARXIV-BATCH-01 实验审计

日期：2026-09-15  
分支：`experiment/arxiv-batch-01`  
基线：`lya@6af2b0cbf32f19a5a9384c30e7ab59ca116f24a7`

## 结论

本轮实现完成，但实验验收结论为 **Case 3 / 暂不合流**：进程级统一调度与 Metadata batch 的离线门禁全部通过；真实网络在严格 `>=4s` 发射间隔下仍出现 HTTP 429，冷却后复测又出现 `429 → ReadTimeout`。因此，本进程内部并发不是当前 429 的充分解释。

Provider failure 已与合法空结果分离：只有 `HTTP 200 + 合法 Atom + requested ID 缺失` 返回 `None`；429、连接/读取超时、非合法 XML、重试耗尽均向所有相关调用者抛出异常。

## 实现范围

- 新增进程级单例 `ArxivRequestScheduler`，Search、Known-ID 与 Metadata 共用一个物理请求节拍。
- Metadata 使用 200ms 收集窗口、最多 32 个唯一 ID，并对同 ID 的并发等待者去重。
- Search query 不做 OR 合并，检索语义未改。
- FullText 使用独立 client，不再与 export API 共用 gate。
- 429 优先遵守服务端数字型 `Retry-After`；只有本地 fallback backoff 受上限约束。
- 提供 `scheduler_enabled`、`metadata_batch_enabled`、窗口与最大批量开关；关闭实验优化时仍不恢复 `429 → None` 的旧错误路径。
- Runtime Debug 新增逐条逻辑/物理 provider 事件及请求压缩、批量、状态、等待和耗时汇总。
- 未修改 `StructuredSourceRetrievalTool._enrich_metadata()`、workflow、agent、reviewer 或 renderer。

## 静态审计

`export.arxiv.org/api/query` 的 endpoint 定义和实际 API client 调用仅位于 `arxiv_scheduler.py`。`arxiv.py` 中保留的一处直接 `_client.get()` 只服务于 `arxiv.org/html` 与 `arxiv.org/pdf`，属于任务书明确要求的独立全文域。

## 离线证据

专项命令：

```text
pytest tests/test_arxiv_scheduler.py tests/test_arxiv_tools.py
       tests/test_arxiv_rate_smoke.py tests/test_runtime_artifacts.py
       tests/test_runtime_config_injection.py
```

结果：`51 passed`。

核心并发门禁：

| 检查 | 结果 |
|---|---:|
| Metadata logical requests | 20 |
| Unique IDs | 15 |
| Metadata physical requests | 1 |
| Dedup count | 5 |
| Average/max batch size | 15 / 15 |
| Metadata batch ratio | 20.0 |
| Search/Metadata 最小间隔共享 | PASS |
| 429 batch 所有 Future 抛异常 | PASS |
| ReadTimeout batch 所有 Future 抛异常 | PASS |
| 坏 XML 所有 Future 抛异常 | PASS |
| 合法 Atom 部分缺失仅对应 ID 返回 `None` | PASS |
| Runtime logical/physical 事件与汇总落盘 | PASS |
| 两个实验 feature switch | PASS |

全仓 `-m 'not live'` 回归在本环境未形成可信的完成结果：既有 `tests/test_api.py::test_novelty_health_and_run_lifecycle` 超过 70 秒；单独执行 StructuredRetrieval 异步用例也停在 `asyncio.to_thread`。最小独立命令 `asyncio.run(asyncio.to_thread(lambda: 1))` 在当前容器同样超过 5 秒，而普通 `ThreadPoolExecutor` 和本轮专项并发测试正常。因此这是当前 Python/沙箱的 asyncio worker 环境限制，不应记录为代码回归通过或失败。该环境问题不影响上面的 51 项隔离门禁，但不能记录为“全仓通过”。

## Live smoke

顺序严格为 `A → B → D → C`，B 不通过后不越过门禁。

第一次真实执行：A known-ID 为 200；B exact-title 两次请求均为 429。冷却后第二次执行：A 为 200；B 首次为 429、重试为 ReadTimeout。第二次的物理发射间隔为约 `4000.106ms` 与 `4000.142ms`，`interval_violation_count=0`。

补齐 Case 3 证据后的第三次执行中，A 本身连续两次返回 429；两次响应体均为 `Rate exceeded.`，响应头显示 `server: Google Frontend`，且没有 `Retry-After`，所以调度器分别使用 2 秒、4 秒的 bounded fallback。两次实际发射相隔约 `18390.021ms`（首次响应本身耗时约 16.39 秒），仍无间隔违规。完整响应头、响应体摘录和 UTC 发射时间已保存在 `live_smoke.json`，并保留了第二次执行摘要。

因此 D 与 C 均按协议标为 `SKIPPED_UPSTREAM_GATE`。最新逐请求事实见 `live_smoke.json`。

## 固定 Paper Input 决策

已固定输入：

```text
backups/MF2033k6lC/v2/paper-input/others/paper.json
SHA-256: 89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66
```

任务书要求 A/B/D 通过后再执行 C，并以 `429_count == 0` 作为完整流程前置 Gate。当前 B 连续复现 provider failure，故没有启动高成本 Paper Input 全流程，也没有伪造 Run 1–3。结构化结果见 `full_run_metrics.json`。

## 验收判定

- 统一调度、批处理、去重、异常语义、Runtime Debug：通过。
- 离线 `average_batch_size > 1`、物理请求压缩：通过。
- Live `429_count == 0`：失败。
- 固定 Paper Input 连续两次无 429：未执行（上游 Gate 失败）。
- 总结：**ARXIV-BATCH-01 方案实现完成，但尚不能判定方案有效或进入正式合流。下一步应携带时间戳、响应头、响应体与物理请求序列调查出口 IP / arXiv API 限流。**
