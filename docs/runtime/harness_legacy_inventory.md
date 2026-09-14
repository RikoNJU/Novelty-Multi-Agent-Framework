# Harness runtime path inventory

This inventory records the soft-deprecation boundary after the task-scoped Harness
became the formal runtime. Entries marked REMOVED were physically deleted in the
cleanup pass; everything else listed here is still retained.

## ACTIVE

- `TaskResearchRequest` and `TaskResearcherWorkflow`: canonical task scope and Harness.
- `SearchPlanner` / `SearchPlannerAgent`: invoked once by `NoveltyWorkflow` before the
  task scope is constructed.
- `DatabaseSearchTool`, `WebSearchTool`, `BrowserTool`, `ReaderTool`: canonical tools.
- `StructuredSourceRetrievalTool`: active database implementation, consuming only
  `StructuredSourceRetrievalRequest.search_plan` at runtime.
- `SearchTool`, `FullTextTool`, `MetadataTool`: active provider-side ports behind
  `RetrievalSource`; they are not Researcher-facing tools.

## REMOVED

- `StructuredRetrievalResearcherTool` (formerly `tools/database_search/legacy_tool.py`)
  and `StructuredRetrievalToolArguments` (formerly `schemas/legacy_research_tools.py`):
  deleted, together with their package re-exports. Use `DatabaseSearchTool` and
  `DatabaseSearchArguments`.
- `ReferenceReaderToolArguments`: deleted alias for `ReaderArguments`; import
  `ReaderArguments` directly.

## COMPATIBILITY

- `StructuredSourceRetrievalTool.search_planner` and matching factory arguments:
  retained for old constructors, ignored by the active execution path.
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
- Removed symbols must not be reintroduced; `DatabaseSearchTool` is the only
  Researcher-facing database tool.
