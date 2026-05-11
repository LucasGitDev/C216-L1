from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.db.pool import close_pool, init_pool
from app.middlewares import register_middlewares

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Endpoints de verificação básica da API.",
    },
    {
        "name": "alunos",
        "description": "Operações para listar, criar, consultar, atualizar, remover e resetar alunos persistidos no PostgreSQL.",
    },
]

API_DESCRIPTION = """
API para gerenciamento de alunos com persistência em PostgreSQL.

Use os endpoints de `alunos` para criar novos registros, consultar um aluno específico,
atualizar seus dados, removê-lo da coleção ou resetar a lista inteira.

Regras principais:
- os cursos aceitos são `GES`, `GEC`, `GEB` e `GEP`
- a matrícula é sequencial por curso e gerada automaticamente via SEQUENCE no banco
- o `id` é formado por `curso + matrícula`, como `GES1` e `GEC2`
- ids e matrículas não são reutilizados após exclusão
- o e-mail deve seguir o padrão `aluno.sobrenome@curso.inatel.br`
- `PATCH` atualiza apenas os campos enviados
""".strip()


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = get_settings()
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
        summary="CRUD de alunos via REST com persistência em PostgreSQL.",
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
