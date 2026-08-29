# Harness convergence single-task experiment

Date: 2026-08-29

## Runtime boundary

The experiment used the formal chain:

`SearchPlanner -> TaskResearchRequest.search_plan -> TaskResearcherWorkflow -> database_search -> StructuredSourceRetrievalTool -> reader -> EvidenceCardBuilder`

`StructuredSourceRetrievalTool.search_planner` was replaced with a guard that raises
`AssertionError` on every call. The task still completed in the deterministic run,
proving that the compatibility dependency is not read by the active path.

## Deterministic end-to-end result

- Enabled tools: `database_search`, `reader`
- Workflow Planner calls: 1
- Legacy retrieval Planner calls: 0
- Search executions: 1
- Research bundles: 1
- Reader results: 1
- Evidence cards: 1
- Task status: `completed`
- Warnings: none

The executed strategy ID matched `TaskResearchRequest.search_plan.strategies[0]`.
This run is implemented as
`test_single_task_uses_scope_plan_without_legacy_planner` and is part of the offline
regression suite.

## Live run result

The first live run selected `MF2033k6lC / NP-1 / T-1` with only
`database_search` and `reader` registered.

- Workflow Planner calls: 1
- Legacy retrieval Planner calls: 0
- WebSearch calls: 0
- Browser calls: 0
- DatabaseSearch calls: 2
- Candidate works: 0
- Reader calls: 0
- Evidence cards: 0
- Task status: `partial`
- Terminal warning: `database_search tool-call budget exhausted`

The strict plan executed, while medium and broad expressions were rejected by the
existing query adapter because they contain unsupported literal tokens. arXiv returned
no candidates, so Reader and EvidenceCardBuilder had no source material. This is a
retrieval/plan-quality outcome, not a duplicate-Planner or runtime-injection failure;
those behaviors are outside this refactor's allowed scope.

An English-task retry was terminated by the five-minute external-call timeout and did
not produce a replacement result.

Live artifacts are stored under
`outputs/experiments/mf2033k6lc-v3-researcher-attempt3/`.
