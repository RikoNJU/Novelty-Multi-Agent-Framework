# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-fa94c2d3e79041b397470b6d9ba7e956
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: FAILED
Start: 2026-09-27T20:05:57.391561+00:00
End: 2026-09-27T20:11:09.325248+00:00
Duration: 311958 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: 145723771fb615916f1fdd8199b21c603d31b59c
Model: openai_compatible / qwen2.5-7b-instruct
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 22640 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 4350 ms |
| plan_research_task | SUCCESS | 6163 ms |
| plan_research_task | SUCCESS | 5999 ms |
| plan_research_task | SUCCESS | 5612 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 68577 ms |
| run_research_task | SUCCESS | 194107 ms |
| run_research_task | SUCCESS | 4168 ms |
| run_research_task | SUCCESS | 4 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 37 ms |
| validate_synthesis_input | SUCCESS | 1 ms |
| check_final_evidence_sufficiency | SUCCESS | 2 ms |
| synthesize_report | FAILED | 1 ms |
| plan_supplement | NOT_RUN | - ms |
| validate_report_integrity | NOT_RUN | - ms |
| persist_report | NOT_RUN | - ms |
| render_report | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| database_search | 3 | 2 | 1 | 0 |
| reader | 11 | 11 | 0 | 0 |
| reference_search | 1 | 1 | 0 | 1 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | OK | 11 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | ERROR | 11 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 25
Input tokens: 190455
Cached input tokens: 0
Output tokens: 9709
Reasoning tokens: 0
Total tokens: 200164
Estimated API cost (RMB): Unknown (priced subtotal 0.00000000)
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 25 | 190455 | 0 | 9709 | 200164 | Unknown (priced subtotal 0.00000000) | 24 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 1
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 1 | 1 | PASS |
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

- run_research_task / tool_0014: no_search_execution: database search produced no search executions
- synthesize_report / -: ModelCallBudgetExceeded: model_call_budget_exhausted
- - / -: ModelCallBudgetExceeded: model_call_budget_exhausted

## Integrity Gates

- validate_synthesis_input: PASS

## Last Completed Stage

check_final_evidence_sufficiency
