# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-fe88eb06a08841e9bac5b6687c9ed3df
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "e99c240cf77c60638da6139ef8b5303e58fa464514872c59da2bd87b8910e5ab", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-14T14:17:02.427565+00:00
End: 2026-09-14T14:36:57.143154+00:00
Duration: 1195155 ms

## Environment

Git Branch: 0914
Git Commit: 6313f7069511baa4a28866dd2b52be56c269ccf9
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 498984 ms |
| resolve_subject_references | SUCCESS | 331297 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 7452 ms |
| plan_research_task | SUCCESS | 30859 ms |
| plan_research_task | SUCCESS | 4125 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 289311 ms |
| run_research_task | SUCCESS | 284078 ms |
| run_research_task | SUCCESS | 293280 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 16 ms |
| validate_synthesis_input | SUCCESS | 15 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 25796 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 46 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 12 | 11 | 1 | 11 |
| database_search | 14 | 3 | 11 | 3 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | OK | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 35
Input tokens: 141960
Cached input tokens: 96512
Output tokens: 12060
Reasoning tokens: 7197
Total tokens: 154020
Cost: RMB 0.27383760
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 35 | 141960 | 96512 | 12060 | 154020 | 0.27383760 | 0 |

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

### Stage stage_0013

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

### Stage stage_0013

Stage status: SUCCESS
Actual next stage: validate_synthesis_input

| Novelty Point | Coverage | Required Sources | Failed | Not Attempted | Zero Hit |
|---|---|---|---|---|---|
| NP-1 | failed | arxiv | arxiv | - | - |
| NP-2 | failed | arxiv | arxiv | - | - |
| NP-3 | failed | arxiv | arxiv | - | - |


## Errors

- run_research_task / tool_0004: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0006: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0009: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0011: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0012: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0014: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0017: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0018: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0019: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0024: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0026: HarnessPolicyError: reference_search tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
