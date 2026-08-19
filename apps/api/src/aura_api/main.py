from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from aura_api.dependencies import get_execution_service, get_settings
from aura_api.routes import router
from aura_models.config import get_settings as load_settings


def create_app() -> FastAPI:
    settings = load_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AURA Browser Intelligence Platform – REST API (Week 3)",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    dashboard_dir = _dashboard_dir()
    if dashboard_dir.exists():
        app.mount("/assets", StaticFiles(directory=dashboard_dir), name="assets")

        @app.get("/", include_in_schema=False)
        async def dashboard() -> FileResponse:
            return FileResponse(dashboard_dir / "index.html")

    @app.on_event("shutdown")
    async def shutdown() -> None:
        service = get_execution_service()
        await service.shutdown()

    return app


def _dashboard_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "dashboard"


app = create_app()
