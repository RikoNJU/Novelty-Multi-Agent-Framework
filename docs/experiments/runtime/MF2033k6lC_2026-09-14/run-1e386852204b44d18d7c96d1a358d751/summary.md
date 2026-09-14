# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-1e386852204b44d18d7c96d1a358d751
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "e99c240cf77c60638da6139ef8b5303e58fa464514872c59da2bd87b8910e5ab", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-14T13:33:02.475888+00:00
End: 2026-09-14T13:36:39.702659+00:00
Duration: 217657 ms

## Environment

Git Branch: 0914
Git Commit: 6313f7069511baa4a28866dd2b52be56c269ccf9
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 124796 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 12296 ms |
| plan_research_task | SUCCESS | 6360 ms |
| plan_research_task | SUCCESS | 6780 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 49936 ms |
| run_research_task | SUCCESS | 52563 ms |
| run_research_task | SUCCESS | 54188 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 15 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 9984 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 78 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 13 | 12 | 1 | 12 |
| database_search | 13 | 5 | 8 | 5 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | OK | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 37
Input tokens: 148476
Cached input tokens: 98816
Output tokens: 15040
Reasoning tokens: 8827
Total tokens: 163516
Cost: RMB 0.31398480
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 37 | 148476 | 98816 | 15040 | 163516 | 0.31398480 | 0 |

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
| NP-1 | insufficient_evidence | - | 0 | True |
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 0 | True |


## Retrieval Coverage

### Stage stage_0012

Stage status: SUCCESS
Actual next stage: validate_synthesis_input

| Novelty Point | Coverage | Required Sources | Failed | Not Attempted | Zero Hit |
|---|---|---|---|---|---|
| NP-1 | failed | arxiv | arxiv | - | - |
| NP-2 | failed | arxiv | arxiv | - | - |
| NP-3 | failed | arxiv | arxiv | - | - |


## Errors

- run_research_task / tool_0004: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0007: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0009: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0011: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0013: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0015: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0019: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0023: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0026: HarnessPolicyError: database_search tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
