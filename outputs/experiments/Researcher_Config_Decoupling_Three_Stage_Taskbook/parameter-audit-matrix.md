# Researcher Runtime Parameter Audit Matrix

| parameter | old owner/default | new owner | runtime consumer | config path | enforced | reason |
| --- | --- | --- | --- | --- | --- | --- |
| Researcher model alias | `agents.research.model` | Researcher | ModelRegistry lookup | `researcher.model.alias` | yes | role model selection |
| Researcher temperature | workflow hardcoded `0.0` / agent `0.3` | Researcher | `ModelCallOptions` | `researcher.model.temperature` | yes | invocation behavior |
| Researcher max tokens | model profile defaults `4096` | Researcher | `ModelCallOptions` | `researcher.model.max_tokens` | yes | invocation budget |
| Researcher timeout | model profile defaults `300` | Researcher | `ModelCallOptions` | `researcher.model.timeout_seconds` | yes | invocation timeout |
| Researcher tool choice | workflow hardcoded `auto` | Researcher | `ModelCallOptions` | `researcher.model.tool_choice` | yes | invocation policy |
| thinking options | model profile defaults/none | invoking agent | `ModelCallOptions.extra_body` | `*.model.enable_thinking/thinking_budget/reasoning_effort` | yes | provider invocation |
| prompt name | workflow hardcoded | Researcher | PromptLibrary render | `researcher.prompt` | yes | prompt selection |
| max turns | `TaskResearcherConfig=12` | Researcher Harness | ToolCallHarness | `researcher.harness.max_turns` | yes | runtime budget |
| total tool calls | `TaskResearcherConfig=10` | Researcher Harness | ToolCallHarness | `researcher.harness.max_total_tool_calls` | yes | runtime budget |
| per-tool calls | config existed but unused | Researcher Harness | ToolCallHarness | `researcher.harness.per_tool_limits.*` | yes | prevent one-tool repetition |
| DB candidate limit | retrieval/factory fallback `8` | DatabaseSearch | Structured retrieval | `researcher.tools.database_search.candidate_limit_per_task` | yes | recall size |
| DB fulltext limit | factory fallback `8` | DatabaseSearch | Structured retrieval | `researcher.tools.database_search.full_text_limit_per_task` | yes | acquisition size |
| DB concurrency | borrowed workflow concurrency `4` | DatabaseSearch | Structured retrieval semaphores | `researcher.tools.database_search.max_concurrency` | yes | DB-owned concurrency |
| provider selection | retrieval active source | DatabaseSearch | DB factory | `researcher.tools.database_search.providers.*.enabled` | yes | provider composition |
| arXiv interval | provider fallback `3s` | arXiv provider | ArxivSearchTool | `...providers.arxiv.min_interval_seconds` | yes | throttling |
| arXiv timeout | provider fallback `20s` | arXiv provider | httpx client | `...providers.arxiv.timeout_seconds` | yes | network timeout |
| arXiv retries | provider fallback `2` | arXiv provider | ArxivSearchTool | `...providers.arxiv.max_retries` | yes | retry budget |
| arXiv fulltext chars | provider fallback `100000` | arXiv provider | ArxivFullTextTool | `...providers.arxiv.full_text_max_chars` | yes | content limit |
| Web backend | factory hardcoded Baidu | Researcher WebSearch | factory | `researcher.tools.web_search.backend` | validated/injected | deployment selection |
| Web default results | schema default `10` | Researcher WebSearch | configured args schema/tool | `researcher.tools.web_search.default_max_results` | yes | result size |
| Web max results | Baidu protocol `50` mixed with schema | Researcher WebSearch | configured args schema/tool | `researcher.tools.web_search.max_results_per_call` | yes | runtime cap; provider hard cap remains code |
| Baidu timeout | backend fallback `30s` | Baidu backend | httpx client | `researcher.tools.web_search.baidu.timeout_seconds` | yes | network timeout |
| Browser backend | factory hardcoded Playwright | Researcher Browser | factory | `researcher.tools.browser.backend` | validated/injected | deployment selection |
| Browser navigation timeout | backend fallback `30000ms` | Researcher Browser | Playwright backend | `researcher.tools.browser.navigation_timeout_ms` | yes | navigation timeout |
| Browser HTML chars | backend fallback `2000000` | Researcher Browser | Playwright backend | `researcher.tools.browser.max_html_chars` | yes | content limit |
| Browser text chars | backend fallback `500000` | Researcher Browser | Playwright backend | `researcher.tools.browser.max_text_chars` | yes | content limit |
| Reader default chars | schema default `8000` | Researcher Reader | configured args schema | `researcher.tools.reader.default_chars_per_read` | yes | default slice |
| Reader max per read | reader fallback `16000` | Researcher Reader | ReferenceArtifactReaderTool | `researcher.tools.reader.max_chars_per_read` | yes | per-call safety limit |
| Reader total chars | config existed but unused `48000` | Researcher Harness | ToolCallHarness accumulator | `researcher.tools.reader.max_total_read_chars` | yes | cumulative context budget |
| SearchPlanner model alias | agents config | SearchPlanner | ModelRegistry lookup | `search_planner.model.alias` | yes | lightweight model isolation |
| SearchPlanner invocation | model defaults + temperature | SearchPlanner | `ModelCallOptions` | `search_planner.model.*` | yes | invocation behavior |
| SearchPlanner attempts | module constant `2` | SearchPlanner | SearchPlanner loop | `search_planner.max_attempts` | yes | retry budget |

安全与协议常量未配置化：serial 单 ToolCall、private/localhost 浏览限制、SearchPlan 语义校验、trusted provenance 边界、Evidence 只能来自 Reader、Baidu 协议硬上限。
