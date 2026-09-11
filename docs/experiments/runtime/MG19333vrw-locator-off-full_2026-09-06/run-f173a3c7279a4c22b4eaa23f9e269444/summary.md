# Runtime Summary

## Run

Paper ID: MG19333vrw-locator-off-full
Run ID: run-f173a3c7279a4c22b4eaa23f9e269444
Status: SUCCESS
Start: 2026-09-06T10:32:45.693416+00:00
End: 2026-09-06T10:37:49.474904+00:00
Duration: 303789 ms

## Environment

Git Branch: lya
Git Commit: eab288105bc7b0c7baeecb222c005d528fbe6b68
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 4 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 7276 ms |
| plan_research_task | SUCCESS | 4375 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 288183 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| assess_coverage | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 3750 ms |
| render_report | SUCCESS | 2 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 1 | 1 | 0 | 1 |
| database_search | 1 | 1 | 0 | 0 |
| reader | 2 | 2 | 0 | 0 |
| web_search | 6 | 3 | 3 | 0 |
| browser | 1 | 1 | 0 | 0 |

## Errors

- run_research_task / tool_0004: BaiduSearchError: query exceeds Baidu's 72-unit limit (100)
- run_research_task / tool_0009: BaiduSearchError: query exceeds Baidu's 72-unit limit (76)
- run_research_task / tool_0011: HarnessPolicyError: total tool-call budget exhausted

## Last Completed Stage

render_report
