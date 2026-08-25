"""Provider-neutral contracts for acquiring a known Web page."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import Field

from ..schemas import StrictModel


class BrowserFetchResult(StrictModel):
    requested_url: str
    final_url: str
    title: str | None = None
    html: str
    text: str
    content_type: str | None = None
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserBackend(Protocol):
    name: str

    async def fetch(self, url: str) -> BrowserFetchResult: ...
