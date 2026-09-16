# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-20260916T040710883332Z-22d23d373b
Entrypoint: single
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T04:07:10.883386+00:00
End: 2026-09-16T04:10:43.354759+00:00
Duration: 213829 ms

## Environment

Git Branch: fix/arxiv-rate-limit-final
Git Commit: 674c7ff7657a3dda7a4dddd9d39d5b88344a2f05
Model: None / None
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| run_research_task | SUCCESS | 213778 ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 7 | 4 | 3 | 0 |
| database_search | 2 | 2 | 0 | 0 |
| reader | 12 | 12 | 0 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 12 | 0 | INCOMPLETE_RECORD | `diagnostics/reader.json` |
| reference_namespace | ERROR | 12 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | INCOMPLETE | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: INCOMPLETE_RECORD=12

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 22
Input tokens: 398507
Cached input tokens: 3840
Output tokens: 5353
Reasoning tokens: 0
Total tokens: 403860
Cost: RMB 1.23333000
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 22 | 398507 | 3840 | 5353 | 403860 | 1.23333000 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- run_research_task / tool_0003: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0009: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0010: HarnessPolicyError: reader required after database_search returned artifact_ids

## Integrity Gates

- None

## Last Completed Stage

run_research_task
