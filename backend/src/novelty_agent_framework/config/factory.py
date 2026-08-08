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

import httpx

from backend.env import ModelProfile, ModelRegistry, PromptLibrary

from ..agents import (
    NoveltyCoordinatorAgent,
    NoveltyPointExtractorAgent,
    NoveltyResearchAgent,
)
from ..tools import ArxivFullTextTool, ArxivMetadataTool, ArxivSearchTool
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
    arxiv_cfg: Mapping[str, Any] | None = None,
) -> tuple[
    NoveltyCoordinatorAgent,
    NoveltyResearchAgent,
    NoveltyPointExtractorAgent,
]:
    agents_cfg = config.get("agents", {})
    coordinator_cfg = agents_cfg.get("coordinator", {})
    research_cfg = agents_cfg.get("research", {})
    point_extractor_cfg = agents_cfg.get("point_extractor", {})
    arxiv_cfg = dict(arxiv_cfg or {})

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
        candidate_limit=int(arxiv_cfg.get("candidate_limit", 8)),
        candidate_excerpt_chars=int(arxiv_cfg.get("candidate_excerpt_chars", 2000)),
        paper_excerpt_chars=int(arxiv_cfg.get("paper_excerpt_chars", 5000)),
    )
    point_extractor = NoveltyPointExtractorAgent(
        prompts=prompts,
        models=registry,
        model_alias=point_extractor_cfg.get("model", "point_extractor"),
        temperature=float(point_extractor_cfg.get("temperature", 0.2)),
    )
    return coordinator, research, point_extractor


def build_tools(
    config: Mapping[str, Any],
) -> tuple[ArxivSearchTool | None, ArxivFullTextTool | None, ArxivMetadataTool | None]:
    """按配置构建 arXiv 三工具；未启用时返回 (None, None, None) 保持现状。"""

    arxiv_cfg = config.get("tools", {}).get("arxiv", {})
    if not arxiv_cfg.get("enabled", False):
        return None, None, None
    client = httpx.Client(
        timeout=float(arxiv_cfg.get("timeout", 20.0)),
        follow_redirects=True,
    )
    search = ArxivSearchTool(
        client=client,
        min_interval=float(arxiv_cfg.get("min_interval", 3.0)),
        max_retries=int(arxiv_cfg.get("max_retries", 2)),
    )
    return search, ArxivFullTextTool(client=client), ArxivMetadataTool(client=client)


def build_workflow(
    config: Mapping[str, Any] | None = None,
    *,
    config_path: str | Path | None = None,
) -> NoveltyWorkflow:
    """从配置构建完整工作流；``config`` 优先于 ``config_path``。"""

    raw = load_config(config_path) if config is None else copy.deepcopy(dict(config))
    _apply_env_overrides(raw)

    registry = build_model_registry(raw)
    prompts = build_prompt_library()
    arxiv_cfg = raw.get("tools", {}).get("arxiv", {})
    coordinator, research, point_extractor = build_agents(
        raw, registry, prompts, arxiv_cfg=arxiv_cfg
    )
    search_tool, full_text_tool, metadata_tool = build_tools(raw)

    workflow_cfg = raw.get("workflow", {})
    return NoveltyWorkflow(
        NoveltyWorkflowServices(
            coordinator=coordinator,
            research_agent=research,
            point_extractor=point_extractor,
            search_tool=search_tool,
            full_text_tool=full_text_tool,
            metadata_tool=metadata_tool,
        ),
        config=NoveltyWorkflowConfig(
            max_rounds=int(workflow_cfg.get("max_rounds", 2)),
            max_concurrency=int(workflow_cfg.get("max_concurrency", 4)),
            minimum_evidence_per_point=int(
                workflow_cfg.get("minimum_evidence_per_point", 1)
            ),
        ),
    )


def _apply_env_overrides(config: dict[str, Any]) -> None:
    """用 NOVELTY_<角色>_MODEL 覆盖 agents 里的模型别名。"""

    for role, agent_cfg in config.get("agents", {}).items():
        env_value = os.getenv(f"NOVELTY_{role.upper()}_MODEL")
        if env_value:
            agent_cfg["model"] = env_value
