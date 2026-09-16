# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-063681ec4a1046b99be3a1ce43f54c77
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T15:22:53.041609+00:00
End: 2026-09-16T15:28:28.514483+00:00
Duration: 335508 ms

## Environment

Git Branch: lya
Git Commit: 68dcaad43a0178aa1f200446fd5704e5b15ddd40
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 10363 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 8021 ms |
| plan_research_task | SUCCESS | 7092 ms |
| plan_research_task | SUCCESS | 8083 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 93782 ms |
| run_research_task | SUCCESS | 72498 ms |
| run_research_task | SUCCESS | 128724 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 19263 ms |
| validate_synthesis_input | SUCCESS | 5 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 3424 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 6325 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 88218 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 40365 ms |
| validate_synthesis_input | SUCCESS | 7 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 14811 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 3 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 8 | 8 | 0 | 8 |
| database_search | 26 | 12 | 14 | 2 |
| reader | 37 | 32 | 5 | 0 |
| web_search | 2 | 2 | 0 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 37 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 37 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=27

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 97
Input tokens: 1028380
Cached input tokens: 141568
Output tokens: 26569
Reasoning tokens: 663
Total tokens: 1054949
Cost: RMB 2.94202740
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 97 | 1028380 | 141568 | 26569 | 1054949 | 2.94202740 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 2
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: True
Actual next stage: plan_supplement

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 1 | 1 | PASS |
| NP-2 | 0 | 1 | INSUFFICIENT |
| NP-3 | 1 | 1 | PASS |

### Round 2

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 2
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 1 | 1 | PASS |
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
| NP-1 | insufficient_evidence | - | 1 | True |
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
| NP-1 | insufficient_evidence | - | 1 | True |
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 1 | True |


## Errors

- run_research_task / tool_0010: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0013: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0014: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0019: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0018: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0020: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0021: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0024: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0027: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0030: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0036: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0044: ValidationError: 1 validation error for ConfiguredReaderCall8000_16000
  Value error, batch offsets and limits belong inside each reads item [type=value_error, input_value={'char_start': 14000, 'ma...00, 'max_chars': 8000}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0046: ValidationError: 1 validation error for ConfiguredReaderCall8000_16000
  Value error, batch offsets and limits belong inside each reads item [type=value_error, input_value={'char_start': 22000, 'ma...00, 'max_chars': 8000}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0048: ValidationError: 1 validation error for ConfiguredReaderCall8000_16000
  Value error, batch offsets and limits belong inside each reads item [type=value_error, input_value={'char_start': 30000, 'ma...00, 'max_chars': 8000}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0050: ValidationError: 1 validation error for ConfiguredReaderCall8000_16000
  Value error, batch offsets and limits belong inside each reads item [type=value_error, input_value={'char_start': 38000, 'ma...00, 'max_chars': 8000}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0052: ValidationError: 1 validation error for ConfiguredReaderCall8000_16000
  Value error, batch offsets and limits belong inside each reads item [type=value_error, input_value={'char_start': 38000, 'ma...00, 'max_chars': 2000}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0060: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0063: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0064: HarnessPolicyError: reader required after database_search returned artifact_ids

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
