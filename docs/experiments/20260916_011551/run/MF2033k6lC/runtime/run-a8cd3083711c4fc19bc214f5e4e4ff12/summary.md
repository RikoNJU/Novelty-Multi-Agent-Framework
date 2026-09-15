# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-a8cd3083711c4fc19bc214f5e4e4ff12
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-15T17:10:47.514412+00:00
End: 2026-09-15T17:15:51.518894+00:00
Duration: 313912 ms

## Environment

Git Branch: lya
Git Commit: 9c0b3893040e3165729e6c97cf083f5961c16a28
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 19786 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3245 ms |
| plan_research_task | SUCCESS | 2918 ms |
| plan_research_task | SUCCESS | 6144 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 65014 ms |
| run_research_task | SUCCESS | 87709 ms |
| run_research_task | SUCCESS | 88714 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 40350 ms |
| validate_synthesis_input | SUCCESS | 4 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 3705 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 6465 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 66650 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 43982 ms |
| validate_synthesis_input | SUCCESS | 5 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 31373 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 2 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 14 | 14 | 0 | 0 |
| database_search | 34 | 2 | 32 | 0 |
| reader | 21 | 20 | 1 | 0 |
| web_search | 1 | 1 | 0 | 0 |

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
Input tokens: 1033912
Cached input tokens: 103424
Output tokens: 37999
Reasoning tokens: 11004
Total tokens: 1071911
Cost: RMB 3.16448220
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 98 | 1033912 | 103424 | 37999 | 1071911 | 3.16448220 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 4
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: True
Actual next stage: plan_supplement

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 2 | 1 | PASS |
| NP-3 | 2 | 1 | PASS |

### Round 2

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 4
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 2 | 1 | PASS |
| NP-3 | 2 | 1 | PASS |


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
| NP-2 | reviewed | partially_novel | 2 | True |
| NP-3 | insufficient_evidence | - | 0 | True |

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
| NP-1 | insufficient_evidence | - | 0 | True |
| NP-2 | reviewed | partially_novel | 2 | True |
| NP-3 | reviewed | partially_novel | 2 | True |


## Errors

- run_research_task / tool_0004: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0008: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0009: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0013: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0012: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0011: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0014: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0015: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0016: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0017: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0018: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0019: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0023: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0026: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0027: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0029: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0030: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0033: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0034: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0037: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0038: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0039: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0040: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0042: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0050: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0051: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0054: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0055: ValidationError: 1 validation error for SearchExecution
  Value error, completed_at must not be earlier than started_at [type=value_error, input_value={'execution_id': 'sex_c1f...re=None, snippet=None)]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0060: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0063: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0066: HarnessPolicyError: database_search tool-call budget exhausted
- review_evidence / tool_0070: ValidationError: 1 validation error for ConfiguredReaderCall8000_16000
  Value error, provide artifact_id or reads, exclusively [type=value_error, input_value={'reads': None}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
