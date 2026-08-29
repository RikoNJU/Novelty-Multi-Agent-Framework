"""配置驱动的组合根。

读取 ``models`` / ``agents`` 配置，构建 ModelRegistry、PromptLibrary 和各角色
Agent，最后装配成 NoveltyWorkflow。Demo 装配仍由 ``NoveltyWorkflow.default``
保留，供测试和无模型环境使用。
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any, Mapping

from backend.env import ModelCallOptions, ModelProfile, ModelRegistry, PromptLibrary

from ..agents import (
    EvidenceReviewerConfig,
    NoveltyCoordinatorAgent,
    NoveltyEvidenceReviewer,
    NoveltyPointExtractorAgent,
    NoveltyResearchAgent,
    SearchPlannerAgent,
)
from ..tools import (
    BaiduSearchBackend,
    BrowserTool,
    EvidenceCardBuilder,
    PlaywrightBrowserBackend,
    ReferenceArtifactReaderTool,
    ReaderTool,
    ResearcherToolRegistry,
    WebSearchTool,
)
from ..tools.database_search import (
    RetrievalSource,
    RetrievalSourceRegistry,
    StructuredSourceRetrievalTool,
)
from ..tools.database_search.factory import (
    build_database_search_tool,
    build_retrieval_source as build_database_retrieval_source,
    build_source_registry as build_database_source_registry,
    build_structured_source_retrieval_tool as build_database_structured_tool,
)
from ..persistence import ReferenceStore
from ..workflows import (
    NoveltyWorkflow,
    NoveltyWorkflowConfig,
    NoveltyWorkflowServices,
    TaskResearcherConfig,
    TaskResearcherWorkflow,
)
from .loader import legacy_shape, load_application_config, read_json
from .schemas import ApplicationConfig, ModelInvocationConfig

CONFIG_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = CONFIG_DIR / "settings.example.json"
PROMPTS_ROOT = Path(__file__).resolve().parents[1] / "prompts"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Compatibility shape; new code should call load_application_config()."""

    if path is not None:
        return read_json(path)
    return legacy_shape(load_application_config())


def build_model_registry(
    config: Mapping[str, Any] | ApplicationConfig,
) -> ModelRegistry:
    profiles: dict[str, ModelProfile] = {}
    model_items = (
        config.models.items()
        if isinstance(config, ApplicationConfig)
        else config.get("models", {}).items()
    )
    for alias, value in model_items:
        raw = value.model_dump(mode="python") if hasattr(value, "model_dump") else value
        profiles[alias] = ModelProfile(
            alias=alias,
            provider=raw.get("provider", "openai_compatible"),
            model=raw["model"],
            base_url=raw.get("base_url", "https://api.openai.com/v1"),
            api_key=_resolve_api_key(raw),
            context_window=int(raw.get("context_window", 128_000)),
            supported_params=frozenset(raw.get("supported_params", [])),
            defaults={},
        )
    return ModelRegistry(profiles)


def _resolve_api_key(raw: Mapping[str, Any]) -> str | None:
    env_name = raw.get("api_key_env")
    if env_name:
        value = os.getenv(env_name)
        if value:
            return value
    return os.getenv("NOVELTY_API_KEY") or os.getenv("LLM_API_KEY")


def build_prompt_library(root: str | Path | None = None) -> PromptLibrary:
    return PromptLibrary(root or PROMPTS_ROOT)


def build_agents(
    config: Mapping[str, Any],
    registry: ModelRegistry,
    prompts: PromptLibrary,
    retrieval_cfg: Mapping[str, Any] | None = None,
) -> tuple[
    NoveltyCoordinatorAgent,
    NoveltyResearchAgent,
    NoveltyPointExtractorAgent,
    SearchPlannerAgent,
]:
    agents_cfg = config.get("agents", {})
    coordinator_cfg = agents_cfg.get("coordinator", {})
    research_cfg = agents_cfg.get("research", {})
    point_extractor_cfg = agents_cfg.get("point_extractor", {})
    search_planner_cfg = agents_cfg.get("search_planner", {})
    retrieval_cfg = dict(retrieval_cfg or {})

    coordinator = NoveltyCoordinatorAgent(
        prompts=prompts,
        models=registry,
        model_alias=coordinator_cfg.get("model", "coordinator"),
        temperature=float(coordinator_cfg.get("temperature", 0.2)),
    )
    research = NoveltyResearchAgent(
        prompts=prompts,
        models=registry,
        model_alias=research_cfg.get("model", "research"),
        temperature=float(research_cfg.get("temperature", 0.2)),
        candidate_excerpt_chars=int(retrieval_cfg.get("candidate_excerpt_chars", 2000)),
    )
    point_extractor = NoveltyPointExtractorAgent(
        prompts=prompts,
        models=registry,
        model_alias=point_extractor_cfg.get("model", "point_extractor"),
        temperature=float(point_extractor_cfg.get("temperature", 0.2)),
    )
    search_planner = build_search_planner(
        config, registry, prompts, retrieval_cfg=retrieval_cfg
    )
    return coordinator, research, point_extractor, search_planner


