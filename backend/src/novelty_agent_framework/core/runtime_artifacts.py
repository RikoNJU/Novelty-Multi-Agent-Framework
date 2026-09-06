"""Incremental, local runtime-debug artifacts owned by the Harness layer.

The recorder is deliberately observational: it persists facts at run, stage and
tool boundaries, but does not attempt root-cause diagnosis or replay.
"""

from __future__ import annotations

import contextvars
import dataclasses
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import tempfile
import threading
import time
import traceback as traceback_module
import uuid
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover - the application depends on pydantic
    BaseModel = ()  # type: ignore[assignment,misc]


RUN_STATUSES = {"RUNNING", "SUCCESS", "FAILED", "INTERRUPTED"}
_REDACTED = "***REDACTED***"
_SENSITIVE_KEYS = {
    "apikey",
    "token",
    "accesstoken",
    "refreshtoken",
    "bearertoken",
    "secret",
    "clientsecret",
    "password",
    "authorization",
    "cookie",
    "setcookie",
}
_SENSITIVE_TEXT = re.compile(
    r"(?i)\b(api[_-]?key|token|secret|password|authorization|cookie)"
    r"\s*[:=]\s*([^\s,;]+)"
)

_current_run: contextvars.ContextVar[RuntimeArtifactManager | None] = (
    contextvars.ContextVar("novelty_runtime_artifact_manager", default=None)
)
_current_stage: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "novelty_runtime_stage", default=None
)


@dataclasses.dataclass(frozen=True)
class RuntimeDebugConfig:
    """Runtime-debug storage settings. Debug recording is on by default."""

    enabled: bool = True
    output_root: Path = Path("outputs")
    archive_root: Path = Path("docs/experiments/runtime")
    max_inline_bytes: int = 256_000

    def __post_init__(self) -> None:
        if self.max_inline_bytes < 1:
            raise ValueError("max_inline_bytes must be positive")


@dataclasses.dataclass(frozen=True)
class StageHandle:
    stage_id: str
    stage_name: str
    directory: Path | None
    started_at: datetime
    monotonic_started: float
    context_token: contextvars.Token[str | None] | None = None


@dataclasses.dataclass(frozen=True)
class ToolCallHandle:
    tool_call_id: str
    tool_name: str
    stage_name: str | None
    path: Path | None
    started_at: datetime
    monotonic_started: float
    agent_tool_call_id: str | None = None


