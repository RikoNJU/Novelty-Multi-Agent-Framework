# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-bdb2796a9ad145e2b741706bd4dd4368
Entrypoint: paper_input
Input Identity: {"paper_json": "docs/experiments/20260917_v01_staging/input/sample_a.paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T16:42:36.392858+00:00
End: 2026-09-16T16:49:34.063796+00:00
Duration: 417712 ms

## Environment

Git Branch: lya
Git Commit: 00205761c864d1242a6a5685102d291648798a75
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 10642 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 8265 ms |
| plan_research_task | SUCCESS | 11187 ms |
| plan_research_task | SUCCESS | 3699 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 156186 ms |
| run_research_task | SUCCESS | 102699 ms |
| run_research_task | SUCCESS | 143602 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 21236 ms |
| validate_synthesis_input | SUCCESS | 5 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 13530 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 8909 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 89117 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 16140 ms |
| validate_synthesis_input | SUCCESS | 6 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 77942 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 3 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 15 | 15 | 0 | 15 |
| database_search | 30 | 11 | 19 | 0 |
| reader | 43 | 38 | 5 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 43 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 43 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=20

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 111
Input tokens: 1267245
Cached input tokens: 106496
Output tokens: 29817
Reasoning tokens: 1143
Total tokens: 1297062
Cost: RMB 3.78254880
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 111 | 1267245 | 106496 | 29817 | 1297062 | 3.78254880 | 0 |

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
| NP-2 | 1 | 1 | PASS |
| NP-3 | 0 | 1 | INSUFFICIENT |

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
| NP-2 | 1 | 1 | PASS |
| NP-3 | 0 | 1 | INSUFFICIENT |


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
| NP-2 | insufficient_evidence | - | 1 | True |
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
| NP-1 | insufficient_evidence | - | 1 | True |
| NP-2 | insufficient_evidence | - | 1 | True |
| NP-3 | insufficient_evidence | - | 0 | True |


## Errors

- run_research_task / tool_0011: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0013: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0016: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0019: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0021: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0022: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0024: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0025: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0028: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0031: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0050: ValidationError: 1 validation error for ConfiguredReaderCall8000_16000
  Value error, batch offsets and limits belong inside each reads item [type=value_error, input_value={'char_start': 42000, 'ma...00, 'max_chars': 8000}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0054: ValidationError: 1 validation error for ConfiguredReaderCall8000_16000
  Value error, batch offsets and limits belong inside each reads item [type=value_error, input_value={'char_start': 58000, 'ma...00, 'max_chars': 8000}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0056: ValidationError: 1 validation error for ConfiguredReaderCall8000_16000
  Value error, batch offsets and limits belong inside each reads item [type=value_error, input_value={'char_start': 58000, 'ma...00, 'max_chars': 8000}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0061: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0070: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0072: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0074: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0076: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0077: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0078: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0080: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0081: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0083: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0084: HarnessPolicyError: database_search tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
