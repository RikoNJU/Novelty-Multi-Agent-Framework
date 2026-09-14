# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-94376cef423340cfb6d68499433e887a
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "e99c240cf77c60638da6139ef8b5303e58fa464514872c59da2bd87b8910e5ab", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-14T13:03:55.558532+00:00
End: 2026-09-14T13:11:21.442923+00:00
Duration: 446265 ms

## Environment

Git Branch: 0914
Git Commit: 6313f7069511baa4a28866dd2b52be56c269ccf9
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 345671 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 8828 ms |
| plan_research_task | SUCCESS | 11734 ms |
| plan_research_task | SUCCESS | 2515 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 64000 ms |
| run_research_task | SUCCESS | 65110 ms |
| run_research_task | SUCCESS | 68780 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 16 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 6219 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 63 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 12 | 11 | 1 | 11 |
| database_search | 13 | 3 | 10 | 3 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | OK | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 36
Input tokens: 142532
Cached input tokens: 60160
Output tokens: 13427
Reasoning tokens: 7718
Total tokens: 155959
Cost: RMB 0.38600700
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 36 | 142532 | 60160 | 13427 | 155959 | 0.38600700 | 0 |

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

- run_research_task / tool_0007: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0011: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0012: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0013: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0014: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0016: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0019: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0020: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0022: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0024: HarnessPolicyError: reference_search tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
