from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Verificar saúde da API",
    description="Endpoint simples para confirmar que a aplicação está respondendo normalmente.",
    operation_id="healthCheck",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
