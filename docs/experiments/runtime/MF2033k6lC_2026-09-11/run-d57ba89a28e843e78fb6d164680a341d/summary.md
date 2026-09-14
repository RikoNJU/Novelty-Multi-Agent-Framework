# Runtime Summary

## Run

Paper ID: MF2033k6lC
Run ID: run-d57ba89a28e843e78fb6d164680a341d
Status: SUCCESS
Start: 2026-09-11T17:51:59.488023+00:00
End: 2026-09-11T18:03:59.153103+00:00
Duration: 719656 ms

## Environment

Git Branch: hyl
Git Commit: 9050cfa6fd6212d2c89dbc59c06af4cb11035b3e
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 105296 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 5281 ms |
| plan_research_task | SUCCESS | 4796 ms |
| plan_research_task | SUCCESS | 5391 ms |
| plan_research_task | SUCCESS | 5046 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 575750 ms |
| run_research_task | SUCCESS | 579875 ms |
| run_research_task | SUCCESS | 586156 ms |
| run_research_task | SUCCESS | 565781 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 14 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 6891 ms |
| validate_report_integrity | SUCCESS | 14 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 31 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 23 | 19 | 4 | 5 |
| database_search | 18 | 14 | 4 | 4 |
| reader | 24 | 23 | 1 | 0 |
| browser | 2 | 0 | 2 | 0 |

## LLM Token Usage and Cost

Calls: 80
Input tokens: 1105965
Cached input tokens: 955904
Output tokens: 25745
Reasoning tokens: 10196
Total tokens: 1131710
Cost: RMB 0.61969740
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 80 | 1105965 | 955904 | 25745 | 1131710 | 0.61969740 | 0 |

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


## Reviewer Information Adjudication

### Stage stage_0014

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


## Errors

- run_research_task / tool_0011: ValueError: unknown source_record_id 'ref_c9b0a5329c1ebbb843e61096'
- run_research_task / tool_0023: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0025: BrowserDependencyError: Chromium runtime libraries are unavailable in both the system loader and the current Python environment; install them with 'playwright install-deps chromium' during deployment
- run_research_task / tool_0030: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0032: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0050: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0053: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0061: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0062: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0066: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0067: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
