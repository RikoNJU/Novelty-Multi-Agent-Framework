# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-e5eac9bc62204cc8b77e2ab334a58a0c
Entrypoint: paper_input
Input Identity: {"paper_json": "docs/experiments/20260916_203750/input/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T12:38:07.642779+00:00
End: 2026-09-16T12:40:25.307589+00:00
Duration: 137694 ms

## Environment

Git Branch: lya
Git Commit: ce3c20d809ea484aaea7f4e4f71adebf07238330
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 10899 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 2318 ms |
| plan_research_task | SUCCESS | 7098 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 45487 ms |
| run_research_task | SUCCESS | 77557 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 22619 ms |
| validate_synthesis_input | SUCCESS | 12 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 16812 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 3 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 5 | 5 | 0 | 0 |
| database_search | 9 | 4 | 5 | 0 |
| reader | 19 | 17 | 2 | 0 |
| web_search | 1 | 1 | 0 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 19 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 19 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=18

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 51
Input tokens: 523833
Cached input tokens: 66304
Output tokens: 20561
Reasoning tokens: 555
Total tokens: 544394
Cost: RMB 1.57752720
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 51 | 523833 | 66304 | 20561 | 544394 | 1.57752720 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: PASS
Input final valid Cards: 5
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 3 | 1 | PASS |
| NP-2 | 2 | 1 | PASS |


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
| NP-1 | reviewed | partially_novel | 3 | True |
| NP-2 | reviewed | partially_novel | 2 | False |


## Errors

- run_research_task / tool_0007: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0010: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0012: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0015: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0018: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0019: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0021: ToolExecutionError: all 1 search executions failed

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
