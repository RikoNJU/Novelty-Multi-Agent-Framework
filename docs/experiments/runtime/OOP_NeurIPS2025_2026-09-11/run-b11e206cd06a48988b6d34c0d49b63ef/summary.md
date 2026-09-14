# Runtime Summary

## Run

Paper ID: OOP_NeurIPS2025
Run ID: run-b11e206cd06a48988b6d34c0d49b63ef
Status: SUCCESS
Start: 2026-09-11T15:52:15.201996+00:00
End: 2026-09-11T15:56:52.897766+00:00
Duration: 277765 ms

## Environment

Git Branch: hyl
Git Commit: d21d39995978c76583f1e107aa1767f67b77aac4
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 27093 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 5905 ms |
| plan_research_task | SUCCESS | 7406 ms |
| plan_research_task | SUCCESS | 8500 ms |
| plan_research_task | SUCCESS | 8672 ms |
| plan_research_task | SUCCESS | 7842 ms |
| plan_research_task | SUCCESS | 10891 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 152250 ms |
| run_research_task | SUCCESS | 134375 ms |
| run_research_task | SUCCESS | 130359 ms |
| run_research_task | SUCCESS | 152203 ms |
| run_research_task | SUCCESS | 56687 ms |
| run_research_task | SUCCESS | 59500 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 7125 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 30 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 24 | 23 | 1 | 4 |
| database_search | 14 | 12 | 2 | 12 |
| web_search | 22 | 0 | 22 | 0 |
| reader | 6 | 5 | 1 | 0 |

## LLM Token Usage and Cost

Calls: 83
Input tokens: 954338
Cached input tokens: 726528
Output tokens: 16046
Reasoning tokens: 1168
Total tokens: 970384
Cost: RMB 1.04580240
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 83 | 954338 | 726528 | 16046 | 970384 | 1.04580240 | 0 |

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


## Errors

- run_research_task / tool_0008: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0009: BaiduSearchError: query exceeds Baidu's 72-unit limit (89)
- run_research_task / tool_0010: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0012: BaiduSearchError: query exceeds Baidu's 72-unit limit (91)
- run_research_task / tool_0013: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0014: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0016: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0019: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0022: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0028: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0036: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0037: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0040: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0041: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0043: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0044: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0047: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0048: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0049: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0051: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0054: BaiduSearchError: query exceeds Baidu's 72-unit limit (84)
- run_research_task / tool_0055: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0058: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0062: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0064: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- run_research_task / tool_0066: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
