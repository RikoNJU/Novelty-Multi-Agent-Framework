# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-d20cf7604f34411abe224ba46f4c7006
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T14:42:38.792535+00:00
End: 2026-09-16T14:46:38.680863+00:00
Duration: 239921 ms

## Environment

Git Branch: lya
Git Commit: 68dcaad43a0178aa1f200446fd5704e5b15ddd40
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 9829 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 13465 ms |
| plan_research_task | SUCCESS | 4453 ms |
| plan_research_task | SUCCESS | 3787 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 105216 ms |
| run_research_task | SUCCESS | 119922 ms |
| run_research_task | SUCCESS | 141232 ms |
| validate_evidence | SUCCESS | 3 ms |
| review_evidence | SUCCESS | 31410 ms |
| validate_synthesis_input | SUCCESS | 12 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 35235 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 3 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 6 | 6 | 0 | 6 |
| database_search | 18 | 9 | 9 | 2 |
| reader | 22 | 22 | 0 | 0 |
| web_search | 3 | 2 | 1 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 22 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 22 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | OK | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=12

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 66
Input tokens: 582367
Cached input tokens: 38912
Output tokens: 22540
Reasoning tokens: 279
Total tokens: 604907
Cost: RMB 1.84489860
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 66 | 582367 | 38912 | 22540 | 604907 | 1.84489860 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: PASS
Input final valid Cards: 4
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 1 | 1 | PASS |
| NP-2 | 2 | 1 | PASS |
| NP-3 | 1 | 1 | PASS |


## Reviewer Information Adjudication

### Stage stage_0012

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
| NP-1 | reviewed | partially_novel | 1 | False |
| NP-2 | reviewed | partially_novel | 2 | False |
| NP-3 | reviewed | partially_novel | 1 | False |


## Errors

- run_research_task / tool_0010: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0013: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0015: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0016: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0018: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0023: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0030: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0031: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0033: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0035: HarnessPolicyError: reader required after database_search returned artifact_ids

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
