# Runtime Summary

## Run

Paper ID: MG19333vrw-debug-full-20260907
Run ID: run-1978a1e85dc54f958289e728cc59dad6
Status: SUCCESS
Start: 2026-09-07T05:39:17.108498+00:00
End: 2026-09-07T05:42:50.527944+00:00
Duration: 215923 ms

## Environment

Git Branch: lya
Git Commit: 5909b50993fdad4de4caf49bb0ea0bf1a62930bb
Model: openai_compatible / deepseek-ai/DeepSeek-V4-Flash
Python: 3.11.15

## Stage Status

| Stage | Status | Duration |
|---|---|---:|
| extract_points | SUCCESS | 23682 ms |
| plan | SUCCESS | 0 ms |
| dispatch_planning_tasks | SUCCESS | 0 ms |
| plan_research_task | SUCCESS | 1893 ms |
| plan_research_task | SUCCESS | 2304 ms |
| plan_research_task | SUCCESS | 1932 ms |
| plan_research_task | SUCCESS | 2166 ms |
| plan_research_task | SUCCESS | 1967 ms |
| plan_research_task | SUCCESS | 3958 ms |
| dispatch_research_tasks | SUCCESS | 0 ms |
| run_research_task | SUCCESS | 87583 ms |
| run_research_task | SUCCESS | 124978 ms |
| run_research_task | SUCCESS | 86515 ms |
| run_research_task | SUCCESS | 122191 ms |
| run_research_task | SUCCESS | 59511 ms |
| run_research_task | SUCCESS | 57371 ms |
| validate_evidence | SUCCESS | 1 ms |
| review_evidence | SUCCESS | 24114 ms |
| validate_synthesis_input | SUCCESS | 6 ms |
| check_final_evidence_sufficiency | SUCCESS | 0 ms |
| synthesize_report | SUCCESS | 7490 ms |
| validate_report_integrity | SUCCESS | 0 ms |
| persist_report | SUCCESS | 0 ms |
| render_report | SUCCESS | 3 ms |
| plan_supplement | NOT_RUN | - ms |

## Tool Calls

| Tool | Calls | Success | Failed | Empty |
|---|---:|---:|---:|---:|
| reference_search | 6 | 6 | 0 | 6 |
| database_search | 6 | 6 | 0 | 3 |
| web_search | 18 | 10 | 8 | 0 |
| reader | 23 | 9 | 14 | 0 |
| browser | 12 | 4 | 8 | 0 |

## LLM Token Usage and Cost

Calls: 79
Input tokens: 603601
Cached input tokens: 414976
Output tokens: 16831
Reasoning tokens: 3110
Total tokens: 620432
Cost: RMB 0.84184680
Cost completeness: COMPLETE

| Model | Calls | Input | Cached | Output | Total | Cost (RMB) | Unpriced |
|---|---:|---:|---:|---:|---:|---:|---:|
| deepseek-ai/DeepSeek-V4-Flash | 79 | 603601 | 414976 | 16831 | 620432 | 0.84184680 | 0 |

## Final Evidence Sufficiency Checks

### Round 1

Configured cut: 1
Stage status: SUCCESS
Check status: INSUFFICIENT
Input final valid Cards: 1
Ignored Cards: 0
Output matches calculation: True
Round limit allows supplement: False
Actual next stage: synthesize_report

| Novelty Point | Valid Cards | Required Cards | Status |
|---|---:|---:|---|
| NP-1 | 0 | 1 | INSUFFICIENT |
| NP-2 | 1 | 1 | PASS |
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
| NP-2 | reviewed | partially_novel | 1 | True |
| NP-3 | insufficient_evidence | - | 0 | True |


## Errors

- run_research_task / tool_0009: BaiduSearchError: query exceeds Baidu's 72-unit limit (75)
- run_research_task / tool_0011: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0012: ValueError: unknown artifact_id 'art_1a8c528bc80025cb8f47a55f'
- run_research_task / tool_0013: ValueError: unknown artifact_id 'art_fb210e6a4ae2442f9e508d3e'
- run_research_task / tool_0016: ValueError: unknown artifact_id 'art_1a8c528bc80025cb8f47a55f'
- run_research_task / tool_0017: ValueError: unknown artifact_id 'art_1a8c528bc80025cb8f47a55f'
- run_research_task / tool_0018: ValueError: unknown artifact_id 'art_fb210e6a4ae2442f9e508d3e'
- run_research_task / tool_0020: ValueError: unknown artifact_id 'art_fb210e6a4ae2442f9e508d3e'
- run_research_task / tool_0021: ValueError: unknown artifact_id 'art_6e177beea223cf6b5d9af10e'
- run_research_task / tool_0023: ValueError: unknown artifact_id 'art_1a8c528bc80025cb8f47a55f'
- run_research_task / tool_0024: Error: Page.content: Unable to retrieve content because the page is navigating and changing the content.
- run_research_task / tool_0025: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0026: ValueError: unknown artifact_id 'art_1a8c528bc80025cb8f47a55f'
- run_research_task / tool_0027: ValueError: unknown source_record_id 'src_ee53d14f342a6624ac77a7bd'
- run_research_task / tool_0029: ValueError: unknown artifact_id 'art_11bcd7d5b4edcd225fe5854a'
- run_research_task / tool_0030: ValueError: unknown source_record_id 'src_a31519d9b0381f626aa2e2a5'
- run_research_task / tool_0031: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0032: BaiduSearchError: query exceeds Baidu's 72-unit limit (77)
- run_research_task / tool_0033: HarnessPolicyError: browser tool-call budget exhausted
- run_research_task / tool_0035: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0037: ValueError: unknown artifact_id 'art_8f245d06c2061148c86adbc4'
- run_research_task / tool_0040: ValueError: unknown artifact_id 'art_95ad6c557298c54466136c1d'
- run_research_task / tool_0044: HarnessPolicyError: reader required after database_search returned artifact_ids
- run_research_task / tool_0046: ValueError: unknown artifact_id 'art_1a8c528bc80025cb8f47a55f'
- run_research_task / tool_0048: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0047: Error: Page.content: Unable to retrieve content because the page is navigating and changing the content.
- run_research_task / tool_0054: Error: Page.content: Unable to retrieve content because the page is navigating and changing the content.
- run_research_task / tool_0060: BaiduSearchError: query exceeds Baidu's 72-unit limit (89)
- run_research_task / tool_0062: HarnessPolicyError: total tool-call budget exhausted
- run_research_task / tool_0063: HarnessPolicyError: total tool-call budget exhausted

## Integrity Gates

- validate_synthesis_input: PASS
- validate_report_integrity: PASS

## Last Completed Stage

render_report
