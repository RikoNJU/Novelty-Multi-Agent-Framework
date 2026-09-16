# Baseline

- origin/lya HEAD: `43ba4fbcab4990042c28b19765e4ad7656eb1b22`
- origin/hyl HEAD: `b672d2540f3a579ab37e1a826ea0298da0c6b26b`
- merge-base: `ba266c246429d3b4901797cc589cdf7844756a44`
- Development baseline: latest origin/lya, branch `fix/arxiv-rate-limit-final`. Remote refs refreshed before comparison.
- Shared API scheduler: `5e2a005`, already present in lya.
- Ported from hyl: `67e5560` Web parser, transport, fixtures, tests, config inheritance; arxiv.py factory changes adapted manually because hyl has additional API policy changes.
- hyl-only arXiv commits: `5b3ff2c` (rate policy inside broader research changes), `44d7a1b` (merge), `67e5560` (Web channel).
- hyl-only API policy changes preceding 67e5560 are not needed for the Web fix; retain lya scheduler and validate it independently.
- Retained lya-only relevant changes: `4fba6e6` successful retrieval cache / batch reader; `dfd66f6` structured outputs and search execution preservation.
- Excluded hyl changes: Reviewer, Renderer, SearchPlanner prompt, Springer, reference prefilter/coverage, workflow changes and historical experiment dumps. No whole-branch merge.

## Instance lifecycle

`config/factory.py:_build_workflow_from_application_config` builds one database tool registry per workflow. `database_search/factory.py` builds one `RetrievalSource` per enabled provider. Every ResearchTask shares that registry, hence search/metadata share one Web Session in a workflow. A second workflow, standalone tool or bootstrap factory can still instantiate another Session; all Sessions now use the same process-wide Web gate. The gate covers search, /abs/ and Web-mode HTML/PDF acquisition. `asyncio.to_thread` preserves task/runtime context. Research Task max_concurrency remains 4.

The gate uses the largest interval configured by any Session during the process lifetime. Independent processes are outside this in-process scheduler's scope. Interval staircase experiments run in separate, sequential processes.

## Final implementation commits

- `9222d37`: bounded shared Web transport, provider failure propagation, API/Web request diagnostics.
- `674c7ff`: hyl fixtures, offline acceptance, extensions of existing smoke scripts.
