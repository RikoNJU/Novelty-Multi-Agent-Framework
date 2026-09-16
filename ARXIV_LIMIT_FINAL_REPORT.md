# arXiv 限流最终验收报告（2026-09-16）

限流相关工程能力已完成收口，三轮真实工作流已执行，未调用 MinerU。开发分支为 `fix/arxiv-rate-limit-final`，基于 `origin/lya@43ba4fb`；仅移植 hyl 的 arXiv Web 能力，没有整分支合并。

## 结论

1. **arXiv API 的 429 不保证消失。** 本次真实 API smoke 恰好恢复为 HTTP 200，不能推断其他出口或时段不会再次受限。
2. **系统能够受控处理 API 限流。** 进程共享调度、有限重试、Retry-After、预算、熔断和恢复路径均有离线验证；本次 API 的 17 次逻辑请求合并为 7 次物理请求，Runtime 计数一致，0 间隔违规。
3. **Web 已提供真实可运行的替代路径。** API 不可用时可显式配置 Web；本次 Web 独立完成检索、产物落盘、Reader、EvidenceCard、Reviewer 和 Renderer。这里不把本次可用的 API 说成“当前不可用”，也未添加自动切换机制。

## 验收结果

| 项目 | 结果 |
|---|---|
| 定向离线测试 | 154 passed |
| 完整离线回归 | 830 passed，6 skipped；1 个原始 lya 已存在的 Reader 旧断言失败 |
| Web 间隔阶梯 | 8/6/4/2 秒各 8 次主题检索，32/32 有 SearchHit，0 间隔违规 |
| 默认 Web 间隔 | 保留 8 秒；小样本和重复查询不足以证明 2 秒长期安全 |
| 四并发 provider smoke | 8/8 命中，0 间隔违规 |
| Run 1：单 ResearchTask | 成功；17 次读取、3 张缓存参考文献卡，213.91 秒 |
| Run 2：NP-2 全部任务 | 成功；两任务启动相差 8.84 ms，16 次 HTTP 200，246.88 秒 |
| Run 3：完整 PaperInput 工作流 | 成功；986.37 秒，最终 3 张卡，其中 2 张来自本次 Web 新候选；Reviewer 与 Renderer 完成 |
| 完整工作流物理请求 | 39 次：37 次 200、2 次 406；0 重试、0 间隔违规，最小间隔 8000.07 ms |
| 故障与零命中 | 真实 406 被记录为 FAILED / PROVIDER_FAILED，未伪装 EMPTY；成功零结果独立标识 ZERO_RESULT |
| 完整性 Gate | 两次证据 Gate 与最终报告 Gate 全部通过 |

Run 1 的 NP-2 未采纳新候选生成卡；Web 新候选成卡由 Run 3 的 NP-1 / NP-3 真实任务补证，最终两张卡均通过来源核验并保留在报告中。没有人为修改研究结论来让单任务验收通过。

## 修改与边界

- Web 通道传播明确异常，阻止故障后的伪 fallback；已有成功候选与失败执行分开保存。
- 所有 Web Session 共用进程级闸门；Web 全文与重定向每跳也受控。Research Task max_concurrency 保持 4。
- Web 增加有限重试、总预算和 CLOSED / OPEN / HALF_OPEN 单探测熔断，复用已有失败阈值配置。
- 接入现有 Runtime Debug，补 API 漏记的逻辑事件、批次 task_ids、熔断和 API/Web 汇总。
- 未修改 SearchPlanner、Reviewer、Renderer、检索词质量或 fallback 相关性策略。

单进程共享调度不等于跨进程/跨主机出口协调。真实 406、检索相关性和已有 Reader schema 测试问题仍需分别处理；它们没有被隐藏或混为限流工程故障。当前可移除“请求失控、故障伪空、并发无全局节流”这一 arXiv 阻塞项，不代表对所有检索质量或服务端可用性作保证。

## 交付

- `9222d37`：生产修复与 Runtime Debug。
- `674c7ff`：离线测试、hyl 页面夹具与现有 smoke 扩展。
- 实验归档与本报告独立提交，包含下述验收记录。

[实验总览](docs/experiments/ARXIV_LIMIT_FINAL_2026-09-16/README.md) · [基线](docs/experiments/ARXIV_LIMIT_FINAL_2026-09-16/baseline.md) · [工作流审计](docs/experiments/ARXIV_LIMIT_FINAL_2026-09-16/metrics/workflows.json) · [新 Web 候选证据来源](docs/experiments/ARXIV_LIMIT_FINAL_2026-09-16/metrics/web-card-provenance.json) · [最终业务报告](docs/experiments/ARXIV_LIMIT_FINAL_2026-09-16/runtime/full/MF2033k6lC/report/MF2033k6lC-report.md)
