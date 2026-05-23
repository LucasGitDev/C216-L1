from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.db.pool import close_pool, init_pool
from app.middlewares import register_middlewares

OPENAPI_TAGS = [
    {"name": "health", "description": "Endpoints de verificação básica da API."},
    {
        "name": "professores",
        "description": "Operações CRUD sobre professores persistidos no PostgreSQL.",
    },
]

API_DESCRIPTION = """
API para gerenciamento de professores com persistência em PostgreSQL.

Endpoints disponíveis em `/api/v1/professores` para criar, listar, consultar, atualizar,
remover e resetar professores. `PATCH` atualiza apenas os campos enviados.
""".strip()


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("APP_DATABASE_URL is required")
    await init_pool(
        settings.database_url,
        min_size=settings.db_pool_min_size,
        max_size=settings.db_pool_max_size,
    )
    try:
        yield
    finally:
        await close_pool()


def create_application(*, use_lifespan: bool = True) -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        summary="CRUD de professores via REST com persistência em PostgreSQL.",
        description=API_DESCRIPTION,
        debug=settings.debug,
        version=settings.app_version,
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan if use_lifespan else None,
    )
    register_middlewares(application)
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_application()
