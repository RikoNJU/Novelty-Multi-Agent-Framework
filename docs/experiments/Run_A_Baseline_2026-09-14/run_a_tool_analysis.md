# Run A：Tool 级分析

## Runtime Tool Call 汇总

`SUCCESS`、`EMPTY`、`FAILED` 在本表中互斥；Runtime summary 的 `success` 包含正常返回的 EMPTY，因此数值口径不同。

| Tool | Calls | Success（非空/可用） | Empty | Failed | Success Rate | Empty Rate |
|---|---:|---:|---:|---:|---:|---:|
| reference_search | 16 | 7 | 7 | 2 | 43.75% | 43.75% |
| database_search | 9 | 0 | 9 | 0（外层） | 0.00% | 100.00% |
| reader | 14 | 14 | 0 | 0 | 100.00% | 0.00% |
| web_search | 0 | 0 | 0 | 0 | N/A | N/A |
| browser | 0 | 0 | 0 | 0 | N/A | N/A |
| evidence card builder | 0（非 Tool） | 6 张卡 | 0 | 0 | N/A | N/A |

Web Search 与 Browser 在冻结配置中 disabled。Evidence Card 由 Researcher 输出模型生成，不是 Harness Tool Call。

## database_search 内部执行

9 次外层 Tool Call 均为 `SUCCESS + EMPTY`。展开 `raw_result.payload.search_executions` 后：

| Provider | Internal executions | Succeeded | Empty | Failed | Failure detail |
|---|---:|---:|---:|---:|---|
| null_catalog | 24 | 24 | 24 | 0 | 测试型空目录，预期 NULL_QUERY |
| arxiv | 30 | 0 | 0 | 30 | 25 `ReadTimeout`，5 HTTP 429 |

5 次 arXiv 外层调用（`tool_0003`, `tool_0009`, `tool_0018`, `tool_0030`, `tool_0036`）各含 6 次 failed internal execution，却全部向 Agent 返回 `succeeded: true`、`results: []`，因此被 Runtime 计为 EMPTY 而非 FAILED。影响所有 4 个任务。

## reference_search

- 非空成功：7 次，每次 `result_count=8`。
- 空结果：7 次。
- PRE_TOOL 失败：2 次，均为 `reference_search tool-call budget exhausted`。
- 失败调用：`tool_0007`（NP-1/T-1）和 `tool_0027`（NP-2/T-1）。

## Reader

14/14 次执行成功，Reader diagnostic 为 `OK`，无 WRONG_NAMESPACE、LOST_MANIFEST_ENTRY、NEVER_PERSISTED、FILE_NOT_FOUND 或 PARSE_ERROR。Reader 返回结果能够给出实际 namespace，6 条最终 Evidence 均可反向解析到 `subject_reference` artifact。

## LLM

| Metric | Value |
|---|---:|
| Calls | 49 |
| Successful | 49 |
| Failed | 0 |
| Input tokens | 309,768 |
| Cached input tokens | 204,800 |
| Output tokens | 19,266 |
| Reasoning tokens | 6,091 |
| Total tokens | 329,034 |
| Cost | RMB 0.274869 |

`extract_points` 单阶段耗时 334.8 秒，接近但未超过其 600 秒配置上限；这次不是失败，不进入业务修复 Backlog。
