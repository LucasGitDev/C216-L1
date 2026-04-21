from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.middlewares import register_middlewares

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Endpoints de verificação básica da API.",
    },
    {
        "name": "alunos",
        "description": "Operações para listar, criar, consultar, atualizar, remover e resetar alunos em memória.",
    },
]

API_DESCRIPTION = """
API para gerenciamento de alunos em memória.

Use os endpoints de `alunos` para criar novos registros, consultar um aluno específico,
atualizar seus dados, removê-lo da coleção em memória ou resetar a lista inteira.

Regras principais:
- os cursos aceitos são `GES`, `GEC`, `GEB` e `GEP`
- a matrícula é sequencial por curso e gerada automaticamente
- o `id` é formado por `curso + matrícula`, como `GES1` e `GEC2`
- ids e matrículas não são reutilizados após exclusão
- o e-mail deve seguir o padrão `aluno.sobrenome@curso.inatel.br`
- `PATCH` atualiza apenas os campos enviados
""".strip()


def create_application() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        summary="CRUD de alunos em memória via REST.",
        description=API_DESCRIPTION,
        debug=settings.debug,
        version=settings.app_version,
        openapi_tags=OPENAPI_TAGS,
    )
    register_middlewares(application)
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_application()
