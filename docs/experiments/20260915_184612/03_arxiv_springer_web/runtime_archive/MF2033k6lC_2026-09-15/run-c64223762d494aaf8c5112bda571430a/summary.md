# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-c64223762d494aaf8c5112bda571430a
Entrypoint: paper_input
Input Identity: {"paper_json": "docs/experiments/20260915_172846/input/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-15T10:36:30.280679+00:00
End: 2026-09-15T10:44:17.426116+00:00
Duration: 467691 ms

## Environment

Git Branch: experiment/arxiv-batch-01
Git Commit: 5e2a00532dceeb27ceebfe9aa5fe383bcc96eaf4
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 78327 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3476 ms |
| plan_research_task | SUCCESS | 4844 ms |
| plan_research_task | SUCCESS | 2644 ms |
| plan_research_task | SUCCESS | 5746 ms |
| plan_research_task | SUCCESS | 3532 ms |
| plan_research_task | SUCCESS | 2781 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 79125 ms |
| run_research_task | SUCCESS | 73834 ms |
| run_research_task | SUCCESS | 78393 ms |
| run_research_task | SUCCESS | 75915 ms |
| run_research_task | SUCCESS | 39782 ms |
| run_research_task | SUCCESS | 30893 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 5 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| plan_supplement | SUCCESS | 7343 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 7866 ms |
| plan_research_task | SUCCESS | 3411 ms |
| plan_research_task | SUCCESS | 4547 ms |
| plan_research_task | SUCCESS | 6032 ms |
| plan_research_task | SUCCESS | 7026 ms |
| plan_research_task | SUCCESS | 3217 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 25487 ms |
| run_research_task | SUCCESS | 57681 ms |
| run_research_task | SUCCESS | 90838 ms |
| run_research_task | SUCCESS | 79382 ms |
| run_research_task | SUCCESS | 38148 ms |
| run_research_task | SUCCESS | 40661 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 86703 ms |
| validate_synthesis_input | SUCCESS | 24 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 27559 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 1 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 27 | 26 | 1 | 5 |
| database_search | 32 | 2 | 30 | 0 |
| web_search | 55 | 39 | 16 | 0 |
| reader | 41 | 35 | 6 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 41 | 6 | WRONG_NAMESPACE | `diagnostics/reader.json` |
| reference_namespace | ERROR | 41 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: NEVER_PERSISTED=2, OTHER=2, WRONG_NAMESPACE=2

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 182
Input tokens: 2381681
Cached input tokens: 1947392
Output tokens: 50523
Reasoning tokens: 10603
Total tokens: 2432204
Cost: RMB 2.34179160
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 182 | 2381681 | 1947392 | 50523 | 2432204 | 2.34179160 | 0 |

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
Input final valid Cards: 2
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 1 | 1 | PASS |
| NP-3 | 1 | 1 | PASS |


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
| NP-2 | insufficient_evidence | - | 0 | True |
| NP-3 | insufficient_evidence | - | 0 | True |

### Stage stage_0037

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
| NP-2 | reviewed | partially_novel | 1 | True |
| NP-3 | reviewed | partially_novel | 1 | True |


## Errors

- run_research_task / tool_0004: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0013: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0015: ValueError: unknown artifact_id 'src_0d2f8b17cae0c6b6beed2550' in the research or subject reference manifest
- run_research_task / tool_0006: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0010: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0012: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0017: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0021: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0020: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0019: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0023: BaiduSearchError: query exceeds Baidu's 72-unit limit (81)
- run_research_task / tool_0028: BaiduSearchError: query exceeds Baidu's 72-unit limit (77)
- run_research_task / tool_0046: HarnessPolicyError: web_search tool-call budget exhausted
- run_research_task / tool_0051: HarnessPolicyError: web_search tool-call budget exhausted
- run_research_task / tool_0055: HarnessPolicyError: web_search tool-call budget exhausted
- run_research_task / tool_0056: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0059: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0061: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0063: BaiduSearchError: query exceeds Baidu's 72-unit limit (88)
- run_research_task / tool_0065: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0066: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0067: BaiduSearchError: query exceeds Baidu's 72-unit limit (78)
- run_research_task / tool_0071: BaiduSearchError: query exceeds Baidu's 72-unit limit (94)
- run_research_task / tool_0075: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0077: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0076: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0079: BaiduSearchError: query exceeds Baidu's 72-unit limit (75)
- run_research_task / tool_0080: HarnessPolicyError: web_search tool-call budget exhausted
- run_research_task / tool_0081: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0089: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0095: HarnessPolicyError: web_search tool-call budget exhausted
- run_research_task / tool_0087: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0088: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0091: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0100: BaiduSearchError: query exceeds Baidu's 72-unit limit (113)
- run_research_task / tool_0101: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0099: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0104: ValueError: unknown artifact_id 'src_1eee03f7afd673e24551ee6f' in the research or subject reference manifest
- run_research_task / tool_0108: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0110: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0111: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0113: BaiduSearchError: query exceeds Baidu's 72-unit limit (96)
- run_research_task / tool_0116: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0122: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0123: BaiduSearchError: query exceeds Baidu's 72-unit limit (85)
- run_research_task / tool_0126: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0129: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0130: HarnessPolicyError: web_search tool-call budget exhausted
- run_research_task / tool_0137: ToolExecutionError: all 1 search executions failed
- run_research_task / tool_0143: BaiduSearchError: query exceeds Baidu's 72-unit limit (76)
- run_research_task / tool_0151: HarnessPolicyError: total tool-call budget exhausted
- review_evidence / tool_0152: ValueError: unknown artifact_id 'art_d88778158223021b818fdd97' in the research manifest
- review_evidence / tool_0153: ValueError: unknown artifact_id 'art_d88778158223021b818fdd97' in the research manifest

## Integrity Gates

- validate_synthesis_input: PASS
- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