class RuntimeArtifactManager:
    """Own one run's paths, identifiers, redaction and incremental writes."""

    def __init__(
        self,
        paper_id: str,
        *,
        config: RuntimeDebugConfig | None = None,
        run_id: str | None = None,
        runtime_config: Mapping[str, Any] | None = None,
        model_provider: str | None = None,
        model_name: str | None = None,
        enabled_tools: list[str] | tuple[str, ...] = (),
        stage_names: list[str] | tuple[str, ...] = (),
    ) -> None:
        self.config = config or RuntimeDebugConfig()
        self.paper_id = paper_id
        self.run_id = run_id or _new_run_id()
        self.runtime_config = dict(runtime_config or {})
        self.model_provider = model_provider
        self.model_name = model_name
        self.enabled_tools = list(enabled_tools)
        self.stage_names = list(dict.fromkeys(stage_names))
        self.started_at = _now()
        self._monotonic_started = time.monotonic()
        self._lock = threading.RLock()
        self._stage_counter = 0
        self._tool_counter = 0
        self._error_counter = 0
        self._stage_records: list[dict[str, Any]] = []
        self._tool_records: list[dict[str, Any]] = []
        self._error_records: list[dict[str, Any]] = []
        self._activation_token: contextvars.Token[RuntimeArtifactManager | None] | None = None
        self.run_dir: Path | None = None
        if self.config.enabled:
            safe_paper_id = _safe_segment(paper_id)
            self.run_dir = (
                Path(self.config.output_root)
                / safe_paper_id
                / "runtime"
                / _safe_segment(self.run_id)
            )
            for child in ("stages", "tools", "errors"):
                (self.run_dir / child).mkdir(parents=True, exist_ok=False)
            self._write_manifest("RUNNING")

    def __enter__(self) -> RuntimeArtifactManager:
        self.activate()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.deactivate()

    def activate(self) -> None:
        if self._activation_token is not None:
            raise RuntimeError("runtime artifact manager is already active")
        self._activation_token = _current_run.set(self)

    def deactivate(self) -> None:
        if self._activation_token is not None:
            _current_run.reset(self._activation_token)
            self._activation_token = None

    def start_stage(self, stage_name: str, stage_input: Any) -> StageHandle:
        started = _now()
        token = _current_stage.set(stage_name)
        if not self.config.enabled:
            return StageHandle(
                "", stage_name, None, started, time.monotonic(), token
            )
        with self._lock:
            self._stage_counter += 1
            stage_id = f"stage_{self._stage_counter:04d}"
            directory = self.run_dir / "stages" / (
                f"{self._stage_counter:04d}_{_safe_segment(stage_name)}"
            )
            directory.mkdir(parents=False, exist_ok=False)
            debug_details = _stage_debug_details(
                stage_name,
                stage_input=stage_input,
                stage_output=None,
                runtime_config=self.runtime_config,
            )
            record = {
                "stage_id": stage_id,
                "stage_name": stage_name,
                "status": "RUNNING",
                "started_at": _iso(started),
                "finished_at": None,
                "duration": None,
                "duration_ms": None,
                "error": None,
                "validation_result": None,
                "directory": directory,
            }
            if debug_details is not None:
                record["debug_details"] = debug_details
                record["_stage_input"] = stage_input
            self._stage_records.append(record)
            self._write_json(directory / "input.json", stage_input)
            self._write_json(directory / "meta.json", _public_record(record))
            return StageHandle(
                stage_id, stage_name, directory, started, time.monotonic(), token
            )

    def finish_stage(self, handle: StageHandle, stage_output: Any) -> None:
        if handle.context_token is not None:
            _current_stage.reset(handle.context_token)
        if not self.config.enabled or handle.directory is None:
            return
        finished = _now()
        validation_result = _stage_validation_result(
            handle.stage_name, stage_output
        )
        with self._lock:
            record = self._find_record(self._stage_records, "stage_id", handle.stage_id)
            stage_input = record.pop("_stage_input", None)
            debug_details = _stage_debug_details(
                handle.stage_name,
                stage_input=stage_input,
                stage_output=stage_output,
                runtime_config=self.runtime_config,
            )
            record.update(
                status="SUCCESS",
                finished_at=_iso(finished),
                duration=_elapsed_seconds(handle.monotonic_started),
                duration_ms=_elapsed_ms(handle.monotonic_started),
                validation_result=validation_result,
            )
            if debug_details is not None:
                record["debug_details"] = debug_details
            self._write_json(handle.directory / "output.json", stage_output)
            self._write_json(handle.directory / "meta.json", _public_record(record))

    def fail_stage(self, handle: StageHandle, exc: BaseException) -> None:
        if handle.context_token is not None:
            _current_stage.reset(handle.context_token)
        if not self.config.enabled or handle.directory is None:
            return
        finished = _now()
        error = self._error_payload(exc, stage=handle.stage_name)
        with self._lock:
            record = self._find_record(self._stage_records, "stage_id", handle.stage_id)
            record.pop("_stage_input", None)
            record.update(
                status="FAILED",
                finished_at=_iso(finished),
                duration=_elapsed_seconds(handle.monotonic_started),
                duration_ms=_elapsed_ms(handle.monotonic_started),
                error=error,
            )
            self._write_json(handle.directory / "meta.json", _public_record(record))
            self._persist_error(error)

    def start_tool_call(
        self,
        tool_name: str,
        *,
        agent_arguments: Any,
        resolved_arguments: Any,
        agent_tool_call_id: str | None = None,
        stage_name: str | None = None,
    ) -> ToolCallHandle:
        started = _now()
        stage = stage_name if stage_name is not None else _current_stage.get()
        if not self.config.enabled:
            return ToolCallHandle(
                "", tool_name, stage, None, started, time.monotonic(), agent_tool_call_id
            )
        with self._lock:
            self._tool_counter += 1
            tool_call_id = f"tool_{self._tool_counter:04d}"
            path = self.run_dir / "tools" / (
                f"{self._tool_counter:04d}_{_safe_segment(tool_name)}.json"
            )
            record = {
                "tool_name": tool_name,
                "tool_call_id": tool_call_id,
                "agent_tool_call_id": agent_tool_call_id,
                "stage_name": stage,
                "started_at": _iso(started),
                "finished_at": None,
                "duration": None,
                "duration_ms": None,
                "execution_status": "RUNNING",
                "failure_phase": None,
                "business_status": None,
                "result_count": None,
                "agent_arguments": agent_arguments,
                "resolved_arguments": resolved_arguments,
                "raw_result": None,
                "normalized_result": None,
                "error": None,
                "path": path,
            }
            self._tool_records.append(record)
            self._write_json(path, _public_record(record))
            return ToolCallHandle(
                tool_call_id,
                tool_name,
                stage,
                path,
                started,
                time.monotonic(),
                agent_tool_call_id,
            )

    def finish_tool_call(
        self,
        handle: ToolCallHandle,
        *,
        raw_result: Any,
        normalized_result: Any,
        succeeded: bool = True,
        error: BaseException | str | Mapping[str, Any] | None = None,
        result_count: int | None = None,
        business_status: str | None = None,
        failure_phase: str | None = None,
    ) -> None:
        if not self.config.enabled or handle.path is None:
            return
        with self._lock:
            record = self._find_record(
                self._tool_records, "tool_call_id", handle.tool_call_id
            )
            error_payload = self._coerce_error(
                error, stage=handle.stage_name, tool_call_id=handle.tool_call_id
            )
            if result_count is None:
                result_count = _infer_result_count(normalized_result)
            if business_status is None:
                business_status = "EMPTY" if succeeded and result_count == 0 else "NORMAL"
            record.update(
                finished_at=_iso(_now()),
                duration=_elapsed_seconds(handle.monotonic_started),
                duration_ms=_elapsed_ms(handle.monotonic_started),
                execution_status="SUCCESS" if succeeded else "FAILED",
                failure_phase=(
                    None
                    if succeeded
                    else failure_phase
                    or ("NORMALIZATION" if raw_result is not None and normalized_result is None
                        else "TOOL_EXECUTION")
                ),
                business_status=business_status,
                result_count=result_count,
                raw_result=raw_result,
                normalized_result=normalized_result,
                error=error_payload,
            )
            self._write_json(handle.path, _public_record(record))
            if error_payload is not None:
                self._persist_error(error_payload)

    def fail_tool_call(
        self,
        handle: ToolCallHandle,
        exc: BaseException,
        *,
        raw_result: Any = None,
        normalized_result: Any = None,
        failure_phase: str | None = None,
    ) -> None:
        self.finish_tool_call(
            handle,
            raw_result=raw_result,
            normalized_result=normalized_result,
            succeeded=False,
            error=exc,
            business_status="INVALID" if raw_result is not None else "NORMAL",
            failure_phase=failure_phase,
        )

    def finish_run(
        self,
        status: str,
        *,
        error: BaseException | None = None,
    ) -> tuple[Path | None, Path | None]:
        if status not in RUN_STATUSES - {"RUNNING"}:
            raise ValueError(f"invalid terminal run status {status!r}")
        if not self.config.enabled:
            return None, None
        with self._lock:
            if error is not None:
                self._persist_error(self._error_payload(error, stage=_current_stage.get()))
            finished = _now()
            self._write_manifest(status, end_time=finished)
            self._write_not_run_stages()
            summary = _prepare_value(
                self._build_summary(status, finished),
                max_inline_bytes=self.config.max_inline_bytes,
            )
            summary_json = self.run_dir / "summary.json"
            summary_md = self.run_dir / "summary.md"
            self._write_json(summary_json, summary)
            _atomic_write_text(summary_md, _render_summary(summary))
            archive = (
                Path(self.config.archive_root)
                / f"{_safe_segment(self.paper_id)}_{finished.date().isoformat()}"
                / _safe_segment(self.run_id)
            )
            archive.mkdir(parents=True, exist_ok=False)
            shutil.copy2(summary_json, archive / "summary.json")
            shutil.copy2(summary_md, archive / "summary.md")
            return summary_json, archive

    def _write_not_run_stages(self) -> None:
        executed_names = {item["stage_name"] for item in self._stage_records}
        for stage_name in self.stage_names:
            if stage_name in executed_names:
                continue
            directory = self.run_dir / "stages" / f"not_run_{_safe_segment(stage_name)}"
            directory.mkdir(parents=False, exist_ok=True)
            self._write_json(
                directory / "meta.json",
                {
                    "stage_id": None,
                    "stage_name": stage_name,
                    "status": "NOT_RUN",
                    "started_at": None,
                    "finished_at": None,
                    "duration": None,
                    "duration_ms": None,
                    "error": None,
                    "validation_result": None,
                },
            )

    def _write_manifest(self, status: str, end_time: datetime | None = None) -> None:
        if status not in RUN_STATUSES:
            raise ValueError(f"invalid run status {status!r}")
        branch, commit = _git_identity()
        manifest = {
            "run_id": self.run_id,
            "paper_id": self.paper_id,
            "status": status,
            "start_time": _iso(self.started_at),
            "end_time": _iso(end_time) if end_time else None,
            "duration_ms": (
                _elapsed_ms(self._monotonic_started) if end_time else None
            ),
            "git_branch": branch,
            "git_commit": commit,
            "python_version": platform.python_version(),
            "os": platform.platform(),
            "runtime_debug_enabled": self.config.enabled,
            "model_provider": self.model_provider,
            "model_name": self.model_name,
            "enabled_tools": self.enabled_tools,
            "runtime_config": self.runtime_config,
        }
        self._write_json(self.run_dir / "manifest.json", manifest)

    def _build_summary(self, status: str, finished: datetime) -> dict[str, Any]:
        executed_names = {item["stage_name"] for item in self._stage_records}
        stages = [_public_record(item) for item in self._stage_records]
        stages.extend(
            {
                "stage_id": None,
                "stage_name": name,
                "status": "NOT_RUN",
                "started_at": None,
                "finished_at": None,
                "duration_ms": None,
                "duration": None,
                "error": None,
            }
            for name in self.stage_names
            if name not in executed_names
        )
        tool_stats: dict[str, dict[str, Any]] = {}
        for record in self._tool_records:
            stats = tool_stats.setdefault(
                record["tool_name"],
                {"tool_name": record["tool_name"], "calls": 0, "success": 0,
                 "failed": 0, "empty": 0},
            )
            stats["calls"] += 1
            if record["execution_status"] == "SUCCESS":
                stats["success"] += 1
            elif record["execution_status"] == "FAILED":
                stats["failed"] += 1
            if record["business_status"] == "EMPTY":
                stats["empty"] += 1
        completed = [item for item in self._stage_records if item["status"] == "SUCCESS"]
        integrity_gates = [
            {
                "stage_name": item["stage_name"],
                **item["validation_result"],
            }
            for item in self._stage_records
            if item.get("validation_result") is not None
        ]
        final_evidence_sufficiency_checks = []
        for index, item in enumerate(self._stage_records):
            details = item.get("debug_details")
            if not isinstance(details, Mapping) or not details.get(
                "final_evidence_sufficiency"
            ):
                continue
            next_stage = (
                self._stage_records[index + 1]["stage_name"]
                if index + 1 < len(self._stage_records)
                else None
            )
            final_evidence_sufficiency_checks.append(
                {
                    "stage_id": item["stage_id"],
                    "stage_status": item["status"],
                    **details["final_evidence_sufficiency"],
                    "actual_next_stage": next_stage,
                }
            )
        return {
            "run": {
                "paper_id": self.paper_id,
                "run_id": self.run_id,
                "status": status,
                "start_time": _iso(self.started_at),
                "end_time": _iso(finished),
                "duration_ms": _elapsed_ms(self._monotonic_started),
            },
            "environment": {
                "git_branch": _git_identity()[0],
                "git_commit": _git_identity()[1],
                "model_provider": self.model_provider,
                "model_name": self.model_name,
                "python_version": platform.python_version(),
            },
            "stages": stages,
            "tool_calls": list(tool_stats.values()),
            "errors": list(self._error_records),
            "integrity_gates": integrity_gates,
            "final_evidence_sufficiency_checks": (
                final_evidence_sufficiency_checks
            ),
            "last_completed_stage": completed[-1]["stage_name"] if completed else None,
        }

    def _coerce_error(
        self,
        error: BaseException | str | Mapping[str, Any] | None,
        *,
        stage: str | None,
        tool_call_id: str | None,
    ) -> dict[str, Any] | None:
        if error is None:
            return None
        if isinstance(error, BaseException):
            return self._error_payload(error, stage=stage, tool_call_id=tool_call_id)
        if isinstance(error, Mapping):
            payload = dict(error)
            payload.setdefault("type", "RuntimeError")
            payload.setdefault("message", "")
            payload.setdefault("traceback", "")
            payload.setdefault("stage", stage)
            payload.setdefault("tool_call_id", tool_call_id)
            payload.setdefault("timestamp", _iso(_now()))
            return payload
        error_type, separator, message = error.partition(":")
        if not separator or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", error_type):
            error_type, message = "ToolExecutionError", error
        return {
            "type": error_type,
            "message": message.strip(),
            "traceback": "".join(traceback_module.format_stack()),
            "stage": stage,
            "tool_call_id": tool_call_id,
            "timestamp": _iso(_now()),
        }

    def _error_payload(
        self,
        exc: BaseException,
        *,
        stage: str | None,
        tool_call_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": "".join(
                traceback_module.format_exception(type(exc), exc, exc.__traceback__)
            ),
            "stage": stage,
            "tool_call_id": tool_call_id,
            "timestamp": _iso(_now()),
        }

    def _persist_error(self, error: Mapping[str, Any]) -> None:
        self._error_counter += 1
        payload = dict(error)
        payload["error_id"] = f"error_{self._error_counter:04d}"
        self._error_records.append(payload)
        path = self.run_dir / "errors" / f"{self._error_counter:04d}.json"
        self._write_json(path, payload)

    def _write_json(self, path: Path, value: Any) -> None:
        serializable = _prepare_value(value, max_inline_bytes=self.config.max_inline_bytes)
        _atomic_write_text(
            path, json.dumps(serializable, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )

    @staticmethod
    def _find_record(records: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
        for record in records:
            if record[key] == value:
                return record
        raise KeyError(value)


def current_runtime_artifacts() -> RuntimeArtifactManager | None:
    """Return the active run recorder, if runtime debugging is enabled."""

    manager = _current_run.get()
    return manager if manager is not None and manager.config.enabled else None


def _new_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"run-{stamp}-{uuid.uuid4().hex[:10]}"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _elapsed_ms(started: float) -> int:
    return max(0, int((time.monotonic() - started) * 1000))


def _elapsed_seconds(started: float) -> float:
    return round(max(0.0, time.monotonic() - started), 6)


def _safe_segment(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._")
    if not safe or safe in {".", ".."}:
        raise ValueError("runtime artifact path identifier is empty or unsafe")
    return safe[:160]


def _public_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.items()
        if key not in {"path", "directory"} and not key.startswith("_")
    }


def _prepare_value(value: Any, *, max_inline_bytes: int, key: str | None = None) -> Any:
    if key is not None and _is_sensitive_key(key):
        return _REDACTED
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    elif dataclasses.is_dataclass(value) and not isinstance(value, type):
        value = dataclasses.asdict(value)
    if isinstance(value, Mapping):
        return {
            str(item_key): _prepare_value(
                item_value, max_inline_bytes=max_inline_bytes, key=str(item_key)
            )
            for item_key, item_value in value.items()
        }
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_prepare_value(item, max_inline_bytes=max_inline_bytes) for item in value]
    if isinstance(value, Path):
        return _path_reference(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return _prepare_value(value.value, max_inline_bytes=max_inline_bytes)
    if isinstance(value, bytes):
        return {
            "type": "content_reference",
            "size": len(value),
            "sha256": hashlib.sha256(value).hexdigest(),
            "summary": "binary content omitted from runtime artifact",
        }
    if isinstance(value, str):
        redacted = _SENSITIVE_TEXT.sub(lambda match: f"{match.group(1)}={_REDACTED}", value)
        encoded = redacted.encode("utf-8")
        if len(encoded) > max_inline_bytes:
            return {
                "type": "content_reference",
                "size": len(encoded),
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "summary": f"large text omitted ({len(encoded)} bytes)",
            }
        return redacted
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _prepare_value(repr(value), max_inline_bytes=max_inline_bytes)


def _is_sensitive_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    return normalized in _SENSITIVE_KEYS or normalized.endswith(
        ("apikey", "token", "secret", "password", "authorization", "cookie")
    )


def _path_reference(path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {"type": "artifact_reference", "path": str(path)}
    try:
        stat = path.stat()
        payload["size"] = stat.st_size
        if path.is_file():
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            payload["sha256"] = digest.hexdigest()
    except OSError as exc:
        payload["summary"] = f"path metadata unavailable: {type(exc).__name__}"
    return payload


def _infer_result_count(value: Any) -> int | None:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="python")
    if isinstance(value, (list, tuple, set, frozenset)):
        return len(value)
    if isinstance(value, Mapping):
        for key in ("results", "items", "hits", "evidence_cards", "artifacts"):
            candidate = value.get(key)
            if isinstance(candidate, (list, tuple)):
                return len(candidate)
        for candidate in value.values():
            inferred = _infer_result_count(candidate)
            if inferred is not None:
                return inferred
    return None


def _stage_debug_details(
    stage_name: str,
    *,
    stage_input: Any,
    stage_output: Any,
    runtime_config: Mapping[str, Any],
) -> dict[str, Any] | None:
    if stage_name != "check_final_evidence_sufficiency":
        return None
    state = _as_mapping(stage_input)
    if state is None:
        return None
    brief = _as_mapping(state.get("brief")) or {}
    point_values = brief.get("novelty_points", state.get("novelty_points", []))
    point_ids = [
        point_id
        for point in _as_sequence(point_values)
        if (point_id := _field_value(point, "point_id")) is not None
    ]
    counts = {point_id: 0 for point_id in point_ids}
    ignored_card_count = 0
    cards = _as_sequence(state.get("evidence_cards", []))
    for card in cards:
        point_id = _field_value(card, "novelty_point_id")
        if point_id in counts:
            counts[point_id] += 1
        else:
            ignored_card_count += 1

    workflow_config = _workflow_runtime_config(runtime_config)
    configured_cut = workflow_config.get("min_final_evidence_cards_per_point")
    if not isinstance(configured_cut, int) or isinstance(configured_cut, bool):
        configured_cut = _required_count_from_output(stage_output)
    if configured_cut is None:
        return None

    point_results = [
        {
            "novelty_point_id": point_id,
            "valid_card_count": counts[point_id],
            "required_card_count": configured_cut,
            "status": "PASS" if counts[point_id] >= configured_cut else "INSUFFICIENT",
        }
        for point_id in point_ids
    ]
    calculated_insufficient = [
        item["novelty_point_id"]
        for item in point_results
        if item["status"] == "INSUFFICIENT"
    ]
    calculated_insufficient_facts = [
        {
            "novelty_point_id": item["novelty_point_id"],
            "valid_card_count": item["valid_card_count"],
            "required_card_count": item["required_card_count"],
            "reason": "insufficient_final_evidence",
        }
        for item in point_results
        if item["status"] == "INSUFFICIENT"
    ]
    reported = _reported_insufficient_points(stage_output)
    rounds = state.get("rounds")
    max_rounds = workflow_config.get("max_rounds")
    round_limit_allows_supplement = (
        bool(reported)
        and isinstance(rounds, int)
        and isinstance(max_rounds, int)
        and rounds < max_rounds
    )
    return {
        "final_evidence_sufficiency": {
            "configured_cut": configured_cut,
            "round": rounds,
            "max_rounds": max_rounds,
            "input_final_valid_card_count": len(cards),
            "counted_final_valid_card_count": sum(counts.values()),
            "ignored_card_count": ignored_card_count,
            "calculated_status": (
                "INSUFFICIENT" if calculated_insufficient else "PASS"
            ),
            "check_status": (
                ("INSUFFICIENT" if reported else "PASS")
                if reported is not None
                else None
            ),
            "point_results": point_results,
            "calculated_insufficient_point_ids": calculated_insufficient,
            "calculated_insufficient_final_evidence_points": (
                calculated_insufficient_facts
            ),
            "reported_insufficient_final_evidence_points": reported,
            "output_matches_calculation": (
                reported == calculated_insufficient_facts
                if reported is not None
                else None
            ),
            "round_limit_allows_supplement": round_limit_allows_supplement,
        }
    }


def _as_mapping(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="python")
    elif dataclasses.is_dataclass(value) and not isinstance(value, type):
        value = dataclasses.asdict(value)
    return value if isinstance(value, Mapping) else None


def _as_sequence(value: Any) -> list[Any] | tuple[Any, ...]:
    return value if isinstance(value, (list, tuple)) else []


def _field_value(value: Any, field: str) -> str | None:
    mapping = _as_mapping(value)
    candidate = (
        mapping.get(field) if mapping is not None else getattr(value, field, None)
    )
    return candidate if isinstance(candidate, str) and candidate else None


def _workflow_runtime_config(runtime_config: Mapping[str, Any]) -> Mapping[str, Any]:
    workflow = runtime_config.get("workflow")
    if isinstance(workflow, Mapping):
        return workflow
    project = runtime_config.get("project")
    if isinstance(project, Mapping):
        workflow = project.get("workflow")
        if isinstance(workflow, Mapping):
            return workflow
    return {}


def _reported_insufficient_points(stage_output: Any) -> list[dict[str, Any]] | None:
    output = _as_mapping(stage_output)
    if output is None or "insufficient_final_evidence_points" not in output:
        return None
    reported = []
    for item in _as_sequence(output["insufficient_final_evidence_points"]):
        mapping = _as_mapping(item)
        if mapping is not None:
            reported.append(dict(mapping))
    return reported


def _required_count_from_output(stage_output: Any) -> int | None:
    reported = _reported_insufficient_points(stage_output)
    if not reported:
        return None
    value = reported[0].get("required_card_count")
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _stage_validation_result(stage_name: str, output: Any) -> dict[str, Any] | None:
    if not isinstance(output, Mapping):
        return None
    key = {
        "validate_synthesis_input": "synthesis_integrity",
        "validate_report_integrity": "report_integrity",
    }.get(stage_name)
    value = output.get(key) if key is not None else None
    return dict(value) if isinstance(value, Mapping) else None


def _git_identity() -> tuple[str | None, str | None]:
    def run(*args: str) -> str | None:
        try:
            completed = subprocess.run(
                ["git", *args], capture_output=True, text=True, timeout=2, check=False
            )
        except (OSError, subprocess.SubprocessError):
            return None
        value = completed.stdout.strip()
        return value if completed.returncode == 0 and value else None

    return run("branch", "--show-current"), run("rev-parse", "HEAD")


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.",
            suffix=".tmp", delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _render_summary(summary: Mapping[str, Any]) -> str:
    run = summary["run"]
    environment = summary["environment"]
    lines = [
        "# Runtime Summary", "", "## Run", "",
        f"Paper ID: {run['paper_id']}", f"Run ID: {run['run_id']}",
        f"Status: {run['status']}", f"Start: {run['start_time']}",
        f"End: {run['end_time']}", f"Duration: {run['duration_ms']} ms", "",
        "## Environment", "", f"Git Branch: {environment['git_branch']}",
        f"Git Commit: {environment['git_commit']}",
        f"Model: {environment['model_provider']} / {environment['model_name']}",
        f"Python: {environment['python_version']}", "", "## Stage Status", "",
        "| Stage | Status | Duration |", "|---|---|---:|",
    ]
    lines.extend(
        f"| {item['stage_name']} | {item['status']} | "
        f"{item.get('duration_ms') if item.get('duration_ms') is not None else '-'} ms |"
        for item in summary["stages"]
    )
    lines.extend(["", "## Tool Calls", "", "| Tool | Calls | Success | Failed | Empty |",
                  "|---|---:|---:|---:|---:|"])
    lines.extend(
        f"| {item['tool_name']} | {item['calls']} | {item['success']} | "
        f"{item['failed']} | {item['empty']} |"
        for item in summary["tool_calls"]
    )
    lines.extend(["", "## Final Evidence Sufficiency Checks", ""])
    checks = summary.get("final_evidence_sufficiency_checks", [])
    if checks:
        for check in checks:
            lines.extend(
                [
                    f"### Round {check.get('round')}",
                    "",
                    f"Configured cut: {check.get('configured_cut')}",
                    f"Stage status: {check.get('stage_status')}",
                    f"Check status: {check.get('check_status')}",
                    f"Input final valid Cards: {check.get('input_final_valid_card_count')}",
                    f"Ignored Cards: {check.get('ignored_card_count')}",
                    f"Output matches calculation: {check.get('output_matches_calculation')}",
                    "Round limit allows supplement: "
                    f"{check.get('round_limit_allows_supplement')}",
                    f"Actual next stage: {check.get('actual_next_stage')}",
                    "",
                    "| Novelty Point | Valid Cards | Required Cards | Status |",
                    "|---|---:|---:|---|",
                ]
            )
            lines.extend(
                f"| {item['novelty_point_id']} | {item['valid_card_count']} | "
                f"{item['required_card_count']} | {item['status']} |"
                for item in check.get("point_results", [])
            )
            lines.append("")
    else:
        lines.append("- None")
    lines.extend(["", "## Errors", ""])
    if summary["errors"]:
        lines.extend(
            f"- {item.get('stage') or '-'} / {item.get('tool_call_id') or '-'}: "
            f"{item.get('type')}: {item.get('message')}"
            for item in summary["errors"]
        )
    else:
        lines.append("- None")
    lines.extend(["", "## Integrity Gates", ""])
    if summary.get("integrity_gates"):
        lines.extend(
            f"- {item['stage_name']}: "
            f"{'PASS' if item.get('validation_passed') else 'FAILED'}"
            for item in summary["integrity_gates"]
        )
        for item in summary["integrity_gates"]:
            for issue in item.get("issues", []):
                lines.append(f"  - {issue}")
            for rejected in item.get("rejected_cards", []):
                for reason in rejected.get("reasons", []):
                    lines.append(f"  - {rejected.get('card_id')}: {reason}")
    else:
        lines.append("- None")
    lines.extend(["", "## Last Completed Stage", "",
                  str(summary["last_completed_stage"] or "None"), ""])
    return "\n".join(lines)


__all__ = [
    "RuntimeArtifactManager",
    "RuntimeDebugConfig",
    "StageHandle",
    "ToolCallHandle",
    "current_runtime_artifacts",
]
