# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-cb9a3ecc9c4a4a57896cf12fa7b62706
Entrypoint: paper_input
Input Identity: {"paper_json": "docs/experiments/20260915_172846/input/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-15T10:24:05.645740+00:00
End: 2026-09-15T10:34:12.451069+00:00
Duration: 606855 ms

## Environment

Git Branch: experiment/arxiv-batch-01
Git Commit: 5e2a00532dceeb27ceebfe9aa5fe383bcc96eaf4
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 149900 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 6855 ms |
| plan_research_task | SUCCESS | 3915 ms |
| plan_research_task | SUCCESS | 7180 ms |
| plan_research_task | SUCCESS | 6586 ms |
| plan_research_task | SUCCESS | 3631 ms |
| plan_research_task | SUCCESS | 4756 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 112701 ms |
| run_research_task | SUCCESS | 147058 ms |
| run_research_task | SUCCESS | 70736 ms |
| run_research_task | SUCCESS | 146056 ms |
| run_research_task | SUCCESS | 32573 ms |
| run_research_task | SUCCESS | 47741 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 73623 ms |
| validate_synthesis_input | SUCCESS | 5 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 11030 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 5075 ms |
| plan_research_task | SUCCESS | 4122 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 70325 ms |
| run_research_task | SUCCESS | 78386 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 76021 ms |
| validate_synthesis_input | SUCCESS | 7 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 24007 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 2 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 31 | 26 | 5 | 10 |
| database_search | 29 | 3 | 26 | 0 |
| reader | 45 | 36 | 9 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 45 | 9 | WRONG_NAMESPACE | `diagnostics/reader.json` |
| reference_namespace | ERROR | 45 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: OTHER=3, WRONG_NAMESPACE=6

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 128
Input tokens: 990679
Cached input tokens: 805376
Output tokens: 44128
Reasoning tokens: 15449
Total tokens: 1034807
Cost: RMB 1.19467380
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 128 | 990679 | 805376 | 44128 | 1034807 | 1.19467380 | 0 |

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
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 2 | 1 | PASS |
| NP-3 | 1 | 1 | PASS |

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
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 2 | 1 | PASS |
| NP-3 | 1 | 1 | PASS |


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
| NP-2 | reviewed | novel | 2 | True |
| NP-3 | insufficient_evidence | - | 0 | True |

### Stage stage_0029

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
| NP-2 | reviewed | novel | 2 | False |
| NP-3 | insufficient_evidence | - | 0 | True |


## Errors

- run_research_task / tool_0009: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0008: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0013: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0022: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0024: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0011: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0012: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0025: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0027: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0029: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0028: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0030: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0031: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0046: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0047: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0050: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0057: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0061: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0064: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0069: HarnessPolicyError: total tool-call budget exhausted
- review_evidence / tool_0070: ValueError: unknown artifact_id 'art_6f98816ebc9005d24844fdfd' in the research manifest
- review_evidence / tool_0071: ValueError: unknown artifact_id 'art_d88778158223021b818fdd97' in the research manifest
- review_evidence / tool_0072: ValueError: unknown artifact_id 'art_6f98816ebc9005d24844fdfd' in the research manifest
- run_research_task / tool_0079: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0080: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0081: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0082: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0089: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0090: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0093: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0094: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0095: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0097: HarnessPolicyError: reference_search tool-call budget exhausted
- review_evidence / tool_0098: ValueError: unknown artifact_id 'art_d88778158223021b818fdd97' in the research manifest
- review_evidence / tool_0099: ValueError: unknown artifact_id 'art_6f98816ebc9005d24844fdfd' in the research manifest
- review_evidence / tool_0100: PermissionError: artifact 'none' is outside reviewer scope
- review_evidence / tool_0101: ValueError: unknown artifact_id 'art_d88778158223021b818fdd97' in the research manifest
- review_evidence / tool_0102: PermissionError: artifact 'x' is outside reviewer scope
- review_evidence / tool_0103: PermissionError: artifact 'none' is outside reviewer scope

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
