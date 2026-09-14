# Runtime Summary

## Run

Paper ID: MG19333vrw
Run ID: reader-probe-2
Status: SUCCESS
Start: 2026-09-11T15:22:57.872633+00:00
End: 2026-09-11T15:24:11.212537+00:00
Duration: 73405 ms

## Environment

Git Branch: hyl
Git Commit: 80928594257cdbe1f350bc7de4a6041bbee76514
Model: None / None
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| run_research_task | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 3 | 3 | 0 | 1 |
| web_search | 4 | 0 | 4 | 0 |
| database_search | 2 | 2 | 0 | 0 |
| reader | 12 | 9 | 3 | 0 |

## LLM Token Usage and Cost

Calls: 22
Input tokens: 164408
Cached input tokens: 139520
Output tokens: 4872
Reasoning tokens: 0
Total tokens: 169280
Cost: RMB 0.16036800
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 22 | 164408 | 139520 | 4872 | 169280 | 0.16036800 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- - / tool_0004: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- - / tool_0009: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- - / tool_0011: BaiduSearchError: query exceeds Baidu's 72-unit limit (77)
- - / tool_0012: ValueError: artifact art_4634390df5d21784a59f3de0 sha256 mismatch
- - / tool_0014: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- - / tool_0015: ValueError: artifact art_6729fe01c8e0c19c99425d88 sha256 mismatch
- - / tool_0021: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- None

## Last Completed Stage

None
