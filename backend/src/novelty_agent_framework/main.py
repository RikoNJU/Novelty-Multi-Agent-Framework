"""论文查新 FastAPI 应用入口。"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .web.store import RunStore
from .web.routes import router as pdf_router
from .web.middleware import UploadLimitMiddleware
from fastapi.middleware.cors import CORSMiddleware

from .config import NoveltyWebSettings
from .routers import health_router, runs_router


def create_app(settings: NoveltyWebSettings | None = None, *, runs_root: Path | None = None, runner=None, static_root: Path | None = None) -> FastAPI:
    settings = settings or NoveltyWebSettings.from_env()
    @asynccontextmanager
    async def lifespan(app):
        kwargs = {'executor': runner} if runner is not None else {}
        app.state.pdf_runs = RunStore(runs_root or Path(os.getenv('NOVELTY_WEB_RUNS', 'outputs/web-runs')), **kwargs)
        try:
            yield
        finally:
            from starlette.concurrency import run_in_threadpool
            await run_in_threadpool(app.state.pdf_runs.close)

    application = FastAPI(
        lifespan=lifespan,
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
    application.include_router(pdf_router)
    application.add_middleware(UploadLimitMiddleware)

    @application.middleware('http')
    async def cache_policy(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        elif request.url.path in ('/', '/index.html', '/sw.js'):
            response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    static_root = static_root or Path(os.getenv('NOVELTY_FRONTEND_DIST', 'frontend/dist'))
    if static_root.is_dir():
        application.mount('/', StaticFiles(directory=static_root, html=True), name='frontend')
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
