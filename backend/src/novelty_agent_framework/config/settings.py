"""论文查新 Web 应用配置。"""

from __future__ import annotations

import os
from dataclasses import dataclass


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
