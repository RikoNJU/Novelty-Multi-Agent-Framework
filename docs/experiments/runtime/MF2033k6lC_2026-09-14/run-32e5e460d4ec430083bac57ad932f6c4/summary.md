# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-32e5e460d4ec430083bac57ad932f6c4
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "e99c240cf77c60638da6139ef8b5303e58fa464514872c59da2bd87b8910e5ab", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-14T13:40:24.742320+00:00
End: 2026-09-14T13:43:25.250245+00:00
Duration: 180953 ms

## Environment

Git Branch: 0914
Git Commit: 6313f7069511baa4a28866dd2b52be56c269ccf9
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 87969 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 5655 ms |
| plan_research_task | SUCCESS | 7155 ms |
| plan_research_task | SUCCESS | 9719 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 61375 ms |
| run_research_task | SUCCESS | 60092 ms |
| run_research_task | SUCCESS | 61015 ms |
| validate_evidence | SUCCESS | 15 ms |
| review_evidence | SUCCESS | 16 ms |
| validate_synthesis_input | SUCCESS | 15 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 6390 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 77 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 13 | 11 | 2 | 11 |
| database_search | 12 | 3 | 9 | 3 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | OK | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 34
Input tokens: 138076
Cached input tokens: 93184
Output tokens: 10835
Reasoning tokens: 4799
Total tokens: 148911
Cost: RMB 0.26014620
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 34 | 138076 | 93184 | 10835 | 148911 | 0.26014620 | 0 |

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
- run_research_task / tool_0008: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0009: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0011: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0015: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0016: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0017: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0023: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0024: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0025: HarnessPolicyError: reference_search tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
