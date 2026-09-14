# Runtime Summary

## Run

Paper ID: MG19333vrw-debug-full-20260907
Run ID: run-a9041be374d442b09cd92de7b5a4f980
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MG19333vrw-debug-full-20260907/paper-input/others/paper.json", "paper_sha256": "183b58191547b78b92ec264d24c1abc5429d1637fbd74bbf7af8f40678cc69f4", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: FAILED
Start: 2026-09-13T23:28:26.576385+00:00
End: 2026-09-13T23:28:26.671773+00:00
Duration: 146 ms

## Environment

Git Branch: lya
Git Commit: c9a5fab087f3f7f753491d18cfb2fcd36ce90d80
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | FAILED | 62 ms |
| plan | NOT_RUN | - ms |
| dispatch_planning_tasks | NOT_RUN | - ms |
| plan_research_task | NOT_RUN | - ms |
| dispatch_research_tasks | NOT_RUN | - ms |
| run_research_task | NOT_RUN | - ms |
| validate_evidence | NOT_RUN | - ms |
| review_evidence | NOT_RUN | - ms |
| validate_synthesis_input | NOT_RUN | - ms |
| check_final_evidence_sufficiency | NOT_RUN | - ms |
| plan_supplement | NOT_RUN | - ms |
| synthesize_report | NOT_RUN | - ms |
| validate_report_integrity | NOT_RUN | - ms |
| persist_report | NOT_RUN | - ms |
| render_report | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | INCOMPLETE | 0 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | OK | 0 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 1
Input tokens: 0
Cached input tokens: 0
Output tokens: 0
Reasoning tokens: 0
Total tokens: 0
Cost: RMB 0.00000000
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 1 | 0 | 0 | 0 | 0 | 0.00000000 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- extract_points / -: ModelClientError: 模型 HTTP 调用失败: 401 {"code":30014,"data":null,"message":"Token is invalid."}
- - / -: ModelClientError: 模型 HTTP 调用失败: 401 {"code":30014,"data":null,"message":"Token is invalid."}

## Integrity Gates

- None

## Last Completed Stage

None
