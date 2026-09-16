# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-d36b9cc71aac4891bd09e05ac8eb7602
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T15:00:25.075496+00:00
End: 2026-09-16T15:08:14.397917+00:00
Duration: 469359 ms

## Environment

Git Branch: lya
Git Commit: 68dcaad43a0178aa1f200446fd5704e5b15ddd40
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 15964 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 4060 ms |
| plan_research_task | SUCCESS | 7769 ms |
| plan_research_task | SUCCESS | 9377 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 190013 ms |
| run_research_task | SUCCESS | 98816 ms |
| run_research_task | SUCCESS | 139715 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 45276 ms |
| validate_synthesis_input | SUCCESS | 5 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 5065 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3840 ms |
| plan_research_task | SUCCESS | 8611 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 118844 ms |
| run_research_task | SUCCESS | 108817 ms |
| validate_evidence | SUCCESS | 3 ms |
| review_evidence | SUCCESS | 42377 ms |
| validate_synthesis_input | SUCCESS | 6 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 17382 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 5 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| database_search | 44 | 17 | 27 | 5 |
| reference_search | 7 | 7 | 0 | 7 |
| reader | 21 | 21 | 0 | 0 |
| web_search | 5 | 5 | 0 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 21 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 21 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=13

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 98
Input tokens: 1074401
Cached input tokens: 108288
Output tokens: 28316
Reasoning tokens: 539
Total tokens: 1102717
Cost: RMB 3.18566940
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 98 | 1074401 | 108288 | 28316 | 1102717 | 3.18566940 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 1
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: True
Actual next stage: plan_supplement

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 0 | 1 | INSUFFICIENT |
| NP-3 | 1 | 1 | PASS |

### Round 2

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
| NP-2 | 0 | 1 | INSUFFICIENT |
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
| NP-1 | insufficient_evidence | - | 0 | True |
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 1 | True |

### Stage stage_0023

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
| NP-3 | reviewed | novel | 1 | False |


## Errors

- run_research_task / tool_0006: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0009: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0014: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0015: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0017: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0018: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0020: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0023: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0024: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0026: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0029: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0033: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0035: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0036: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0039: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0041: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0045: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0046: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0055: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0058: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0059: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0062: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0066: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0067: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0069: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0071: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0075: HarnessPolicyError: database_search tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
