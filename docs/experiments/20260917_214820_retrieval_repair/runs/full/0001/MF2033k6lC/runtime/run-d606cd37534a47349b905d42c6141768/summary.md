# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-d606cd37534a47349b905d42c6141768
Entrypoint: paper_input
Input Identity: {"paper_json": "docs/experiments/20260916_233840/input/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-17T14:31:28.070180+00:00
End: 2026-09-17T14:41:39.060943+00:00
Duration: 611067 ms

## Environment

Git Branch: lya
Git Commit: 00256091346b641834003957721035f5dfa834e5
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.12.3

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 58365 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 15796 ms |
| plan_research_task | SUCCESS | 5474 ms |
| plan_research_task | SUCCESS | 3929 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 82328 ms |
| run_research_task | SUCCESS | 130706 ms |
| run_research_task | SUCCESS | 116948 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 93158 ms |
| validate_synthesis_input | SUCCESS | 6 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 103736 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 4 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 10 | 10 | 0 | 10 |
| database_search | 19 | 8 | 11 | 0 |
| reader | 27 | 26 | 1 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 27 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 27 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=15

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 75
Input tokens: 641281
Cached input tokens: 28928
Output tokens: 25745
Reasoning tokens: 720
Total tokens: 667026
Cost: RMB 2.07744240
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 75 | 641281 | 28928 | 25745 | 667026 | 2.07744240 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: PASS
Input final valid Cards: 5
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 1 | 1 | PASS |
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
| NP-1 | insufficient_evidence | - | 1 | True |
| NP-2 | insufficient_evidence | - | 2 | True |
| NP-3 | insufficient_evidence | - | 2 | True |


## Errors

- run_research_task / tool_0004: ValidationError: 1 validation error for ConfiguredReaderCall8000_16000
  Value error, batch offsets and limits belong inside each reads item [type=value_error, input_value={'max_chars': 8000, 'read...a', 'max_chars': 8000}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0007: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0009: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0014: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0020: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0023: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0024: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0025: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0039: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0040: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0042: ToolExecutionError: all 1 search executions failed

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
