# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-a36b256d94614b42b0962bea7e024727
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-27T20:02:18.609281+00:00
End: 2026-09-27T20:03:41.444198+00:00
Duration: 82843 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: 145723771fb615916f1fdd8199b21c603d31b59c
Model: openai_compatible / qwen2.5-7b-instruct
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 40258 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 7005 ms |
| plan_research_task | SUCCESS | 6498 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 11705 ms |
| run_research_task | SUCCESS | 4857 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 2 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 2 ms |
| synthesize_report | SUCCESS | 12258 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 2 ms |
| render_report | SUCCESS | 1 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| database_search | 4 | 0 | 4 | 0 |
| web_search | 1 | 0 | 1 | 0 |
| reference_search | 1 | 1 | 0 | 1 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | OK | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 15
Input tokens: 60182
Cached input tokens: 0
Output tokens: 2882
Reasoning tokens: 0
Total tokens: 63064
Estimated API cost (RMB): Unknown (priced subtotal 0.00000000)
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 15 | 60182 | 0 | 2882 | 63064 | Unknown (priced subtotal 0.00000000) | 15 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 0
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 0 | 1 | INSUFFICIENT |


## Reviewer Information Adjudication

### Stage stage_0010

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


## Errors

- run_research_task / tool_0001: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0002: ValidationError: 2 validation errors for DatabaseSearchArguments
full_text_source_record_ids.0
  String should have at least 1 character [type=string_too_short, input_value='', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/string_too_short
toolbench_rapidapi_key
  Extra inputs are not permitted [type=extra_forbidden, input_value='', input_type=str]
    For further information visit https://errors.pydantic.dev/2.13/v/extra_forbidden
- run_research_task / tool_0003: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0004: ValueError: unregistered researcher tool 'web_search'
- run_research_task / tool_0005: ToolExecutionError: all 1 search executions failed

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
