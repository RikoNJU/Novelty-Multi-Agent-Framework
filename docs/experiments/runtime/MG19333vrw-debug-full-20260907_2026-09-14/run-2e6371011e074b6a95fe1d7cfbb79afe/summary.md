# Runtime Summary

## Run

Paper ID: MG19333vrw-debug-full-20260907
Run ID: run-2e6371011e074b6a95fe1d7cfbb79afe
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MG19333vrw-debug-full-20260907/paper-input/others/paper.json", "paper_sha256": "183b58191547b78b92ec264d24c1abc5429d1637fbd74bbf7af8f40678cc69f4", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-14T05:53:01.919666+00:00
End: 2026-09-14T05:55:41.418523+00:00
Duration: 159511 ms

## Environment

Git Branch: lya
Git Commit: a0b0b75714bf3795732618fee228acb42c4a86a7
Model: openai_compatible / deepseek-v4-flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 12710 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 9029 ms |
| plan_research_task | SUCCESS | 16939 ms |
| plan_research_task | SUCCESS | 6159 ms |
| plan_research_task | SUCCESS | 14116 ms |
| plan_research_task | SUCCESS | 14359 ms |
| plan_research_task | SUCCESS | 22816 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 44557 ms |
| run_research_task | SUCCESS | 52372 ms |
| run_research_task | SUCCESS | 40205 ms |
| run_research_task | SUCCESS | 49056 ms |
| run_research_task | SUCCESS | 13329 ms |
| run_research_task | SUCCESS | 11181 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 7314 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 2 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 19 | 19 | 0 | 19 |
| database_search | 15 | 6 | 9 | 6 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | OK | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 54
Input tokens: 188582
Cached input tokens: 160896
Output tokens: 27583
Reasoning tokens: 20645
Total tokens: 216165
Cost: RMB 0.00000000
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-v4-flash | 54 | 188582 | 160896 | 27583 | 216165 | 0.00000000 | 54 |

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

- run_research_task / tool_0008: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0006: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0011: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0005: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0009: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0020: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0021: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0030: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0033: ToolExecutionError: all 1 search executions failed

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