def build_search_planner(
    config: Mapping[str, Any],
    registry: ModelRegistry,
    prompts: PromptLibrary,
    *,
    retrieval_cfg: Mapping[str, Any] | None = None,
) -> SearchPlannerAgent:
    """单独构建 SearchPlanner，供检索 Tool 组合根复用。"""

    agents_cfg = config.get("agents", {})
    research_cfg = agents_cfg.get("research", {})
    search_planner_cfg = agents_cfg.get("search_planner", {})
    runtime = config.get("search_planner_runtime", {})
    invocation = runtime.get("model", {})
    return SearchPlannerAgent(
        prompts=prompts,
        models=registry,
        model_alias=search_planner_cfg.get(
            "model", research_cfg.get("model", "search_planner")
        ),
        temperature=float(search_planner_cfg.get("temperature", 0.2)),
        model_options=(
            _model_options(invocation, response_format={"type": "json_object"})
            if invocation else None
        ),
        max_attempts=int(runtime.get("max_attempts", 2)),
        prompt_name=str(runtime.get("prompt", "search_planner/plan")),
    )


def build_source_registry() -> RetrievalSourceRegistry:
    """兼容入口；数据库组合职责已收束到 database_search。"""

    return build_database_source_registry()


def build_retrieval_source(
    config: Mapping[str, Any],
    *,
    source_registry: RetrievalSourceRegistry | None = None,
) -> RetrievalSource:
    return build_database_retrieval_source(
        _normalized_retrieval_config(config), source_registry=source_registry
    )


def build_tools(config: Mapping[str, Any]):
    """兼容旧调用者，返回活动来源的三项检索工具。"""

    source = build_retrieval_source(config)
    return source.search_tool, source.full_text_tool, source.metadata_tool


def build_structured_source_retrieval_tool(
    config: Mapping[str, Any],
    *,
    source_registry: RetrievalSourceRegistry | None = None,
) -> StructuredSourceRetrievalTool:
    """构建独立检索 Tool；不接入或修改现有 NoveltyWorkflow。"""

    raw = copy.deepcopy(dict(config))
    _apply_env_overrides(raw)
    models = build_model_registry(raw)
    prompts = build_prompt_library()
    retrieval_cfg = _normalized_retrieval_config(raw)
    search_planner = build_search_planner(
        raw, models, prompts, retrieval_cfg=retrieval_cfg
    )
    workflow_cfg = raw.get("workflow", {})
    return build_database_structured_tool(
        retrieval_cfg,
        search_planner=search_planner,
        source_registry=source_registry,
        max_concurrency=int(workflow_cfg.get("max_concurrency", 4)),
    )


