# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-a27befb0e6b445778d8c3422fd4f71f6
Entrypoint: paper_input
Input Identity: {"paper_json": "backups/MF2033k6lC/v2/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-13T18:05:13.312698+00:00
End: 2026-09-13T18:32:56.414667+00:00
Duration: 1663184 ms

## Environment

Git Branch: lya
Git Commit: 0b3c266c9c6fcd445fecb1c45cb00e4a90a4e7a9
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 334813 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 2777 ms |
| plan_research_task | SUCCESS | 10162 ms |
| plan_research_task | SUCCESS | 2064 ms |
| plan_research_task | SUCCESS | 10693 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 253418 ms |
| run_research_task | SUCCESS | 220131 ms |
| run_research_task | SUCCESS | 211928 ms |
| run_research_task | SUCCESS | 600532 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 1 ms |
| validate_synthesis_input | SUCCESS | 24 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 16249 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 1 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 16 | 14 | 2 | 7 |
| database_search | 9 | 9 | 0 | 9 |
| reader | 14 | 14 | 0 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | OK | 14 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | ERROR | 14 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 49
Input tokens: 309768
Cached input tokens: 204800
Output tokens: 19266
Reasoning tokens: 6091
Total tokens: 329034
Cost: RMB 0.27486900
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 49 | 309768 | 204800 | 19266 | 329034 | 0.27486900 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: PASS
Input final valid Cards: 6
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 2 | 1 | PASS |
| NP-2 | 4 | 1 | PASS |


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


## Errors

- run_research_task / tool_0007: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0027: HarnessPolicyError: reference_search tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
