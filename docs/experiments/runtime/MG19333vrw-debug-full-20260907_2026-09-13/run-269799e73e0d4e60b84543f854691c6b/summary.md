# Runtime Summary

## Run

Paper ID: MG19333vrw-debug-full-20260907
Run ID: run-269799e73e0d4e60b84543f854691c6b
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MG19333vrw-debug-full-20260907/paper-input/others/paper.json", "paper_sha256": "183b58191547b78b92ec264d24c1abc5429d1637fbd74bbf7af8f40678cc69f4", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-13T23:33:42.014109+00:00
End: 2026-09-13T23:56:24.518965+00:00
Duration: 1362522 ms

## Environment

Git Branch: lya
Git Commit: c9a5fab087f3f7f753491d18cfb2fcd36ce90d80
Model: openai_compatible / deepseek-v4-flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 7519 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 24161 ms |
| plan_research_task | SUCCESS | 27918 ms |
| plan_research_task | SUCCESS | 16695 ms |
| plan_research_task | SUCCESS | 20754 ms |
| plan_research_task | SUCCESS | 13720 ms |
| plan_research_task | SUCCESS | 10931 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 1013627 ms |
| run_research_task | SUCCESS | 1234325 ms |
| run_research_task | SUCCESS | 1012857 ms |
| run_research_task | SUCCESS | 1013326 ms |
| run_research_task | SUCCESS | 218881 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 1 ms |
| validate_synthesis_input | SUCCESS | 2 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 6182 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 2 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 15 | 15 | 0 | 15 |
| database_search | 9 | 4 | 5 | 4 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | OK | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 48
Input tokens: 156208
Cached input tokens: 68992
Output tokens: 32070
Reasoning tokens: 24625
Total tokens: 188278
Cost: RMB 0.00000000
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-v4-flash | 48 | 156208 | 68992 | 32070 | 188278 | 0.00000000 | 47 |

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

### Stage stage_0017

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

- run_research_task / tool_0008: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0009: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0011: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0023: ToolExecutionError: all 6 search executions failed

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