def build_workflow(
    config: Mapping[str, Any] | ApplicationConfig | None = None,
    *,
    config_path: str | Path | None = None,
    source_registry: RetrievalSourceRegistry | None = None,
) -> NoveltyWorkflow:
    """从配置构建完整工作流；``config`` 优先于 ``config_path``。"""

    if isinstance(config, ApplicationConfig):
        return _build_workflow_from_application_config(
            config, source_registry=source_registry
        )
    if config is None and config_path is None:
        return _build_workflow_from_application_config(
            load_application_config(), source_registry=source_registry
        )

    raw = (
        load_config(config_path) if config is None else copy.deepcopy(dict(config))
    )
    _apply_env_overrides(raw)

    registry = build_model_registry(raw)
    prompts = build_prompt_library()
    retrieval_cfg = _normalized_retrieval_config(raw)
    if "retrieval" not in raw:
        retrieval_cfg.setdefault("sources", {}).setdefault("arxiv", {})[
            "adapter_only"
        ] = False
    agents_cfg = raw.get("agents", {})
    coordinator_cfg = agents_cfg.get("coordinator", {})
    point_extractor_cfg = agents_cfg.get("point_extractor", {})
    research_cfg = agents_cfg.get("research", {})
    coordinator = NoveltyCoordinatorAgent(
        prompts=prompts,
        models=registry,
        model_alias=coordinator_cfg.get("model", "coordinator"),
        temperature=float(coordinator_cfg.get("temperature", 0.2)),
    )
    point_extractor = NoveltyPointExtractorAgent(
        prompts=prompts,
        models=registry,
        model_alias=point_extractor_cfg.get("model", "point_extractor"),
        temperature=float(point_extractor_cfg.get("temperature", 0.2)),
    )
    research_model = registry.client_for(research_cfg.get("model", "research"))
    search_planner = build_search_planner(
        raw, registry, prompts, retrieval_cfg=retrieval_cfg
    )
    reviewer_cfg = agents_cfg.get("reviewer", {})
    reviewer = (
        NoveltyEvidenceReviewer(
            prompts=prompts,
            models=registry,
            config=EvidenceReviewerConfig(
                enabled=True,
                model_alias=str(reviewer_cfg.get("model", "reviewer")),
                temperature=float(reviewer_cfg.get("temperature", 0.0)),
                max_cards_per_call=int(reviewer_cfg.get("max_cards_per_call", 8)),
                fail_closed=bool(reviewer_cfg.get("fail_closed", True)),
            ),
        )
        if reviewer_cfg.get("enabled", False)
        else None
    )

    workflow_cfg = raw.get("workflow", {})
    researcher_runtime = raw.get("researcher_runtime", {})
    runtime_tools = researcher_runtime.get("tools", {})
    web_cfg = runtime_tools.get("web_search", {})
    browser_cfg = runtime_tools.get("browser", {})
    reader_cfg = runtime_tools.get("reader", {})
    store = ReferenceStore()
    tool_registry = ResearcherToolRegistry(
        [
            build_database_search_tool(
                retrieval_cfg,
                reference_store=store,
                source_registry=source_registry,
                max_concurrency=int(retrieval_cfg["max_concurrency"]),
            ),
            WebSearchTool(
                BaiduSearchBackend(
                    timeout_seconds=float(
                        web_cfg.get("baidu", {}).get("timeout_seconds", 30.0)
                    )
                ),
                store,
                default_max_results=int(web_cfg.get("default_max_results", 10)),
                max_results_per_call=int(web_cfg.get("max_results_per_call", 50)),
            ),
            BrowserTool(
                PlaywrightBrowserBackend(
                    network_mode=str(browser_cfg.get("network_mode", "inherit")),
                    navigation_timeout_ms=int(
                        browser_cfg.get("navigation_timeout_ms", 30_000)
                    ),
                    max_html_chars=int(browser_cfg.get("max_html_chars", 2_000_000)),
                    max_text_chars=int(browser_cfg.get("max_text_chars", 500_000)),
                ),
                store,
            ),
            ReaderTool(
                ReferenceArtifactReaderTool(
                    store,
                    max_chars_per_read=int(
                        reader_cfg.get("max_chars_per_read", 16_000)
                    ),
                ),
                default_chars_per_read=int(
                    reader_cfg.get("default_chars_per_read", 8_000)
                ),
            ),
        ]
    )
    budget_cfg = raw.get("task_researcher", {})
    task_researcher = TaskResearcherWorkflow(
        research_model,
        tool_registry,
        EvidenceCardBuilder(store),
        prompts=prompts,
        config=TaskResearcherConfig(
            max_steps=int(budget_cfg.get("max_steps", 12)),
            max_tool_calls=int(budget_cfg.get("max_tool_calls", 10)),
            max_chars_per_read=int(budget_cfg.get("max_chars_per_read", 8_000)),
            max_total_read_chars=int(
                budget_cfg.get("max_total_read_chars", 48_000)
            ),
            per_tool_limits=dict(
                budget_cfg.get(
                    "per_tool_limits",
                    {
                        "database_search": 2,
                        "web_search": 3,
                        "browser": 3,
                        "reader": 8,
                    },
                )
            ),
            model_options=(
                _model_options(researcher_runtime.get("model", {}))
                if researcher_runtime
                else ModelCallOptions(temperature=0.0, tool_choice="auto")
            ),
            prompt_name=str(
                researcher_runtime.get("prompt", "research/native_tool_loop")
            ),
        ),
    )
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=coordinator,
            task_researcher=task_researcher,
            search_planner=search_planner,
            point_extractor=point_extractor,
            reviewer=reviewer,
        ),
        config=NoveltyWorkflowConfig(
            max_rounds=int(workflow_cfg.get("max_rounds", 2)),
            max_concurrency=int(workflow_cfg.get("max_concurrency", 4)),
            minimum_evidence_per_point=int(
                workflow_cfg.get("minimum_evidence_per_point", 1)
            ),
            candidate_limit_per_task=int(
                retrieval_cfg.get("candidate_limit_per_task", 8)
            ),
        ),
    )


