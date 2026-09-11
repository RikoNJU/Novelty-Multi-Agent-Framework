# Runtime Summary

## Run

Paper ID: MG19333vrw-locator-off-full
Run ID: run-f5622ac5d0c64b1d863b8e66e6684396
Status: SUCCESS
Start: 2026-09-06T10:43:32.836521+00:00
End: 2026-09-06T10:49:20.728996+00:00
Duration: 347899 ms

## Environment

Git Branch: lya
Git Commit: eab288105bc7b0c7baeecb222c005d528fbe6b68
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 3 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 4220 ms |
| plan_research_task | SUCCESS | 5118 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 334870 ms |
| run_research_task | SUCCESS | 335248 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| assess_coverage | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 3069 ms |
| render_report | SUCCESS | 2 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 2 | 2 | 0 | 2 |
| database_search | 3 | 3 | 0 | 0 |
| web_search | 9 | 4 | 5 | 0 |
| reader | 6 | 4 | 2 | 0 |
| browser | 2 | 1 | 1 | 0 |

## Errors

- run_research_task / tool_0004: BaiduSearchError: Baidu Web Search request timed out
- run_research_task / tool_0006: ValidationError: 1 validation error for ReferenceReadResult
  Value error, read range must match text length [type=value_error, input_value={'read_id': 'read_238279c...8de5d4ef24bbe109e22448'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0008: BaiduSearchError: query exceeds Baidu's 72-unit limit (103)
- run_research_task / tool_0010: BaiduSearchError: query exceeds Baidu's 72-unit limit (76)
- run_research_task / tool_0015: BaiduSearchError: query exceeds Baidu's 72-unit limit (73)
- run_research_task / tool_0017: ValueError: unknown source_record_id 'src_838e2e18186eed7fde84f0f8'
- run_research_task / tool_0021: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0022: HarnessPolicyError: total tool-call budget exhausted

## Last Completed Stage

render_report
