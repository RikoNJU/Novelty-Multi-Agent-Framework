# Runtime Summary

## Run

Paper ID: MG19333vrw-debug-full-20260907
Run ID: run-5f78c1dade354974856fb7270ec04c89
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MG19333vrw-debug-full-20260907/paper-input/others/paper.json", "paper_sha256": "183b58191547b78b92ec264d24c1abc5429d1637fbd74bbf7af8f40678cc69f4", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-14T04:23:09.443677+00:00
End: 2026-09-14T04:26:09.768435+00:00
Duration: 183183 ms

## Environment

Git Branch: lya
Git Commit: 0f239b91484cc8d11a61b2e263714b087675d6b1
Model: openai_compatible / deepseek-v4-flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 11004 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 15385 ms |
| plan_research_task | SUCCESS | 11615 ms |
| plan_research_task | SUCCESS | 26112 ms |
| plan_research_task | SUCCESS | 11736 ms |
| plan_research_task | SUCCESS | 27750 ms |
| plan_research_task | SUCCESS | 28622 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 1479 ms |
| run_research_task | SUCCESS | 44880 ms |
| run_research_task | SUCCESS | 44453 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 2 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 5762 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 1 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 5 | 5 | 0 | 5 |
| database_search | 5 | 2 | 3 | 2 |
| reader | 1 | 0 | 1 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 1 | 1 | NEVER_PERSISTED | `diagnostics/reader.json` |
| reference_namespace | OK | 1 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: NEVER_PERSISTED=1

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 32
Input tokens: 111139
Cached input tokens: 89728
Output tokens: 32447
Reasoning tokens: 28278
Total tokens: 143586
Cost: RMB 0.00000000
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-v4-flash | 32 | 111139 | 89728 | 32447 | 143586 | 0.00000000 | 31 |

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

### Stage stage_0015

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


## Errors

- run_research_task / tool_0005: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0004: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0008: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0011: ValueError: unknown artifact_id 'none' in the research or subject reference manifest

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
