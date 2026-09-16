"""论文查新 FastAPI 应用入口。"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import NoveltyWebSettings
from .routers import health_router, runs_router
from .services import (
    NoveltyWorkflowService,
    build_demo_workflow_service,
    build_real_workflow_service,
)

logger = logging.getLogger(__name__)


def create_app(
    settings: NoveltyWebSettings | None = None,
    *,
    service: NoveltyWorkflowService | None = None,
) -> FastAPI:
    settings = settings or NoveltyWebSettings.from_env()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Evidence-grounded novelty research workflow API",
    )
    application.state.settings = settings
    application.state.workflow_service = service
    application.state.workflow_error = None
    if service is None:
        try:
            application.state.workflow_service = (
                build_real_workflow_service(settings)
                if settings.workflow_mode == "real"
                else build_demo_workflow_service(settings)
            )
        except Exception as exc:  # noqa: BLE001 - keep app available for health checks
            application.state.workflow_error = type(exc).__name__
            logger.error("workflow initialization failed: %s", type(exc).__name__)
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
