"""论文查新 Web 应用配置。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class HarnessBudgetConfig:
    """Provider-neutral limits for one serial tool-calling run."""

    max_turns: int = 12
    max_total_tool_calls: int = 10
    per_tool_limits: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.max_turns < 1:
            raise ValueError("task_researcher.harness.max_turns must be positive")
        if self.max_total_tool_calls < 1:
            raise ValueError(
                "task_researcher.harness.max_total_tool_calls must be positive"
            )
        for name, limit in self.per_tool_limits.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError("per_tool_limits keys must be non-empty tool names")
            if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
                raise ValueError(f"per_tool_limits[{name!r}] must be positive")


@dataclass(frozen=True)
class ProgressProjectionConfig:
    """Feature settings reserved for harness progress projection."""

    enabled: bool = False


@dataclass(frozen=True)
class SkillRuntimeConfig:
    """Feature settings reserved for on-demand skill loading."""

    enabled: bool = False
    root: Path | None = None
    max_loaded: int | None = None

    def __post_init__(self) -> None:
        if self.max_loaded is not None and self.max_loaded < 1:
            raise ValueError("task_researcher.skills.max_loaded must be positive")


@dataclass(frozen=True)
class ResearcherRuntimeConfig:
    """Typed boundary between external settings and Researcher composition."""

    harness: HarnessBudgetConfig = field(default_factory=HarnessBudgetConfig)
    projection: ProgressProjectionConfig = field(
        default_factory=ProgressProjectionConfig
    )
    skills: SkillRuntimeConfig = field(default_factory=SkillRuntimeConfig)
    max_chars_per_read: int = 8_000
    max_total_read_chars: int = 48_000

    def __post_init__(self) -> None:
        if min(self.max_chars_per_read, self.max_total_read_chars) < 1:
            raise ValueError("researcher read budgets must be positive")

    @classmethod
    def from_mapping(
        cls, raw: Mapping[str, Any] | None = None
    ) -> "ResearcherRuntimeConfig":
        data = _mapping(raw, "task_researcher")
        harness_raw = _mapping(data.get("harness"), "task_researcher.harness")
        projection_raw = _mapping(
            data.get("projection"), "task_researcher.projection"
        )
        skills_raw = _mapping(data.get("skills"), "task_researcher.skills")

        # Flat keys are accepted as a migration bridge for existing user configs.
        max_turns = harness_raw.get("max_turns", data.get("max_steps", 12))
        max_total = harness_raw.get(
            "max_total_tool_calls", data.get("max_tool_calls", 10)
        )
        per_tool = harness_raw.get(
            "per_tool_limits", data.get("per_tool_limits", {})
        )
        if not isinstance(per_tool, Mapping):
            raise ValueError("task_researcher.harness.per_tool_limits must be an object")

        root = skills_raw.get("root")
        max_loaded = skills_raw.get("max_loaded")
        return cls(
            harness=HarnessBudgetConfig(
                max_turns=_positive_int(max_turns, "harness.max_turns"),
                max_total_tool_calls=_positive_int(
                    max_total, "harness.max_total_tool_calls"
                ),
                per_tool_limits=dict(per_tool),
            ),
            projection=ProgressProjectionConfig(
                enabled=_bool(projection_raw.get("enabled", False), "projection.enabled")
            ),
            skills=SkillRuntimeConfig(
                enabled=_bool(skills_raw.get("enabled", False), "skills.enabled"),
                root=Path(root) if root is not None else None,
                max_loaded=(
                    _positive_int(max_loaded, "skills.max_loaded")
                    if max_loaded is not None
                    else None
                ),
            ),
            max_chars_per_read=_positive_int(
                data.get("max_chars_per_read", 8_000), "max_chars_per_read"
            ),
            max_total_read_chars=_positive_int(
                data.get("max_total_read_chars", 48_000), "max_total_read_chars"
            ),
        )


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    return value


def _positive_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"task_researcher.{label} must be positive")
    return value


def _bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"task_researcher.{label} must be boolean")
    return value


@dataclass(frozen=True)
class NoveltyWebSettings:
    app_name: str = "论文查新 Multi-Agent"
    api_prefix: str = "/api/novelty"
    host: str = "0.0.0.0"
    port: int = 8010
    cors_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://localhost:5173",
    )

    @classmethod
    def from_env(cls) -> "NoveltyWebSettings":
        origins = os.getenv("NOVELTY_CORS_ORIGINS")
        return cls(
            host=os.getenv("NOVELTY_HOST", cls.host),
            port=int(os.getenv("NOVELTY_PORT", str(cls.port))),
            cors_origins=(
                tuple(item.strip() for item in origins.split(",") if item.strip())
                if origins
                else cls.cors_origins
            ),
        )