def _build_workflow_from_application_config(
    config: ApplicationConfig,
    *,
    source_registry: RetrievalSourceRegistry | None = None,
) -> NoveltyWorkflow:
    """Build the production workflow directly from validated typed fields."""

    registry = build_model_registry(config)
    prompts = build_prompt_library()
    coordinator = NoveltyCoordinatorAgent(
        prompts=prompts,
        models=registry,
        model_alias=config.coordinator.model.alias,
        temperature=config.coordinator.model.temperature,
    )
    point_extractor = NoveltyPointExtractorAgent(
        prompts=prompts,
        models=registry,
        model_alias=config.point_extractor.model.alias,
        temperature=config.point_extractor.model.temperature,
    )
    search_planner = SearchPlannerAgent(
        prompts=prompts,
        models=registry,
        model_alias=config.search_planner.model.alias,
        temperature=config.search_planner.model.temperature,
        model_options=_typed_model_options(
            config.search_planner.model,
            response_format={"type": "json_object"},
        ),
        max_attempts=config.search_planner.max_attempts,
        prompt_name=config.search_planner.prompt,
    )
    reviewer = (
        NoveltyEvidenceReviewer(
            prompts=prompts,
            models=registry,
            config=EvidenceReviewerConfig(
                enabled=True,
                model_alias=config.reviewer.model.alias,
                temperature=config.reviewer.model.temperature,
                max_cards_per_call=config.reviewer.max_cards_per_call,
                fail_closed=config.reviewer.fail_closed,
            ),
        )
        if config.reviewer is not None and config.reviewer.enabled
        else None
    )

    database = config.researcher.tools.database_search
    retrieval = {
        "active_source": database.active_source,
        "candidate_limit_per_task": database.candidate_limit_per_task,
        "candidate_excerpt_chars": database.candidate_excerpt_chars,
        "full_text_limit_per_task": database.full_text_limit_per_task,
        "max_concurrency": database.max_concurrency,
        "sources": database.providers,
    }
    web = config.researcher.tools.web_search
    browser = config.researcher.tools.browser
    reader = config.researcher.tools.reader
    store = ReferenceStore()
    tool_registry = ResearcherToolRegistry(
        [
            build_database_search_tool(
                retrieval,
                reference_store=store,
                source_registry=source_registry,
                max_concurrency=database.max_concurrency,
            ),
            WebSearchTool(
                BaiduSearchBackend(
                    timeout_seconds=float(web.baidu.get("timeout_seconds", 30.0))
                ),
                store,
                default_max_results=web.default_max_results,
                max_results_per_call=web.max_results_per_call,
            ),
            BrowserTool(
                PlaywrightBrowserBackend(
                    network_mode=browser.network_mode,
                    navigation_timeout_ms=browser.navigation_timeout_ms,
                    max_html_chars=browser.max_html_chars,
                    max_text_chars=browser.max_text_chars,
                ),
                store,
            ),
            ReaderTool(
                ReferenceArtifactReaderTool(
                    store, max_chars_per_read=reader.max_chars_per_read
                ),
                default_chars_per_read=reader.default_chars_per_read,
            ),
        ]
    )
    researcher = config.researcher
    task_researcher = TaskResearcherWorkflow(
        registry.client_for(researcher.model.alias),
        tool_registry,
        EvidenceCardBuilder(store),
        prompts=prompts,
        config=TaskResearcherConfig(
            max_steps=researcher.harness.max_turns,
            max_tool_calls=researcher.harness.max_total_tool_calls,
            max_chars_per_read=reader.max_chars_per_read,
            max_total_read_chars=reader.max_total_read_chars,
            per_tool_limits=dict(researcher.harness.per_tool_limits),
            model_options=_typed_model_options(researcher.model),
            prompt_name=researcher.prompt,
        ),
    )
    workflow = config.project.workflow
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=coordinator,
            task_researcher=task_researcher,
            search_planner=search_planner,
            point_extractor=point_extractor,
            reviewer=reviewer,
        ),
        config=NoveltyWorkflowConfig(
            max_rounds=workflow.max_rounds,
            max_concurrency=workflow.max_concurrency,
            minimum_evidence_per_point=workflow.minimum_evidence_per_point,
            candidate_limit_per_task=database.candidate_limit_per_task,
        ),
    )


