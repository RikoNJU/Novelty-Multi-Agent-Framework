# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-9435c25972914f8087d99944b1446cbd
Entrypoint: paper_input
Input Identity: {"paper_json": "docs/experiments/.full_run_after_fixes/input/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: FAILED
Start: 2026-09-15T14:12:36.986865+00:00
End: 2026-09-15T14:18:07.299720+00:00
Duration: 330762 ms

## Environment

Git Branch: lya
Git Commit: f0b0238599841d767177a7b377a7cf0797af15d8
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 242960 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 60029 ms |
| plan_research_task | SUCCESS | 6136 ms |
| plan_research_task | SUCCESS | 5169 ms |
| plan_research_task | SUCCESS | 5346 ms |
| plan_research_task | SUCCESS | 4429 ms |
| plan_research_task | SUCCESS | 6538 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
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
| reviewer | ERROR | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 14
Input tokens: 22955
Cached input tokens: 256
Output tokens: 19134
Reasoning tokens: 13880
Total tokens: 42089
Cost: RMB 0.24037980
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 14 | 22955 | 256 | 19134 | 42089 | 0.24037980 | 0 |

## Final Evidence Sufficiency Checks

- None

## Reviewer Information Adjudication

- None

## Errors

- - / -: WorkflowExecutionError: SearchPlan completeness check failed: {"duplicate_plan_count": 0, "expected_task_count": 6, "missing_task_keys": [["NP-1", "T-1"]], "search_plan_count": 5, "unexpected_plan_keys": []}

## Integrity Gates

- None

## Last Completed Stage

dispatch_research_tasks
