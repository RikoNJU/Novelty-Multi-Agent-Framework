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
    RetrievalSource,
    RetrievalSourceRegistry,
    build_null_catalog_source,
)
from ..workflows import NoveltyWorkflow, NoveltyWorkflowConfig, NoveltyWorkflowServices

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
    search_planner = SearchPlannerAgent(
        prompts=prompts,
        models=registry,
        model_alias=search_planner_cfg.get(
            "model", research_cfg.get("model", "search_planner")
        ),
        temperature=float(search_planner_cfg.get("temperature", 0.2)),
    )
    return coordinator, research, point_extractor, search_planner


def build_source_registry() -> RetrievalSourceRegistry:
    """在组合根注册具体来源；Registry 本身没有来源条件分支。"""

    registry = RetrievalSourceRegistry()
    registry.register("arxiv", _build_arxiv_source_lazily)
    registry.register("null_catalog", build_null_catalog_source)
    return registry


def _build_arxiv_source_lazily(config: Mapping[str, Any]) -> RetrievalSource:
    """仅在 arXiv 赢得 active_source 选择后导入其具体实现。"""

    from ..tools.arxiv import build_arxiv_source

    return build_arxiv_source(config)


def build_retrieval_source(
    config: Mapping[str, Any],
    *,
    source_registry: RetrievalSourceRegistry | None = None,
) -> RetrievalSource:
    retrieval = _normalized_retrieval_config(config)
    source_id = str(retrieval.get("active_source", "arxiv"))
    sources = retrieval.get("sources", {})
    source_config = sources.get(source_id, {}) if isinstance(sources, Mapping) else {}
    registry = source_registry or build_source_registry()
    return registry.build(source_id, source_config)


def build_tools(config: Mapping[str, Any]):
    """兼容旧调用者，返回活动来源的三项检索工具。"""

    source = build_retrieval_source(config)
    return source.search_tool, source.full_text_tool, source.metadata_tool


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
    coordinator, research, point_extractor, search_planner = build_agents(
        raw, registry, prompts, retrieval_cfg=retrieval_cfg
    )
    source = build_retrieval_source(raw, source_registry=source_registry)

    workflow_cfg = raw.get("workflow", {})
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=coordinator,
            research_agent=research,
            search_planner=search_planner,
            query_adapter=source.query_adapter,
            point_extractor=point_extractor,
            search_tool=source.search_tool,
            full_text_tool=source.full_text_tool,
            metadata_tool=source.metadata_tool,
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