def _normalized_retrieval_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """读取新配置，并把历史 ``tools.arxiv`` 形状映射到通用结构。"""

    if "retrieval" in config:
        retrieval = copy.deepcopy(dict(config.get("retrieval", {})))
        # 过渡期允许旧开关显式启用 arXiv，避免既有部署静默失效。
        legacy_arxiv = config.get("tools", {}).get("arxiv", {})
        if legacy_arxiv.get("enabled"):
            retrieval.setdefault("sources", {}).setdefault("arxiv", {}).update(
                legacy_arxiv
            )
        retrieval.setdefault(
            "max_concurrency",
            int(config.get("workflow", {}).get("max_concurrency", 4)),
        )
        _adapt_legacy_arxiv_provider(retrieval)
        return retrieval
    arxiv = dict(config.get("tools", {}).get("arxiv", {}))
    # 旧配置没有来源选择语义：保留“Adapter 可用、网络工具关闭”的兼容行为。
    arxiv["adapter_only"] = not arxiv.get("enabled", False)
    arxiv["enabled"] = True
    retrieval = {
        "active_source": "arxiv",
        "candidate_limit_per_task": arxiv.get("candidate_limit", 8),
        "candidate_excerpt_chars": arxiv.get("candidate_excerpt_chars", 2000),
        "full_text_limit_per_task": arxiv.get("full_text_limit", 8),
        "max_concurrency": int(config.get("workflow", {}).get("max_concurrency", 4)),
        "sources": {"arxiv": arxiv},
    }
    _adapt_legacy_arxiv_provider(retrieval)
    return retrieval


def _adapt_legacy_arxiv_provider(retrieval: dict[str, Any]) -> None:
    """Compatibility-only key adaptation; split config already uses canonical keys."""

    arxiv = retrieval.get("sources", {}).get("arxiv")
    if not isinstance(arxiv, dict):
        return
    arxiv.setdefault("min_interval_seconds", arxiv.pop("min_interval", 3.0))
    arxiv.setdefault("timeout_seconds", arxiv.pop("timeout", 20.0))
    arxiv.setdefault("max_retries", 2)
    arxiv.setdefault("full_text_max_chars", 100_000)


def _apply_env_overrides(config: dict[str, Any]) -> None:
    """用 NOVELTY_<角色>_MODEL 覆盖 agents 里的模型别名。"""

    for role, agent_cfg in config.get("agents", {}).items():
        env_value = os.getenv(f"NOVELTY_{role.upper()}_MODEL")
        if env_value:
            agent_cfg["model"] = env_value


def _model_options(
    config: Mapping[str, Any],
    *,
    response_format: Mapping[str, Any] | None = None,
) -> ModelCallOptions:
    extra_body = {
        key: config[key]
        for key in ("enable_thinking", "thinking_budget", "reasoning_effort")
        if config.get(key) is not None
    }
    return ModelCallOptions(
        temperature=float(config["temperature"]),
        max_tokens=int(config["max_tokens"]),
        timeout_seconds=float(config["timeout_seconds"]),
        tool_choice=config.get("tool_choice"),
        response_format=response_format,
        extra_body=extra_body,
    )


def _typed_model_options(
    config: ModelInvocationConfig,
    *,
    response_format: Mapping[str, Any] | None = None,
) -> ModelCallOptions:
    extra_body = {
        key: value
        for key, value in {
            "enable_thinking": config.enable_thinking,
            "thinking_budget": config.thinking_budget,
            "reasoning_effort": config.reasoning_effort,
        }.items()
        if value is not None
    }
    return ModelCallOptions(
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        timeout_seconds=config.timeout_seconds,
        tool_choice=config.tool_choice,
        response_format=response_format,
        extra_body=extra_body,
    )
