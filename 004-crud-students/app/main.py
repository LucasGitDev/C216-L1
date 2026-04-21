from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.middlewares import register_middlewares

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Endpoints de verificação básica da API.",
    },
]

API_DESCRIPTION = """
API base para exercícios com FastAPI.

O projeto começa com um endpoint de healthcheck e infraestrutura pronta para expansão
com rotas versionadas, middlewares, testes automatizados e execução com Docker.
""".strip()


def create_application() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        summary="Boilerplate FastAPI para exercícios REST.",
        description=API_DESCRIPTION,
        debug=settings.debug,
        version=settings.app_version,
        openapi_tags=OPENAPI_TAGS,
    )
    register_middlewares(application)
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_application()
