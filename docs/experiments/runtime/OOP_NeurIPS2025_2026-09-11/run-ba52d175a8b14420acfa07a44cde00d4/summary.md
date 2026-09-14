# Runtime Summary

## Run

Paper ID: OOP_NeurIPS2025
Run ID: run-ba52d175a8b14420acfa07a44cde00d4
Status: SUCCESS
Start: 2026-09-11T16:43:36.649570+00:00
End: 2026-09-11T16:52:43.602797+00:00
Duration: 547000 ms

## Environment

Git Branch: hyl
Git Commit: 3010a89be2e2965c82e982e1c3f0f85dcbaf6994
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 13296 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 3062 ms |
| plan_research_task | SUCCESS | 8750 ms |
| plan_research_task | SUCCESS | 7764 ms |
| plan_research_task | SUCCESS | 8937 ms |
| plan_research_task | SUCCESS | 3735 ms |
| plan_research_task | SUCCESS | 5030 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 117843 ms |
| run_research_task | SUCCESS | 345328 ms |
| run_research_task | SUCCESS | 347828 ms |
| run_research_task | SUCCESS | 345250 ms |
| run_research_task | SUCCESS | 337406 ms |
| run_research_task | SUCCESS | 142687 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 7703 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 16 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 17 | 15 | 2 | 3 |
| database_search | 16 | 12 | 4 | 4 |
| reader | 30 | 28 | 2 | 0 |
| browser | 2 | 0 | 2 | 0 |

## LLM Token Usage and Cost

Calls: 78
Input tokens: 1070528
Cached input tokens: 888064
Output tokens: 19671
Reasoning tokens: 408
Total tokens: 1090199
Cost: RMB 0.99085020
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 78 | 1070528 | 888064 | 19671 | 1090199 | 0.99085020 | 0 |

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

### Stage stage_0018

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


## Errors

- run_research_task / tool_0028: BrowserDependencyError: Chromium runtime libraries are unavailable in both the system loader and the current Python environment; install them with 'playwright install-deps chromium' during deployment
- run_research_task / tool_0031: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0037: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0039: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0044: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0045: ValueError: unknown source_record_id 'placeholder'
- run_research_task / tool_0047: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0060: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0063: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0065: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
