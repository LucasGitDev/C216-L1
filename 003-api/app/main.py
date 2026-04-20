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
        "name": "microwaves",
        "description": "Operações para listar, criar e controlar micro-ondas em memória.",
    },
]

API_DESCRIPTION = """
API para gerenciamento de múltiplos micro-ondas em memória.

Use os endpoints de `microwaves` para criar novas instâncias, consultar o estado atual,
iniciar um aquecimento com duração em segundos, interromper o ciclo atual ou resetar
o aparelho para o estado padrão.

Regras principais:
- a API inicia com 2 micro-ondas pré-carregados
- `start` exige `content` não vazio
- `power` deve ficar entre 1 e 10
- `stop` só funciona quando o micro-ondas está em execução
- `reset` desliga o aparelho, zera o temporizador e limpa o conteúdo
""".strip()


def create_application() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        summary="Controle de micro-ondas em memória via REST.",
        description=API_DESCRIPTION,
        debug=settings.debug,
        version=settings.app_version,
        openapi_tags=OPENAPI_TAGS,
    )
    register_middlewares(application)
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_application()
