# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-f41ac741cf6f49deaa52124ae5b23903
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-24T20:55:34.849797+00:00
End: 2026-09-24T20:57:33.957143+00:00
Duration: 119123 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: 7e03fcca3eee05c9ce7b06ee9e74b5818b833726
Model: openai_compatible / qwen2.5-7b-instruct
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 28147 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3801 ms |
| plan_research_task | SUCCESS | 6088 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 63739 ms |
| run_research_task | SUCCESS | 7599 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 2 ms |
| validate_synthesis_input | SUCCESS | 1 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 9466 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 1 ms |
| render_report | SUCCESS | 1 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| database_search | 4 | 1 | 3 | 0 |
| reader | 17 | 16 | 1 | 0 |
| reference_search | 1 | 1 | 0 | 1 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 17 | 1 | OTHER | `diagnostics/reader.json` |
| reference_namespace | ERROR | 17 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: OTHER=1

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 30
Input tokens: 226576
Cached input tokens: 0
Output tokens: 3204
Reasoning tokens: 0
Total tokens: 229780
Cost: RMB 0.00000000
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 30 | 226576 | 0 | 3204 | 229780 | 0.00000000 | 30 |

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


## Reviewer Information Adjudication

### Stage stage_0010

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


## Errors

- run_research_task / tool_0001: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0019: HarnessPolicyError: reader tool-call budget exhausted
- run_research_task / tool_0020: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0021: ToolExecutionError: all 1 search executions failed

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
