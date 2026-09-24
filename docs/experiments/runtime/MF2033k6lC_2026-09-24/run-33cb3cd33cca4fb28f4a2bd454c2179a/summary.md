# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-33cb3cd33cca4fb28f4a2bd454c2179a
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "89fcc578efcc840daa9c4e0698943314f794e096e176c067dbbd6e603d42ea66", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: FAILED
Start: 2026-09-24T20:50:56.276474+00:00
End: 2026-09-24T20:53:25.133593+00:00
Duration: 148875 ms

## Environment

Git Branch: experiment/local-llm-baseline
Git Commit: 7e03fcca3eee05c9ce7b06ee9e74b5818b833726
Model: openai_compatible / qwen2.5-7b-instruct
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 37202 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 5945 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 49841 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 55483 ms |
| validate_synthesis_input | SUCCESS | 2 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | FAILED | 193 ms |
| plan_supplement | NOT_RUN | - ms |
| validate_report_integrity | NOT_RUN | - ms |
| persist_report | NOT_RUN | - ms |
| render_report | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| database_search | 2 | 1 | 1 | 0 |
| reader | 6 | 6 | 0 | 3 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | OK | 6 | 0 | - | `diagnostics/reader.json` |
| reference_namespace | ERROR | 6 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | OK | 0 | 0 | - | `diagnostics/reviewer.json` |

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 18
Input tokens: 94048
Cached input tokens: 0
Output tokens: 5934
Reasoning tokens: 0
Total tokens: 99982
Cost: RMB 0.00000000
Cost completeness: PARTIAL

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen2.5-7b-instruct | 18 | 94048 | 0 | 5934 | 99982 | 0.00000000 | 17 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: PASS
Input final valid Cards: 2
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 2 | 1 | PASS |


## Reviewer Information Adjudication

### Stage stage_0008

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
| NP-1 | reviewed | not_novel | 1 | False |


## Errors

- run_research_task / tool_0001: ToolExecutionError: all 1 search executions failed
- synthesize_report / -: ModelClientError: 模型 HTTP 调用失败: 400 {"object":"error","message":"This model's maximum context length is 32768 tokens. However, you requested 61456 tokens (57360 in the messages, 4096 in the completion). Please reduce the length of the messages or completion.","type":"BadRequestError","param":null,"code":400}
- - / -: ModelClientError: 模型 HTTP 调用失败: 400 {"object":"error","message":"This model's maximum context length is 32768 tokens. However, you requested 61456 tokens (57360 in the messages, 4096 in the completion). Please reduce the length of the messages or completion.","type":"BadRequestError","param":null,"code":400}

## Integrity Gates

- validate_synthesis_input: PASS

## Last Completed Stage

check_final_evidence_sufficiency
