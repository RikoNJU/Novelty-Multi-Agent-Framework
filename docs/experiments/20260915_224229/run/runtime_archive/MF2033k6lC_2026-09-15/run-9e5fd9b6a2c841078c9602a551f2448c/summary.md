# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-9e5fd9b6a2c841078c9602a551f2448c
Entrypoint: paper_input
Input Identity: {"paper_json": "docs/experiments/.full_run_after_fixes/input/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-15T14:18:51.896955+00:00
End: 2026-09-15T14:42:29.106821+00:00
Duration: 1421212 ms

## Environment

Git Branch: lya
Git Commit: f0b0238599841d767177a7b377a7cf0797af15d8
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 85233 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3219 ms |
| plan_research_task | SUCCESS | 3857 ms |
| plan_research_task | SUCCESS | 5706 ms |
| plan_research_task | SUCCESS | 6764 ms |
| plan_research_task | SUCCESS | 4590 ms |
| plan_research_task | SUCCESS | 3724 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 94782 ms |
| run_research_task | SUCCESS | 95589 ms |
| run_research_task | SUCCESS | 109200 ms |
| run_research_task | SUCCESS | 240725 ms |
| run_research_task | SUCCESS | 34020 ms |
| run_research_task | SUCCESS | 42229 ms |
| validate_evidence | SUCCESS | 2 ms |
| review_evidence | SUCCESS | 167714 ms |
| validate_synthesis_input | SUCCESS | 6 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 6590 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 9724 ms |
| plan_research_task | SUCCESS | 3546 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 140324 ms |
| run_research_task | SUCCESS | 93190 ms |
| validate_evidence | SUCCESS | 3 ms |
| review_evidence | SUCCESS | 715216 ms |
| validate_synthesis_input | SUCCESS | 14 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 23468 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 5 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 26 | 23 | 3 | 4 |
| database_search | 26 | 2 | 24 | 0 |
| reader | 58 | 53 | 5 | 0 |
| web_search | 10 | 0 | 10 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 58 | 5 | OTHER | `diagnostics/reader.json` |
| reference_namespace | ERROR | 58 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: OTHER=5

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 149
Input tokens: 1402251
Cached input tokens: 178432
Output tokens: 58132
Reasoning tokens: 17459
Total tokens: 1460383
Cost: RMB 4.24817460
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 149 | 1402251 | 178432 | 58132 | 1460383 | 4.24817460 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 5
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: True
Actual next stage: plan_supplement

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 2 | 1 | PASS |
| NP-3 | 3 | 1 | PASS |

### Round 2

Configured cut: 1
Stage status: SUCCESS
Check status: PASS
Input final valid Cards: 8
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 3 | 1 | PASS |
| NP-2 | 2 | 1 | PASS |
| NP-3 | 3 | 1 | PASS |


## Reviewer Information Adjudication

### Stage stage_0018

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
| NP-2 | reviewed | novel | 2 | True |
| NP-3 | reviewed | partially_novel | 1 | False |

### Stage stage_0029

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
| NP-2 | reviewed | novel | 2 | False |
| NP-3 | reviewed | partially_novel | 1 | True |


## Errors

- run_research_task / tool_0006: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0007: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0008: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0009: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0015: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0017: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0018: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0016: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0020: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0019: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0024: ToolExecutionError: query exceeds Baidu's 72-unit limit (74)
- run_research_task / tool_0025: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0028: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0032: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0033: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0034: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0036: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0037: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0040: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0041: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0042: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0044: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0045: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0046: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0047: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0048: BaiduSearchError: Baidu Web Search HTTP 429
- run_research_task / tool_0051: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0055: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0056: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0070: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0086: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0087: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0088: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0091: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0093: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0098: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0107: HarnessPolicyError: reader tool-call budget exhausted
- review_evidence / tool_0113: PermissionError: artifact 'placeholder' is outside reviewer scope
- review_evidence / tool_0114: HarnessPolicyError: total tool-call budget exhausted
- review_evidence / tool_0117: PermissionError: artifact 'none' is outside reviewer scope
- review_evidence / tool_0118: PermissionError: artifact 'none' is outside reviewer scope

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
