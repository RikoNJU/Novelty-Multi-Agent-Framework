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

from backend.env import ModelProfile, ModelRegistry, PromptLibrary

from ..agents import (
    NoveltyCoordinatorAgent,
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

CONFIG_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = CONFIG_DIR / "settings.example.json"
PROMPTS_ROOT = Path(__file__).resolve().parents[1] / "prompts"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_PATH
    with config_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def build_model_registry(config: Mapping[str, Any]) -> ModelRegistry:
    profiles: dict[str, ModelProfile] = {}
    for alias, raw in config.get("models", {}).items():
        profiles[alias] = ModelProfile(
            alias=alias,
            provider=raw.get("provider", "openai_compatible"),
            model=raw["model"],
            base_url=raw.get("base_url", "https://api.openai.com/v1"),
            api_key=_resolve_api_key(raw),
            context_window=int(raw.get("context_window", 128_000)),
            supported_params=frozenset(raw.get("supported_params", [])),
            defaults=dict(raw.get("defaults", {})),
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
    return SearchPlannerAgent(
        prompts=prompts,
        models=registry,
        model_alias=search_planner_cfg.get(
            "model", research_cfg.get("model", "search_planner")
        ),
        temperature=float(search_planner_cfg.get("temperature", 0.2)),
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
    config: Mapping[str, Any] | None = None,
    *,
    config_path: str | Path | None = None,
    source_registry: RetrievalSourceRegistry | None = None,
) -> NoveltyWorkflow:
    """从配置构建完整工作流；``config`` 优先于 ``config_path``。"""

    raw = load_config(config_path) if config is None else copy.deepcopy(dict(config))
    _apply_env_overrides(raw)

    registry = build_model_registry(raw)
    prompts = build_prompt_library()
    retrieval_cfg = _normalized_retrieval_config(raw)
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

    workflow_cfg = raw.get("workflow", {})
    store = ReferenceStore()
    tool_registry = ResearcherToolRegistry(
        [
            WebSearchTool(BaiduSearchBackend(), store),
            BrowserTool(PlaywrightBrowserBackend(), store),
            ReaderTool(ReferenceArtifactReaderTool(store)),
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
                        "web_search": 3,
                        "browser": 3,
                        "reader": 8,
                    },
                )
            ),
        ),
    )
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=coordinator,
            task_researcher=task_researcher,
            point_extractor=point_extractor,
        ),
        config=NoveltyWorkflowConfig(
            max_rounds=int(workflow_cfg.get("max_rounds", 2)),
            max_concurrency=int(workflow_cfg.get("max_concurrency", 4)),
            minimum_evidence_per_point=int(
                workflow_cfg.get("minimum_evidence_per_point", 1)
            ),
            candidate_limit_per_task=int(retrieval_cfg.get("candidate_limit_per_task", 8)),
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
        return retrieval
    arxiv = dict(config.get("tools", {}).get("arxiv", {}))
    # 旧配置没有来源选择语义：保留“Adapter 可用、网络工具关闭”的兼容行为。
    arxiv["adapter_only"] = not arxiv.get("enabled", False)
    arxiv["enabled"] = True
    return {
        "active_source": "arxiv",
        "candidate_limit_per_task": arxiv.get("candidate_limit", 8),
        "candidate_excerpt_chars": arxiv.get("candidate_excerpt_chars", 2000),
        "sources": {"arxiv": arxiv},
    }


def _apply_env_overrides(config: dict[str, Any]) -> None:
    """用 NOVELTY_<角色>_MODEL 覆盖 agents 里的模型别名。"""

    for role, agent_cfg in config.get("agents", {}).items():
        env_value = os.getenv(f"NOVELTY_{role.upper()}_MODEL")
        if env_value:
            agent_cfg["model"] = env_value
