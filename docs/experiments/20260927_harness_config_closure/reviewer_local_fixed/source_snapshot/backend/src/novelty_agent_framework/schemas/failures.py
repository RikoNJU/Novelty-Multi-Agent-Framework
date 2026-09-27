"""Versioned business failures and bounded recovery advice, independent of agents.

Codes describe observed facts. Advice never grants tool/network permission and
never turns missing coverage into a negative scientific finding.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FailureCode(StrEnum):
    PROVIDER_AUTHENTICATION = "provider.authentication"
    PROVIDER_AUTHORIZATION = "provider.authorization"
    PROVIDER_RATE_LIMIT = "provider.rate_limit"
    PROVIDER_NETWORK = "provider.network"
    PROVIDER_SERVICE = "provider.service"
    PROVIDER_PROTOCOL = "provider.protocol"
    PROVIDER_RESOURCE_MISSING = "provider.resource_missing"
    PROVIDER_UNKNOWN = "provider.unknown"
    MATERIAL_UNAVAILABLE = "material.unavailable"
    MATERIAL_INTEGRITY = "material.integrity"
    TOOL_SCOPE = "tool.scope"
    TOOL_ARGUMENTS = "tool.arguments"
    TOOL_UNAVAILABLE = "tool.unavailable"
    MODEL_TIMEOUT = "model.timeout"
    MODEL_TRANSPORT = "model.transport"
    MODEL_CONTEXT_LIMIT = "model.context_limit"
    MODEL_CONTEXT_UNAVAILABLE = "model.context_unavailable"
    MODEL_OUTPUT_SCHEMA = "model.output_schema"
    MODEL_OUTPUT_REFERENCE = "model.output_reference"
    MODEL_USAGE_UNAVAILABLE = "model.usage_unavailable"
    BUDGET_EXHAUSTED = "harness.budget_exhausted"
    COVERAGE_NOT_EXECUTED = "coverage.not_executed"
    COVERAGE_NO_MATCH = "coverage.no_match"
    EVIDENCE_MISSING = "evidence.missing"
    REVIEW_MISSING_FEATURES = "review.missing_features"
    REVIEW_SUMMARY_FAILED = "review.summary_failed"
    UNKNOWN = "execution.unknown"


class RecoveryAction(StrEnum):
    RETRY_REQUEST = "retry_request"
    REPAIR_ARGUMENTS = "repair_arguments"
    REPAIR_OUTPUT = "repair_output"
    CHANGE_PROVIDER = "change_provider"
    FETCH_FULLTEXT = "fetch_fulltext"
    READ_ARTIFACT = "read_artifact"
    REPLAN_QUERY = "replan_query"
    RESEARCH_GAP = "research_gap"
    RESUME_REVIEW = "resume_review"
    RESTORE_CHECKPOINT = "restore_checkpoint"
    MANUAL = "manual"
    STOP = "stop"
    NONE = "none"


class FailureContract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, hide_input_in_errors=True)


class FailureScope(FailureContract):
    paper_id: str | None = None
    run_id: str | None = None
    point_id: str | None = None
    task_id: str | None = None
    attempt: int | None = Field(default=None, ge=1)
    card_id: str | None = None
    artifact_id: str | None = None
    provider: str | None = None
    feature_ids: list[str] = Field(default_factory=list)


class RetryAdvice(FailureContract):
    allowed: bool = False
    max_additional_attempts: int = Field(default=0, ge=0, le=2)
    requires_input_change: bool = False
    retry_after_seconds: float | None = Field(default=None, ge=0, le=3600)

    @model_validator(mode="after")
    def bounded(self):
        if self.allowed != (self.max_additional_attempts > 0):
            raise ValueError("retry allowance and additional attempt limit must agree")
        return self


@dataclass(frozen=True)
class FailureDefinition:
    layer: str
    category: str
    actions: tuple[RecoveryAction, ...]
    retry_limit: int = 0
    input_change: bool = False
    effect: str = "limits_coverage"


A = RecoveryAction
D = FailureDefinition
FAILURE_CATALOG = MappingProxyType({
    FailureCode.PROVIDER_AUTHENTICATION: D("provider", "authentication", (A.CHANGE_PROVIDER, A.MANUAL)),
    FailureCode.PROVIDER_AUTHORIZATION: D("provider", "authorization", (A.CHANGE_PROVIDER, A.MANUAL)),
    FailureCode.PROVIDER_RATE_LIMIT: D("provider", "rate_limit", (A.RETRY_REQUEST, A.CHANGE_PROVIDER, A.STOP), 1),
    FailureCode.PROVIDER_NETWORK: D("provider", "network", (A.RETRY_REQUEST, A.CHANGE_PROVIDER, A.STOP), 1),
    FailureCode.PROVIDER_SERVICE: D("provider", "service", (A.RETRY_REQUEST, A.CHANGE_PROVIDER, A.STOP), 1),
    FailureCode.PROVIDER_PROTOCOL: D("provider", "protocol", (A.CHANGE_PROVIDER, A.MANUAL)),
    FailureCode.PROVIDER_RESOURCE_MISSING: D("provider", "resource", (A.CHANGE_PROVIDER, A.MANUAL)),
    FailureCode.PROVIDER_UNKNOWN: D("provider", "unknown", (A.MANUAL, A.STOP)),
    FailureCode.MATERIAL_UNAVAILABLE: D("reader", "resource", (A.FETCH_FULLTEXT, A.MANUAL)),
    FailureCode.MATERIAL_INTEGRITY: D("reader", "integrity", (A.MANUAL, A.STOP), effect="blocks_card"),
    FailureCode.TOOL_SCOPE: D("harness", "policy", (A.REPAIR_ARGUMENTS, A.STOP), 1, True, "blocks_card"),
    FailureCode.TOOL_ARGUMENTS: D("harness", "arguments", (A.REPAIR_ARGUMENTS, A.STOP), 1, True),
    FailureCode.TOOL_UNAVAILABLE: D("harness", "policy", (A.MANUAL, A.STOP)),
    FailureCode.MODEL_TIMEOUT: D("model", "network", (A.RESTORE_CHECKPOINT, A.RETRY_REQUEST, A.STOP), 1, effect="blocks_point"),
    FailureCode.MODEL_TRANSPORT: D("model", "network", (A.RESTORE_CHECKPOINT, A.RETRY_REQUEST, A.STOP), 1, effect="blocks_point"),
    FailureCode.MODEL_CONTEXT_LIMIT: D("model", "context", (A.RESTORE_CHECKPOINT, A.STOP), effect="blocks_point"),
    FailureCode.MODEL_CONTEXT_UNAVAILABLE: D("model", "context", (A.MANUAL, A.STOP), effect="blocks_point"),
    FailureCode.MODEL_OUTPUT_SCHEMA: D("model", "contract", (A.REPAIR_OUTPUT, A.STOP), 1, True, "blocks_point"),
    FailureCode.MODEL_OUTPUT_REFERENCE: D("reviewer", "integrity", (A.REPAIR_OUTPUT, A.STOP), 1, True, "blocks_point"),
    FailureCode.MODEL_USAGE_UNAVAILABLE: D("runtime", "unknown", (A.NONE,), effect="accounting_unknown"),
    FailureCode.BUDGET_EXHAUSTED: D("harness", "budget", (A.STOP,), effect="blocks_point"),
    FailureCode.COVERAGE_NOT_EXECUTED: D("researcher", "coverage", (A.RESEARCH_GAP, A.STOP)),
    FailureCode.COVERAGE_NO_MATCH: D("provider", "coverage", (A.REPLAN_QUERY, A.STOP)),
    FailureCode.EVIDENCE_MISSING: D("researcher", "coverage", (A.RESEARCH_GAP, A.STOP)),
    FailureCode.REVIEW_MISSING_FEATURES: D("reviewer", "semantic", (A.READ_ARTIFACT, A.FETCH_FULLTEXT, A.RESEARCH_GAP, A.STOP), effect="blocks_point"),
    FailureCode.REVIEW_SUMMARY_FAILED: D("reviewer", "contract", (A.RESUME_REVIEW, A.STOP), 1, effect="blocks_point"),
    FailureCode.UNKNOWN: D("runtime", "unknown", (A.MANUAL, A.STOP), effect="unknown"),
})


class FailureEvent(FailureContract):
    schema_version: Literal[1] = 1
    event_id: str = Field(pattern=r"^failure_[0-9a-f]{24}$")
    code: FailureCode
    layer: str
    category: str
    scope: FailureScope
    execution_status: Literal["incomplete", "partial"] = "incomplete"
    semantic_status: Literal["not_adjudicated"] = "not_adjudicated"
    retry: RetryAdvice
    recovery: RecoveryAction
    conclusion_effect: Literal["limits_coverage", "blocks_card", "blocks_point", "blocks_run", "accounting_unknown", "unknown"]
    evidence_refs: list[str] = Field(default_factory=list)
    cause_event_ids: list[str] = Field(default_factory=list)
    message: str = ""

    @model_validator(mode="after")
    def catalog_consistent(self):
        definition = FAILURE_CATALOG[self.code]
        if (self.layer, self.category) != (definition.layer, definition.category):
            raise ValueError("failure classification must match the code catalog")
        if self.recovery not in definition.actions:
            raise ValueError("recovery action is not allowed for this failure code")
        if self.retry.max_additional_attempts > definition.retry_limit:
            raise ValueError("retry exceeds the code's bounded policy")
        if self.retry.allowed and definition.input_change and not self.retry.requires_input_change:
            raise ValueError("this recovery cannot repeat the same invalid input")
        if self.event_id in self.cause_event_ids or len(set(self.cause_event_ids)) != len(self.cause_event_ids):
            raise ValueError("failure causes cannot contain self or duplicate references")
        return self


def make_failure(code: FailureCode | str, *, scope: FailureScope | dict,
                 message: str = "", evidence_refs: list[str] | None = None,
                 cause_event_ids: list[str] | None = None, occurrence_id: str = "") -> FailureEvent:
    code = FailureCode(code)
    scope = FailureScope.model_validate(scope)
    definition = FAILURE_CATALOG[code]
    identity = json.dumps([code.value, scope.model_dump(mode="json"), occurrence_id], sort_keys=True, ensure_ascii=False)
    # Callers supply sanitized constant descriptions, never raw credential-bearing errors.
    return FailureEvent(event_id="failure_" + hashlib.sha256(identity.encode()).hexdigest()[:24],
        code=code, layer=definition.layer, category=definition.category, scope=scope,
        retry=RetryAdvice(allowed=definition.retry_limit > 0,
            max_additional_attempts=definition.retry_limit, requires_input_change=definition.input_change),
        recovery=definition.actions[0], conclusion_effect=definition.effect,
        message=message, evidence_refs=evidence_refs or [], cause_event_ids=cause_event_ids or [])


class RecoveryArtifact(FailureContract):
    namespace: Literal["research_reference", "subject_reference"] = "research_reference"
    artifact_id: str = Field(min_length=1)


class RecoveryDecision(FailureContract):
    """Runtime-owned next action, including an auditable decision to stop."""
    point_id: str = Field(min_length=1)
    action: RecoveryAction
    reason: str = Field(min_length=1)
    cause_event_ids: list[str] = Field(default_factory=list)
    source_id: str | None = None
    artifacts: list[RecoveryArtifact] = Field(default_factory=list)
    source_record_ids: list[str] = Field(default_factory=list)
    missing_feature_ids: list[str] = Field(default_factory=list)
    missing_aspects: list[str] = Field(default_factory=list)
    max_additional_attempts: int = Field(default=1, ge=0, le=1)

    @model_validator(mode="after")
    def bound_targets(self):
        if self.action == RecoveryAction.READ_ARTIFACT and not self.artifacts:
            raise ValueError("read recovery needs explicit Artifact handles")
        if self.action == RecoveryAction.FETCH_FULLTEXT and (not self.source_id or not self.source_record_ids):
            raise ValueError("acquisition recovery needs a Provider and bound record handles")
        if self.action in {RecoveryAction.CHANGE_PROVIDER, RecoveryAction.RETRY_REQUEST} and not self.source_id:
            raise ValueError("Provider recovery needs an explicit enabled source")
        if self.action in {RecoveryAction.STOP, RecoveryAction.NONE, RecoveryAction.MANUAL} and self.max_additional_attempts:
            raise ValueError("terminal recovery decisions cannot grant attempts")
        return self
