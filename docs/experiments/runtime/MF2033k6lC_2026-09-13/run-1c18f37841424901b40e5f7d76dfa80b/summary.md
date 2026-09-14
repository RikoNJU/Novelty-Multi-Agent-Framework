# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-1c18f37841424901b40e5f7d76dfa80b
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-13T21:13:58.376883+00:00
End: 2026-09-13T22:07:15.578017+00:00
Duration: 3197292 ms

## Environment

Git Branch: lya
Git Commit: f800449a84c69c98cdf249ce325a635915af9fbf
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 328001 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3739 ms |
| plan_research_task | SUCCESS | 3727 ms |
| plan_research_task | SUCCESS | 1622 ms |
| plan_research_task | SUCCESS | 151009 ms |
| plan_research_task | SUCCESS | 1754 ms |
| plan_research_task | SUCCESS | 102321 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 2055425 ms |
| run_research_task | SUCCESS | 1677607 ms |
| run_research_task | SUCCESS | 1157333 ms |
| run_research_task | SUCCESS | 2306414 ms |
| run_research_task | SUCCESS | 520651 ms |
| run_research_task | SUCCESS | 878757 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 29298 ms |
| validate_synthesis_input | SUCCESS | 16 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 18971 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 1 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 28 | 23 | 5 | 8 |
| database_search | 18 | 9 | 9 | 5 |
| reader | 25 | 22 | 3 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 25 | 3 | WRONG_NAMESPACE | `diagnostics/reader.json` |
| reference_namespace | ERROR | 25 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: WRONG_NAMESPACE=3

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 88
Input tokens: 687399
Cached input tokens: 509440
Output tokens: 32478
Reasoning tokens: 9902
Total tokens: 719877
Cost: RMB 0.48950550
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 88 | 687399 | 509440 | 32478 | 719877 | 0.48950550 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 3
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 0 | 1 | INSUFFICIENT |
| NP-3 | 3 | 1 | PASS |


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
| NP-3 | reviewed | partially_novel | 3 | True |


## Errors

- run_research_task / tool_0005: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0006: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0008: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0012: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0023: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0029: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0043: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0045: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0052: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0056: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0059: ToolExecutionError: all 6 search executions failed
- run_research_task / tool_0062: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0066: ToolExecutionError: all 6 search executions failed
- review_evidence / tool_0069: ValueError: unknown artifact_id 'art_6f98816ebc9005d24844fdfd' in the research manifest
- review_evidence / tool_0070: ValueError: unknown artifact_id 'art_6f98816ebc9005d24844fdfd' in the research manifest
- review_evidence / tool_0071: ValueError: unknown artifact_id 'art_6f98816ebc9005d24844fdfd' in the research manifest

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
