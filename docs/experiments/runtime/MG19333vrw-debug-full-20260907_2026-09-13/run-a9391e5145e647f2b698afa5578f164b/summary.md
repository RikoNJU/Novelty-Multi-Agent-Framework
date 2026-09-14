# Runtime Summary

## Run

Paper ID: MG19333vrw-debug-full-20260907
Run ID: run-a9391e5145e647f2b698afa5578f164b
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MG19333vrw-debug-full-20260907/paper-input/others/paper.json", "paper_sha256": "183b58191547b78b92ec264d24c1abc5429d1637fbd74bbf7af8f40678cc69f4", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: FAILED
Start: 2026-09-13T23:05:41.048223+00:00
End: 2026-09-13T23:18:23.633584+00:00
Duration: 762613 ms

## Environment

Git Branch: lya
Git Commit: c9a5fab087f3f7f753491d18cfb2fcd36ce90d80
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 20911 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3094 ms |
| plan_research_task | SUCCESS | 2286 ms |
| plan_research_task | SUCCESS | 2323 ms |
| plan_research_task | SUCCESS | 2113 ms |
| plan_research_task | SUCCESS | 2523 ms |
| plan_research_task | SUCCESS | 5347 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 723550 ms |
| run_research_task | SUCCESS | 723534 ms |
| run_research_task | SUCCESS | 723532 ms |
| run_research_task | SUCCESS | 723611 ms |
| run_research_task | SUCCESS | 82 ms |
| run_research_task | SUCCESS | 81 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 1 ms |
| validate_synthesis_input | SUCCESS | 2 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | FAILED | 110 ms |
| plan_supplement | NOT_RUN | - ms |
| validate_report_integrity | NOT_RUN | - ms |
| persist_report | NOT_RUN | - ms |
| render_report | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 4 | 4 | 0 | 4 |
| database_search | 4 | 0 | 4 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | OK | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 26
Input tokens: 37971
Cached input tokens: 9728
Output tokens: 6022
Reasoning tokens: 1563
Total tokens: 43993
Cost: RMB 0.07092270
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 26 | 37971 | 9728 | 6022 | 43993 | 0.07092270 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 0
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 0 | 1 | INSUFFICIENT |
| NP-3 | 0 | 1 | INSUFFICIENT |


## Reviewer Information Adjudication

### Stage stage_0018

Stage status: SUCCESS
Cards preserved: True
Supplement requests control route: False
Missing reviews: []
Unexpected reviews: []
Duplicate reviews: []
Unresolved Evidence IDs: []
Actual next stage: validate_synthesis_input

| Novelty Point | Status | Verdict | Relevant Works | Supplement |
|---|---|---|---:|---|
| NP-1 | insufficient_evidence | - | 0 | True |
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 0 | True |


## Errors

- run_research_task / tool_0005: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0006: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0007: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0008: ToolExecutionError: all 6 search executions failed
- synthesize_report / -: ModelClientError: 模型 HTTP 调用失败: 402 {"code":30001,"message":"Sorry, your account balance is insufficient","data":null}
- - / -: ModelClientError: 模型 HTTP 调用失败: 402 {"code":30001,"message":"Sorry, your account balance is insufficient","data":null}

## Integrity Gates

- validate_synthesis_input: PASS

## Last Completed Stage

check_final_evidence_sufficiency
