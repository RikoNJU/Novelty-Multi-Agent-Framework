"""Typed configuration contracts; no runtime construction belongs here."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ModelProfileConfig(ConfigModel):
    provider: str
    base_url: str
    model: str
    api_key_env: str | None = None
    context_window: int = Field(gt=0)
    supported_params: list[str] = Field(default_factory=list)


class ModelInvocationConfig(ConfigModel):
    alias: str = Field(min_length=1)
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(gt=0)
    timeout_seconds: float = Field(gt=0)
    tool_choice: str | None = None
    enable_thinking: bool | None = None
    thinking_budget: int | None = Field(default=None, gt=0)
    reasoning_effort: str | None = None


class HarnessConfig(ConfigModel):
    max_turns: int = Field(gt=0)
    max_total_tool_calls: int = Field(gt=0)
    per_tool_limits: dict[str, int]

    @model_validator(mode="after")
    def positive_limits(self):
        if not self.per_tool_limits or any(
            value < 1 for value in self.per_tool_limits.values()
        ):
            raise ValueError("per_tool_limits must contain positive limits")
        return self


class DatabaseSearchConfig(ConfigModel):
    active_source: str = Field(min_length=1)
    candidate_limit_per_task: int = Field(gt=0)
    candidate_excerpt_chars: int = Field(gt=0)
    full_text_limit_per_task: int = Field(ge=0)
    max_concurrency: int = Field(gt=0)
    providers: dict[str, dict[str, Any]]


class WebSearchConfig(ConfigModel):
    backend: Literal["baidu"]
    default_max_results: int = Field(gt=0)
    max_results_per_call: int = Field(gt=0)
    baidu: dict[str, Any]

    @model_validator(mode="after")
    def valid_result_limits(self):
        if self.default_max_results > self.max_results_per_call:
            raise ValueError(
                "default_max_results must not exceed max_results_per_call"
            )
        if self.max_results_per_call > 50:
            raise ValueError("max_results_per_call exceeds Baidu hard limit 50")
        return self


class BrowserConfig(ConfigModel):
    backend: Literal["playwright"]
    network_mode: Literal["inherit", "direct"] = "inherit"
    navigation_timeout_ms: int = Field(gt=0)
    max_html_chars: int = Field(gt=0)
    max_text_chars: int = Field(gt=0)


class ReaderConfig(ConfigModel):
    default_chars_per_read: int = Field(gt=0)
    max_chars_per_read: int = Field(gt=0)
    max_total_read_chars: int = Field(gt=0)

    @model_validator(mode="after")
    def valid_read_limits(self):
        if self.default_chars_per_read > self.max_chars_per_read:
            raise ValueError(
                "default_chars_per_read must not exceed max_chars_per_read"
            )
        if self.max_chars_per_read > 16_000:
            raise ValueError("max_chars_per_read exceeds ReaderArguments cap 16000")
        return self


class ResearcherToolsConfig(ConfigModel):
    database_search: DatabaseSearchConfig
    web_search: WebSearchConfig
    browser: BrowserConfig
    reader: ReaderConfig


class ResearcherConfig(ConfigModel):
    version: int = Field(ge=1)
    model: ModelInvocationConfig
    prompt: str = Field(min_length=1)
    harness: HarnessConfig
    tools: ResearcherToolsConfig


class SearchPlannerLimitsConfig(ConfigModel):
    """SearchPlanner 语义校验的数量预算（与 prompt 数字一致，配置可覆盖）。"""

    max_concepts: int = Field(default=6, gt=0)
    max_terms_per_concept: int = Field(default=5, gt=0)
    max_alias_per_concept: int = Field(default=4, ge=0)
    max_exclude_per_concept: int = Field(default=3, ge=0)
    max_term_words: int = Field(default=8, gt=0)
    require_escape: bool = False


class SearchPlannerConfig(ConfigModel):
    version: int = Field(ge=1)
    model: ModelInvocationConfig
    prompt: str = Field(min_length=1)
    max_attempts: int = Field(gt=0)
    limits: SearchPlannerLimitsConfig = Field(
        default_factory=SearchPlannerLimitsConfig
    )


class ReviewerConfig(ConfigModel):
    version: int = Field(ge=1)
    enabled: bool = False
    model: ModelInvocationConfig
    prompt: str = Field(min_length=1)
    max_cards_per_call: int = Field(gt=0)
    fail_closed: bool = True


class RoleAgentConfig(ConfigModel):
    version: int = Field(ge=1)
    model: ModelInvocationConfig
    prompts: list[str] = Field(min_length=1)


class ServerConfig(ConfigModel):
    host: str
    port: int = Field(ge=1, le=65535)


class CorsConfig(ConfigModel):
    origins: list[str]


class WorkflowConfig(ConfigModel):
    max_rounds: int = Field(gt=0)
    max_concurrency: int = Field(gt=0)
    minimum_evidence_per_point: int = Field(ge=0)


class ProjectSettingsConfig(ConfigModel):
    server: ServerConfig
    cors: CorsConfig
    workflow: WorkflowConfig
    processing: dict[str, Any]


class ApplicationConfig(ConfigModel):
    project: ProjectSettingsConfig
    models: dict[str, ModelProfileConfig]
    researcher: ResearcherConfig
    search_planner: SearchPlannerConfig
    reviewer: ReviewerConfig | None = None
    coordinator: RoleAgentConfig
    point_extractor: RoleAgentConfig

    @model_validator(mode="after")
    def known_model_aliases(self):
        aliases = set(self.models)
        roles = {
            "researcher": self.researcher.model.alias,
            "search_planner": self.search_planner.model.alias,
            "coordinator": self.coordinator.model.alias,
            "point_extractor": self.point_extractor.model.alias,
        }
        if self.reviewer is not None and self.reviewer.enabled:
            roles["reviewer"] = self.reviewer.model.alias
        unknown = {role: alias for role, alias in roles.items() if alias not in aliases}
        for key in ("ocr_model", "llm_model"):
            alias = self.project.processing.get(key)
            if alias and alias not in aliases:
                unknown[f"processing.{key}"] = alias
        if unknown:
            raise ValueError(f"unknown model aliases: {unknown}")
        return self
