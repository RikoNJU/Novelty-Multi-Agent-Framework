# API smoke

沿用 `scripts/arxiv_batch_smoke.py --transport api --max-concurrency 4`。

- 本次出口 API 正常：known ID、英文标题、10-ID metadata batch 均成功。严格主题查询返回 HTTP 200 / 真实零结果。另四个并发逻辑请求（两次主题检索、两次 metadata）全部成功。
- 逻辑请求 17；物理请求 7；HTTP 200 7；429 0；retry 0；interval violation 0。
- Runtime Debug 记录 17 个 logical / 7 个 physical，与 scheduler 一致。
- 当前未复现真实 429；429 / Retry-After / budget / circuit 均以离线 fake HTTP 验证，不能推断出口以后不会再次限流。
- [完整指标](metrics/api.json)；Runtime 路径见 JSON 的 `runtime_dir`。早期 smoke 暴露线程上下文和 API logical event 漏记，均已修复，历史运行保留在 runtime/api 和 runtime/api-complete。
