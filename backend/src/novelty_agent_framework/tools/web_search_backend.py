"""Provider-neutral backend contract for Web resource discovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from math import isfinite
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class SearchHit:
    title: str
    url: str
    snippet: str | None = None
    score: float | None = None
    published_at: datetime | None = None
    source_name: str | None = None
    external_id: str | None = None
    raw_metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("search hit title cannot be empty")
        if not self.url.strip():
            raise ValueError("search hit url cannot be empty")
        _validate_json_value(self.raw_metadata, "raw_metadata")


@dataclass(frozen=True)
class SearchBackendResult:
    query: str
    hits: Sequence[SearchHit] = ()
    warnings: Sequence[str] = ()

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("search result query cannot be empty")


class SearchBackend(Protocol):
    name: str

    async def search(
        self,
        query: str,
        *,
        max_results: int,
    ) -> SearchBackendResult: ...


def _validate_json_value(value: Any, path: str) -> None:
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f"{path} contains non-finite float")
    if value is None or isinstance(value, (str, int, float, bool)):
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{path}[{index}]")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} keys must be strings")
            _validate_json_value(item, f"{path}.{key}")
        return
    raise ValueError(f"{path} contains non-JSON-compatible {type(value).__name__}")
