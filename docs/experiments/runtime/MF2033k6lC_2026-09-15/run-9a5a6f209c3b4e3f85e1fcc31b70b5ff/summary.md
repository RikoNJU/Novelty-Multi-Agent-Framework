# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-9a5a6f209c3b4e3f85e1fcc31b70b5ff
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "430dc1a41d55724e42a21b10e28d25146e931ed1c06e68a712de60006f4f3768", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: FAILED
Start: 2026-09-15T18:05:06.666763+00:00
End: 2026-09-15T22:27:32.335780+00:00
Duration: 15746297 ms

## Environment

Git Branch: hyl
Git Commit: 44d7a1b045333d448bea63b77876fd11ae91ead2
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 196296 ms |
| resolve_subject_references | SUCCESS | 48750 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 2125 ms |
| plan_research_task | SUCCESS | 13468 ms |
| plan_research_task | SUCCESS | 6233 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 87062 ms |
| run_research_task | SUCCESS | 84421 ms |
| run_research_task | SUCCESS | 154094 ms |
| validate_evidence | SUCCESS | 14 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | FAILED | 15324281 ms |
| plan_supplement | NOT_RUN | - ms |
| validate_report_integrity | NOT_RUN | - ms |
| persist_report | NOT_RUN | - ms |
| render_report | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 7 | 6 | 1 | 0 |
| reader | 29 | 25 | 4 | 0 |
| database_search | 9 | 6 | 3 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 29 | 4 | OTHER | `diagnostics/reader.json` |
| reference_namespace | ERROR | 29 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: OTHER=4

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 55
Input tokens: 572310
Cached input tokens: 474880
Output tokens: 14883
Reasoning tokens: 4461
Total tokens: 587193
Cost: RMB 0.28435050
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 55 | 572310 | 474880 | 14883 | 587193 | 0.28435050 | 0 |

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

### Stage stage_0013

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


## Retrieval Coverage

### Stage stage_0013

Stage status: SUCCESS
Actual next stage: validate_synthesis_input

| Novelty Point | Coverage | Required Sources | Failed | Not Attempted | Zero Hit |
|---|---|---|---|---|---|
| NP-1 | partial | arxiv, springer | - | springer | - |
| NP-2 | complete | arxiv, springer | - | - | arxiv, springer |
| NP-3 | partial | arxiv, springer | - | springer | - |


## Errors

- run_research_task / tool_0015: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0016: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0020: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0021: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0035: HarnessPolicyError: reference_search tool-call budget exhausted
- run_research_task / tool_0036: HarnessPolicyError: reader tool-call budget exhausted
- run_research_task / tool_0037: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0045: HarnessPolicyError: reader tool-call budget exhausted
- synthesize_report / -: ModelClientError: 模型网络调用失败: Remote end closed connection without response
- - / -: ModelClientError: 模型网络调用失败: Remote end closed connection without response

## Integrity Gates

- validate_synthesis_input: PASS

## Last Completed Stage

check_final_evidence_sufficiency
