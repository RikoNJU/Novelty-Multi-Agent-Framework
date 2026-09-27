# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-d55196716d254641a84cf1b0c19f14e9
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/local-llm-full-workflow/0002/paper-input.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-27T15:09:50.968667+00:00
End: 2026-09-27T15:11:22.624710+00:00
Duration: 91665 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: b378e443e36d9d662c2e5c8937c4dfd25ee27bdc
Model: openai_compatible / qwen2.5-7b-instruct
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 35601 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 6069 ms |
| plan_research_task | SUCCESS | 4232 ms |
| plan_research_task | SUCCESS | 6316 ms |
| plan_research_task | SUCCESS | 6093 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 5525 ms |
| run_research_task | SUCCESS | 3851 ms |
| run_research_task | SUCCESS | 3869 ms |
| run_research_task | SUCCESS | 4613 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 3 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 15251 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 1 ms |
| render_report | SUCCESS | 1 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| database_search | 4 | 0 | 4 | 0 |
| reference_search | 4 | 4 | 0 | 4 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | OK | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 20
Input tokens: 71360
Cached input tokens: 0
Output tokens: 3613
Reasoning tokens: 0
Total tokens: 74973
Estimated API cost (RMB): Unknown (priced subtotal 0.00000000)
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 20 | 71360 | 0 | 3613 | 74973 | Unknown (priced subtotal 0.00000000) | 20 |

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
| NP-4 | 0 | 1 | INSUFFICIENT |


## Reviewer Information Adjudication

### Stage stage_0014

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
| NP-4 | insufficient_evidence | - | 0 | True |


## Errors

- run_research_task / tool_0001: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0003: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0005: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0007: ToolExecutionError: all 1 search executions failed

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
