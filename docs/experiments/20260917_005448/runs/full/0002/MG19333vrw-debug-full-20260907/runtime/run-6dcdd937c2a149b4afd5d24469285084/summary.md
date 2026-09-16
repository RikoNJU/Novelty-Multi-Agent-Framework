# Runtime Summary

## Run

Paper ID: MG19333vrw-debug-full-20260907
Run ID: run-6dcdd937c2a149b4afd5d24469285084
Entrypoint: paper_input
Input Identity: {"paper_json": "docs/experiments/20260917_v01_staging/input/sample_b.paper.json", "paper_sha256": "956e606ece4e8616375e21f7a6d5784fc789f32c142fe38850db2a6926424466", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T16:50:35.629908+00:00
End: 2026-09-16T16:54:48.077210+00:00
Duration: 252490 ms

## Environment

Git Branch: frontend
Git Commit: 00205761c864d1242a6a5685102d291648798a75
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 9591 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3369 ms |
| plan_research_task | SUCCESS | 3348 ms |
| plan_research_task | SUCCESS | 6859 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 84885 ms |
| run_research_task | SUCCESS | 104198 ms |
| run_research_task | SUCCESS | 172074 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 23012 ms |
| validate_synthesis_input | SUCCESS | 6 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 33783 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 4 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 8 | 8 | 0 | 8 |
| database_search | 12 | 5 | 7 | 0 |
| reader | 20 | 19 | 1 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 20 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 20 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=10

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 57
Input tokens: 455320
Cached input tokens: 81152
Output tokens: 21661
Reasoning tokens: 1482
Total tokens: 476981
Cost: RMB 1.34179860
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 57 | 455320 | 81152 | 21661 | 476981 | 1.34179860 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

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
| NP-1 | 1 | 1 | PASS |
| NP-2 | 1 | 1 | PASS |
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
| NP-1 | reviewed | not_novel | 1 | False |
| NP-2 | insufficient_evidence | - | 1 | True |
| NP-3 | insufficient_evidence | - | 2 | True |


## Errors

- run_research_task / tool_0011: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0012: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0014: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0017: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0021: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0022: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0026: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0033: ValidationError: 1 validation error for ConfiguredReaderCall8000_16000
  Value error, batch offsets and limits belong inside each reads item [type=value_error, input_value={'max_chars': 2000, 'read...a', 'max_chars': 2000}]}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
