# Runtime Summary

## Run

Paper ID: MG19333vrw
Run ID: reader-probe
Status: SUCCESS
Start: 2026-09-11T15:15:32.123392+00:00
End: 2026-09-11T15:16:56.030804+00:00
Duration: 83969 ms

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
| reader | 4 | 1 | 3 | 0 |
| database_search | 2 | 2 | 0 | 0 |
| web_search | 2 | 0 | 2 | 0 |

## LLM Token Usage and Cost

Calls: 11
Input tokens: 95829
Cached input tokens: 81152
Output tokens: 1421
Reasoning tokens: 0
Total tokens: 97250
Cost: RMB 0.08116560
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 11 | 95829 | 81152 | 1421 | 97250 | 0.08116560 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- - / tool_0003: ValueError: unknown artifact_id 'art_bacdea65b0e66693407222b9' in the research manifest
- - / tool_0004: ValueError: unknown artifact_id 'art_bacdea65b0e66693407222b9' in the research manifest
- - / tool_0007: BaiduSearchError: BAIDU_QIANFAN_API_KEY is not configured
- - / tool_0010: HarnessPolicyError: reader required after database_search returned artifact_ids
- - / tool_0011: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- None

## Last Completed Stage

None
