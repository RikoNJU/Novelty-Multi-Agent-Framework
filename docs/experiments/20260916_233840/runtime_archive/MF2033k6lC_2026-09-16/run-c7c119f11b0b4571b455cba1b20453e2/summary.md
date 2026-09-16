# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-c7c119f11b0b4571b455cba1b20453e2
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T14:49:00.398723+00:00
End: 2026-09-16T14:58:20.559715+00:00
Duration: 560202 ms

## Environment

Git Branch: lya
Git Commit: 68dcaad43a0178aa1f200446fd5704e5b15ddd40
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 20084 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 4776 ms |
| plan_research_task | SUCCESS | 8540 ms |
| plan_research_task | SUCCESS | 3777 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 171227 ms |
| run_research_task | SUCCESS | 164501 ms |
| run_research_task | SUCCESS | 217292 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 39425 ms |
| validate_synthesis_input | SUCCESS | 10 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 15120 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 34732 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 143486 ms |
| validate_evidence | SUCCESS | 3 ms |
| review_evidence | SUCCESS | 22920 ms |
| validate_synthesis_input | SUCCESS | 18 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 49138 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 4 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 7 | 7 | 0 | 7 |
| database_search | 28 | 14 | 14 | 3 |
| reader | 33 | 33 | 0 | 0 |
| web_search | 2 | 2 | 0 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 33 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 33 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=27

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 96
Input tokens: 1005526
Cached input tokens: 87296
Output tokens: 34679
Reasoning tokens: 2340
Total tokens: 1040205
Cost: RMB 3.09298980
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 96 | 1005526 | 87296 | 34679 | 1040205 | 3.09298980 | 0 |

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
| NP-1 | 2 | 1 | PASS |
| NP-2 | 0 | 1 | INSUFFICIENT |
| NP-3 | 1 | 1 | PASS |

### Round 2

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
| NP-1 | 2 | 1 | PASS |
| NP-2 | 1 | 1 | PASS |
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
| NP-1 | insufficient_evidence | - | 2 | True |
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 1 | True |

### Stage stage_0021

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
| NP-1 | insufficient_evidence | - | 2 | True |
| NP-2 | insufficient_evidence | - | 1 | True |
| NP-3 | insufficient_evidence | - | 1 | True |


## Errors

- run_research_task / tool_0011: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0017: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0018: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0020: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0022: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0024: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0028: ValueError: unknown or invalid database source record: src_bff4fd2540ef918936a57847
- run_research_task / tool_0029: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0037: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0040: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0052: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0053: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0056: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0060: ToolExecutionError: all 1 search executions failed

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
