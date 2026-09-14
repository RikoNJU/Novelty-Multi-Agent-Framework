# Runtime Summary

## Run

Paper ID: OOP_NeurIPS2025
Run ID: run-9bf2685d763f4c4c96fa093792cba8ae
Status: SUCCESS
Start: 2026-09-11T16:09:31.155873+00:00
End: 2026-09-11T16:24:52.934437+00:00
Duration: 921827 ms

## Environment

Git Branch: hyl
Git Commit: 8c69cf4fa6c04d6bd69fcd1f2d5b667220782625
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.16

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 23014 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 2500 ms |
| plan_research_task | SUCCESS | 5421 ms |
| plan_research_task | SUCCESS | 7109 ms |
| plan_research_task | SUCCESS | 2984 ms |
| plan_research_task | SUCCESS | 6703 ms |
| plan_research_task | SUCCESS | 6280 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 839250 ms |
| run_research_task | SUCCESS | 458735 ms |
| run_research_task | SUCCESS | 430358 ms |
| run_research_task | SUCCESS | 430359 ms |
| run_research_task | SUCCESS | 430172 ms |
| run_research_task | SUCCESS | 423344 ms |
| validate_evidence | SUCCESS | 0 ms |
| review_evidence | SUCCESS | 0 ms |
| validate_synthesis_input | SUCCESS | 0 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 6516 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 15 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 16 | 14 | 2 | 2 |
| database_search | 13 | 12 | 1 | 5 |
| reader | 35 | 25 | 10 | 0 |
| browser | 1 | 0 | 1 | 0 |

## LLM Token Usage and Cost

Calls: 80
Input tokens: 1023286
Cached input tokens: 837120
Output tokens: 19505
Reasoning tokens: 699
Total tokens: 1042791
Cost: RMB 0.98517900
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 80 | 1023286 | 837120 | 19505 | 1042791 | 0.98517900 | 0 |

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

- run_research_task / tool_0019: ValidationError: 1 validation error for ReferenceReadResult
  Value error, read range must match text length [type=value_error, input_value={'namespace': <ArtifactNa...901659626671510374b73a'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0024: ValidationError: 1 validation error for ReferenceReadResult
  Value error, read range must match text length [type=value_error, input_value={'namespace': <ArtifactNa...901659626671510374b73a'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0028: BrowserDependencyError: Chromium runtime libraries are unavailable in both the system loader and the current Python environment; install them with 'playwright install-deps chromium' during deployment
- run_research_task / tool_0029: ValidationError: 1 validation error for ReferenceReadResult
  Value error, read range must match text length [type=value_error, input_value={'namespace': <ArtifactNa...901659626671510374b73a'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0034: ValidationError: 1 validation error for ReferenceReadResult
  Value error, read range must match text length [type=value_error, input_value={'namespace': <ArtifactNa...901659626671510374b73a'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0035: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0036: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0044: HarnessPolicyError: database_search tool-call budget exhausted
- run_research_task / tool_0049: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0052: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0058: ValidationError: 1 validation error for ReferenceReadResult
  Value error, read range must match text length [type=value_error, input_value={'namespace': <ArtifactNa...901659626671510374b73a'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0061: ValidationError: 1 validation error for ReferenceReadResult
  Value error, read range must match text length [type=value_error, input_value={'namespace': <ArtifactNa...901659626671510374b73a'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
- run_research_task / tool_0063: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0065: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
