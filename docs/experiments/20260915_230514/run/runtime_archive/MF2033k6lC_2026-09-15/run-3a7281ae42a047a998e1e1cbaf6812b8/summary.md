# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-3a7281ae42a047a998e1e1cbaf6812b8
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-15T15:07:42.235920+00:00
End: 2026-09-15T15:30:44.357894+00:00
Duration: 1394736 ms

## Environment

Git Branch: lya
Git Commit: 5e1aa3513922812d2155aa32e3159f5579a4e60a
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 179330 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 27852 ms |
| plan_research_task | SUCCESS | 50324 ms |
| plan_research_task | SUCCESS | 2084 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 156263 ms |
| run_research_task | SUCCESS | 59619 ms |
| run_research_task | SUCCESS | 30080 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 1 ms |
| validate_synthesis_input | SUCCESS | 2 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 155362 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 6985 ms |
| plan_research_task | SUCCESS | 41440 ms |
| plan_research_task | SUCCESS | 2611 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 222056 ms |
| run_research_task | SUCCESS | 99611 ms |
| run_research_task | SUCCESS | 329656 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 265415 ms |
| validate_synthesis_input | SUCCESS | 7 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 176351 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 3 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| database_search | 26 | 7 | 19 | 0 |
| reference_search | 17 | 17 | 0 | 17 |
| reader | 33 | 32 | 1 | 0 |
| web_search | 5 | 0 | 5 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 33 | 1 | OTHER | `diagnostics/reader.json` |
| reference_namespace | ERROR | 33 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: OTHER=1

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 106
Input tokens: 1079690
Cached input tokens: 25856
Output tokens: 40339
Reasoning tokens: 17109
Total tokens: 1120029
Cost: RMB 3.53230980
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 106 | 1079690 | 25856 | 40339 | 1120029 | 3.53230980 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 0
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: True
Actual next stage: plan_supplement

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 0 | 1 | INSUFFICIENT |
| NP-3 | 0 | 1 | INSUFFICIENT |

### Round 2

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 1
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
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
| NP-1 | insufficient_evidence | - | 0 | True |
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 0 | True |

### Stage stage_0025

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
| NP-3 | reviewed | partially_novel | 1 | True |


## Errors

- run_research_task / tool_0001: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0006: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0008: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0011: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0013: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0015: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0019: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0020: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0021: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0024: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0025: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0031: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0039: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0041: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0043: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0045: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0046: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0051: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0052: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0053: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0056: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0057: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0064: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0066: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0078: HarnessPolicyError: reader tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
