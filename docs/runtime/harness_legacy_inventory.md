# Harness runtime path inventory

This inventory records the soft-deprecation boundary after the task-scoped Harness
became the formal runtime. Nothing listed here is physically removed in this phase.

## ACTIVE

- `TaskResearchRequest` and `TaskResearcherWorkflow`: canonical task scope and Harness.
- `SearchPlanner` / `SearchPlannerAgent`: invoked once by `NoveltyWorkflow` before the
  task scope is constructed.
- `DatabaseSearchTool`, `WebSearchTool`, `BrowserTool`, `ReaderTool`: canonical tools.
- `StructuredSourceRetrievalTool`: active database implementation, consuming only
  `StructuredSourceRetrievalRequest.search_plan` at runtime.
- `SearchTool`, `FullTextTool`, `MetadataTool`: active provider-side ports behind
  `RetrievalSource`; they are not Researcher-facing tools.

## COMPATIBILITY

- `StructuredSourceRetrievalTool.search_planner` and matching factory arguments:
  retained for old constructors, ignored by the active execution path.
- `StructuredRetrievalResearcherTool` and `StructuredRetrievalToolArguments`: retained
  for historical experiments and null-catalog regressions. New code must use
  `DatabaseSearchTool`.
- `NoveltyResearchAgent` / `LiteratureResearchAgent`: retained for older tests and
  experiments; the formal workflow uses `TaskResearcherWorkflow`.
- `DemoQueryAdapter`: used by deterministic database tests.

## LEGACY / UNUSED

- `DemoResearchAgent`, `DemoSearchTool`: no formal workflow or current test constructs
  these implementations. They remain for historical demos only.
- `config.loader.legacy_shape`: compatibility projection for unmigrated callers; typed
  `ApplicationConfig` is the formal Composition Root.

## Constraints

- New code must not call Planner from database retrieval.
- Runtime-owned task, paper, run, and plan fields come from `TaskResearchRequest`.
- Compatibility symbols must not acquire new behavior before a separate removal task.
