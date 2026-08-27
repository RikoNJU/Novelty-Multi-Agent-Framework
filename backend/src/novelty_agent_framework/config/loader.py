"""Read, combine, and validate the split configuration files."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from .schemas import ApplicationConfig

CONFIG_DIR = Path(__file__).resolve().parent
DEFAULT_PROJECT_PATH = CONFIG_DIR / "settings.example.json"
DEFAULT_MODELS_PATH = CONFIG_DIR / "models.example.json"
DEFAULT_RESEARCHER_PATH = CONFIG_DIR / "agents" / "researcher.example.json"
# Keep the manually-created filename as the path baseline for this task.
DEFAULT_SEARCH_PLANNER_PATH = CONFIG_DIR / "agents" / "search_panner.example.json"
DEFAULT_COORDINATOR_PATH = CONFIG_DIR / "agents" / "coordinator.example.json"
DEFAULT_POINT_EXTRACTOR_PATH = CONFIG_DIR / "agents" / "point_extractor.example.json"


def read_json(path: str | Path) -> dict[str, Any]:
    resolved = Path(path)
    with resolved.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"configuration {resolved} must contain a JSON object")
    return payload


def load_application_config(
    *,
    project_path: str | Path = DEFAULT_PROJECT_PATH,
    models_path: str | Path = DEFAULT_MODELS_PATH,
    researcher_path: str | Path = DEFAULT_RESEARCHER_PATH,
    search_planner_path: str | Path = DEFAULT_SEARCH_PLANNER_PATH,
    coordinator_path: str | Path = DEFAULT_COORDINATOR_PATH,
    point_extractor_path: str | Path = DEFAULT_POINT_EXTRACTOR_PATH,
    environ: Mapping[str, str] | None = None,
) -> ApplicationConfig:
    raw = {
        "project": read_json(project_path),
        "models": read_json(models_path),
        "researcher": read_json(researcher_path),
        "search_planner": read_json(search_planner_path),
        "coordinator": read_json(coordinator_path),
        "point_extractor": read_json(point_extractor_path),
    }
    _apply_model_overrides(raw, environ or os.environ)
    return ApplicationConfig.model_validate(raw)


def _apply_model_overrides(raw: dict[str, Any], environ: Mapping[str, str]) -> None:
    mapping = {
        "researcher": ("NOVELTY_RESEARCHER_MODEL", "NOVELTY_RESEARCH_MODEL"),
        "search_planner": ("NOVELTY_SEARCH_PLANNER_MODEL",),
        "coordinator": ("NOVELTY_COORDINATOR_MODEL",),
        "point_extractor": ("NOVELTY_POINT_EXTRACTOR_MODEL",),
    }
    for role, names in mapping.items():
        value = next((environ[name] for name in names if environ.get(name)), None)
        if value:
            raw[role]["model"]["alias"] = value


def legacy_shape(config: ApplicationConfig) -> dict[str, Any]:
    """Compatibility-only projection for callers not yet migrated to typed config."""

    db = config.researcher.tools.database_search
    return {
        **config.project.model_dump(mode="python"),
        "models": {alias: item.model_dump(mode="python") for alias, item in config.models.items()},
        "agents": {
            "research": {"model": config.researcher.model.alias, "temperature": config.researcher.model.temperature},
            "search_planner": {"model": config.search_planner.model.alias, "temperature": config.search_planner.model.temperature},
            "coordinator": {"model": config.coordinator.model.alias, "temperature": config.coordinator.model.temperature},
            "point_extractor": {"model": config.point_extractor.model.alias, "temperature": config.point_extractor.model.temperature},
        },
        "task_researcher": {
            "max_steps": config.researcher.harness.max_turns,
            "max_tool_calls": config.researcher.harness.max_total_tool_calls,
            "max_chars_per_read": config.researcher.tools.reader.max_chars_per_read,
            "max_total_read_chars": config.researcher.tools.reader.max_total_read_chars,
            "per_tool_limits": config.researcher.harness.per_tool_limits,
        },
        "retrieval": {
            "active_source": db.active_source,
            "candidate_limit_per_task": db.candidate_limit_per_task,
            "candidate_excerpt_chars": db.candidate_excerpt_chars,
            "full_text_limit_per_task": db.full_text_limit_per_task,
            "sources": db.providers,
        },
    }
