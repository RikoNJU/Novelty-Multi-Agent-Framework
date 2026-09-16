# 并发验收

## Provider smoke（已完成）

沿用 smoke，max_concurrency=4，8 个公开主题通过四个线程提交，同一进程共享 Web Session。8/8 有 SearchHit；物理请求 8，HTTP 200 8，interval violation 0；最小实际间隔 8000.1 ms（配置 8000 ms）。

每个 physical event 包含 request_id、task_id、transport、operation、dispatch_at、previous_request_interval_ms、status_code、attempt、elapsed_ms。不同 Session 的共享间隔和共享熔断另有离线并发测试。

[指标和事件](metrics/parallel.json)，Runtime 目录：`docs/experiments/ARXIV_LIMIT_FINAL_2026-09-16/runtime/parallel-provider/arxiv-provider-smoke/runtime/run-20260916T040519749569Z-a6fb02dd76`。

## PaperInput NP-2 全任务并发

第二轮已完成：任务层配置 max_concurrency=4，已有 NP-2 计划包含 T-1(zh)、T-2(en) 两个任务，均正常执行完毕。两个任务于 04:11:07.576802 / 04:11:07.585640 UTC 启动（相差 8.84 ms）。16 个 HTTP dispatch 来自这两个 task_id，全部 200，最小间隔 8000.10 ms，0 violation。总耗时 246.88 秒。

[正式工作流派生审计](metrics/workflows.json)，原始两阶段 meta 与请求事件位于 runtime/parallel/MF2033k6lC/runtime/。
