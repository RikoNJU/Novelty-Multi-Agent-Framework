# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-d54cbc1b41b346ff945eb960456ab647
Entrypoint: paper_input
Input Identity: {"paper_json": "outputs/MF2033k6lC/paper-input/others/paper.json", "paper_sha256": "430dc1a41d55724e42a21b10e28d25146e931ed1c06e68a712de60006f4f3768", "novelty_point_id": null, "task_id": null, "search_plan_id": null}
Status: SUCCESS
Start: 2026-09-16T00:19:15.248843+00:00
End: 2026-09-16T00:33:31.225993+00:00
Duration: 856406 ms

## Environment

Git Branch: hyl
Git Commit: 44d7a1b045333d448bea63b77876fd11ae91ead2
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 202592 ms |
| resolve_subject_references | SUCCESS | 210047 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 18733 ms |
| plan_research_task | SUCCESS | 4875 ms |
| plan_research_task | SUCCESS | 18938 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 126016 ms |
| run_research_task | SUCCESS | 103969 ms |
| run_research_task | SUCCESS | 62639 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 248358 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 25922 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 32 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 7 | 4 | 3 | 0 |
| database_search | 6 | 5 | 1 | 0 |
| reader | 12 | 6 | 6 | 0 |

## Runtime Diagnostics

| Diagnostic | Status | Calls | Failed | Primary finding | Detail |
|---|---|---:|---:|---|---|
| reader | WARNING | 12 | 6 | WRONG_NAMESPACE | `diagnostics/reader.json` |
| reference_namespace | ERROR | 12 | 0 | - | `diagnostics/reference_namespace.json` |
| reviewer | WARNING | 0 | 0 | - | `diagnostics/reviewer.json` |

reader classifications: OTHER=4, WRONG_NAMESPACE=2

## Run Outcome

- None

## LLM Token Usage and Cost

Calls: 38
Input tokens: 338169
Cached input tokens: 255488
Output tokens: 18820
Reasoning tokens: 7198
Total tokens: 356989
Cost: RMB 0.49406940
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 38 | 338169 | 255488 | 18820 | 356989 | 0.49406940 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 2
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 2 | 1 | PASS |
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
| NP-2 | reviewed | novel | 2 | True |
| NP-3 | insufficient_evidence | - | 0 | True |


## Retrieval Coverage

### Stage stage_0013

Stage status: SUCCESS
Actual next stage: validate_synthesis_input

| Novelty Point | Coverage | Required Sources | Failed | Not Attempted | Zero Hit |
|---|---|---|---|---|---|
| NP-1 | partial | arxiv, springer | - | - | arxiv |
| NP-2 | complete | arxiv, springer | - | - | arxiv, springer |
| NP-3 | partial | arxiv, springer | - | springer | arxiv |


## Errors

- run_research_task / tool_0007: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0008: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0009: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0012: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0020: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0021: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0022: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0023: HarnessPolicyError: reader required after database_search returned artifact_ids
- review_evidence / tool_0024: ValueError: unknown artifact_id 'art_d66e0ee9dd302e32ea2daf52' in the research manifest
- review_evidence / tool_0025: ValueError: unknown artifact_id 'art_f3ade99e35dbf7c9385b5639' in the research manifest

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
