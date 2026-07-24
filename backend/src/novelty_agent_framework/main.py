"""论文查新 FastAPI 应用入口。"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import NoveltyWebSettings
from .routers import health_router, runs_router


def create_app(settings: NoveltyWebSettings | None = None) -> FastAPI:
    settings = settings or NoveltyWebSettings.from_env()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Evidence-grounded novelty research workflow API",
    )
    application.state.settings = settings
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health_router, prefix=settings.api_prefix)
    application.include_router(runs_router, prefix=settings.api_prefix)
    return application


app = create_app()


def run() -> None:
    import uvicorn

    settings = NoveltyWebSettings.from_env()
    uvicorn.run(
        "novelty_agent_framework.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )


if __name__ == "__main__":
    run()
