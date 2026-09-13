# Run A：Task 级分析

共同证据身份见 `run_a_workflow_map.md`。任务的稳定唯一键是 `(point_id, task_id)`；`T-1/T-2` 会在不同 point 下重复。

## 汇总

| Metric | Value |
|---|---:|
| Novelty Points | 2 |
| Research Tasks | 4 |
| Tasks started | 4 |
| Tasks completed | 2 |
| Tasks partial | 2 |
| Tasks failed | 0 |
| Tasks with zero candidates（所有 search 合计） | 0 |
| Tasks with zero database candidates | 4 |
| Tasks with zero evidence | 2 |
| Tasks passing Gate A（至少一张卡被接受） | 2 |
| Tasks rejected by Gate A | 0 |
| Tasks not presented to Gate A（零卡） | 2 |

Gate A 是 workflow 聚合门：6 张卡全部接受。这里把接受卡反向归属到任务，不能把“0 rejected”误读为 4 个任务都有效。

## 逐任务结果

| Point ID | Task ID | Language | Status | Candidates | Reads | Evidence | Cards | Gate A | First Failure / Notes |
|---|---|---|---|---:|---:|---:|---:|---|---|
| NP-1 | T-1 | zh | partial | 8（reference） | 0 | 0 | 0 | NOT PRESENTED | `tool_0007`：第 5 次 reference_search 被预算拒绝；database 全空 |
| NP-1 | T-2 | en | completed | ≥8（reference） | 5 | 2 | 2 | PASS 2/2 | database 全空，证据来自 subject references |
| NP-2 | T-1 | zh | partial | 8（reference） | 4 | 0 | 0 | NOT PRESENTED | `tool_0027`：第 5 次 reference_search 被预算拒绝；读了 4 个 artifact 仍无证据 |
| NP-2 | T-2 | en | completed | ≥8（reference） | 5 | 4 | 4 | PASS 4/4 | database 全空，证据来自 subject references |

## 关键观察

1. 两个中文任务均没有 Evidence/Card，两个英文任务贡献全部 6 张最终卡，语言覆盖发生系统性偏斜。
2. 四个任务都至少一次从原论文参考文献召回 8 条，因此不能归类为“零候选”；但 9 次 database_search 全空，且 arXiv 内部执行实际全失败。
3. NP-1/T-1 在成功召回 8 条参考文献后没有 Reader 调用；为何继续重复 search 而未读取，Root Cause 为 `UNKNOWN`。
4. NP-2/T-1 成功 Reader 4 次但未形成证据；模型未产卡的具体判断原因未结构化记录，Root Cause 为 `UNKNOWN`。
5. Runtime stage 四次均为 SUCCESS，任务业务状态必须从各 stage output 的 `task_research_results[0].status` 读取。
