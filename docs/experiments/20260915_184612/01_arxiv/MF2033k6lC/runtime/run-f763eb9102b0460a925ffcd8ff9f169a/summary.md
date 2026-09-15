# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-f763eb9102b0460a925ffcd8ff9f169a
Entrypoint: paper_input
Input Identity: {"paper_json": "docs/experiments/20260915_172846/input/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-15T10:14:00.002792+00:00
End: 2026-09-15T10:21:48.037131+00:00
Duration: 468064 ms

## Environment

Git Branch: experiment/arxiv-batch-01
Git Commit: 5e2a00532dceeb27ceebfe9aa5fe383bcc96eaf4
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 108791 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3034 ms |
| plan_research_task | SUCCESS | 6061 ms |
| plan_research_task | SUCCESS | 3700 ms |
| plan_research_task | SUCCESS | 5480 ms |
| plan_research_task | SUCCESS | 6328 ms |
| plan_research_task | SUCCESS | 5357 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 83732 ms |
| run_research_task | SUCCESS | 105131 ms |
| run_research_task | SUCCESS | 55790 ms |
| run_research_task | SUCCESS | 77010 ms |
| run_research_task | SUCCESS | 40776 ms |
| run_research_task | SUCCESS | 43500 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 60617 ms |
| validate_synthesis_input | SUCCESS | 3 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 7736 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3146 ms |
| plan_research_task | SUCCESS | 6817 ms |
| plan_research_task | SUCCESS | 2866 ms |
| plan_research_task | SUCCESS | 2983 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 62684 ms |
| run_research_task | SUCCESS | 55304 ms |
| run_research_task | SUCCESS | 55638 ms |
| run_research_task | SUCCESS | 60598 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 43996 ms |
| validate_synthesis_input | SUCCESS | 3 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 17515 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 1 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 43 | 38 | 5 | 8 |
| database_search | 35 | 0 | 35 | 0 |
| reader | 39 | 32 | 7 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 39 | 7 | WRONG_NAMESPACE | `diagnostics/reader.json` |
| reference_namespace | ERROR | 39 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: WRONG_NAMESPACE=7

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 142
Input tokens: 931433
Cached input tokens: 660736
Output tokens: 43751
Reasoning tokens: 12560
Total tokens: 975184
Cost: RMB 1.40407080
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 142 | 931433 | 660736 | 43751 | 975184 | 1.40407080 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 3
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: True
Actual next stage: plan_supplement

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 3 | 1 | PASS |
| NP-2 | 0 | 1 | INSUFFICIENT |
| NP-3 | 0 | 1 | INSUFFICIENT |

### Round 2

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
| NP-1 | 3 | 1 | PASS |
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
| NP-1 | reviewed | novel | 3 | False |
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 0 | True |

### Stage stage_0033

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
| NP-1 | reviewed | novel | 2 | True |
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 0 | True |


## Errors

- run_research_task / tool_0005: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0006: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0007: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0008: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0009: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0011: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0019: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0028: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0029: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0032: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0034: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0036: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0040: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0042: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0047: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0049: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0050: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0051: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0062: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0064: HarnessPolicyError: reference_search tool-call budget exhausted
- review_evidence / tool_0065: ValueError: unknown artifact_id 'art_ea01d9c5f48ad68092a07bf7' in the research manifest
- review_evidence / tool_0066: ValueError: unknown artifact_id 'art_ea01d9c5f48ad68092a07bf7' in the research manifest
- review_evidence / tool_0067: ValueError: unknown artifact_id 'art_6f98816ebc9005d24844fdfd' in the research manifest
- review_evidence / tool_0068: ValueError: unknown artifact_id 'art_ea01d9c5f48ad68092a07bf7' in the research manifest
- review_evidence / tool_0069: ValueError: unknown artifact_id 'art_ea01d9c5f48ad68092a07bf7' in the research manifest
- run_research_task / tool_0074: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0076: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0078: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0079: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0080: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0081: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0082: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0083: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0088: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0094: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0102: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0103: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0104: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0106: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0110: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0111: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0112: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0114: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0115: HarnessPolicyError: reference_search tool-call budget exhausted
- review_evidence / tool_0116: ValueError: unknown artifact_id 'art_ea01d9c5f48ad68092a07bf7' in the research manifest
- review_evidence / tool_0117: ValueError: unknown artifact_id 'art_b8b821043e4485fda0b8527c' in the research manifest

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
