"""FastAPI application main entry point."""

from contextlib import asynccontextmanager
import joblib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal, close_db, init_db
from app.core.paths import REPO_ROOT
from app.core.seed import seed_demo_data
from app.core.workbook_import import import_defects_from_workbook
from app.models import Defect
from sqlalchemy import select


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    async with AsyncSessionLocal() as session:
        workbook_path = REPO_ROOT / "Defects_Data_21May.xlsx"
        import_result = await import_defects_from_workbook(session, workbook_path, replace_existing=True)
        await seed_demo_data(session)
        if import_result.get("rows_imported", 0) > 0:
            defect_result = await session.execute(select(Defect).where(Defect.is_deleted.is_(False)))
            defects = [
                {
                    "id": str(defect.id),
                    "title": defect.title,
                    "description": defect.description,
                    "priority": defect.priority,
                    "status": defect.status,
                    "category": defect.category,
                    "assigned_to": defect.assigned_to,
                    "opened_at": defect.opened_at,
                    "resolved_at": defect.resolved_at,
                    "reopen_count": defect.reopen_count,
                    "is_sla_breached": defect.is_sla_breached,
                }
                for defect in defect_result.scalars().all()
            ]
            from app.nlp.embeddings_service import EmbeddingsService

            EmbeddingsService._metadata = defects
            joblib.dump(defects, EmbeddingsService.METADATA_PATH)
    yield
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url=settings.OPENAPI_URL,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": settings.APP_VERSION}

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": settings.APP_NAME}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)