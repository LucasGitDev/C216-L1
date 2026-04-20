from fastapi import APIRouter, Body, Path, Response, status

from app.schemas.microwave import (
    ErrorResponse,
    MicrowaveCollectionResponse,
    MicrowaveCreateRequest,
    MicrowaveStartRequest,
    MicrowaveStateResponse,
)
from app.services.microwaves import microwave_service

router = APIRouter(prefix="/microwaves")

MICROWAVE_ID_PATH = Path(
    ...,
    description="ID numérico do micro-ondas que será consultado ou controlado.",
    examples=[1],
)

NOT_FOUND_RESPONSE = {
    "model": ErrorResponse,
    "description": "Micro-ondas não encontrado.",
    "content": {
        "application/json": {
            "example": {"detail": "microwave not found"},
        }
    },
}

RUNNING_CONFLICT_RESPONSE = {
    "model": ErrorResponse,
    "description": "Ação rejeitada porque o micro-ondas já está em execução.",
    "content": {
        "application/json": {
            "example": {"detail": "microwave is already running"},
        }
    },
}

STOPPED_CONFLICT_RESPONSE = {
    "model": ErrorResponse,
    "description": "Ação rejeitada porque o micro-ondas já está parado.",
    "content": {
        "application/json": {
            "example": {"detail": "microwave is already stopped"},
        }
    },
}

VALIDATION_ERROR_RESPONSE = {
    "description": "Dados inválidos para a operação solicitada.",
    "content": {
        "application/json": {
            "examples": {
                "content_empty": {
                    "summary": "Conteúdo vazio",
                    "value": {
                        "detail": [
                            {
                                "type": "value_error",
                                "loc": ["body", "content"],
                                "msg": "Value error, content must not be empty",
                                "input": "   ",
                            }
                        ]
                    },
                },
                "power_out_of_range": {
                    "summary": "Potência fora da faixa",
                    "value": {
                        "detail": [
                            {
                                "type": "less_than_equal",
                                "loc": ["body", "power"],
                                "msg": "Input should be less than or equal to 10",
                                "input": 11,
                                "ctx": {"le": 10},
                            }
                        ]
                    },
                },
            }
        }
    },
}


@router.get(
    "",
    response_model=MicrowaveCollectionResponse,
    summary="Listar micro-ondas",
    description="Retorna todas as instâncias de micro-ondas atualmente mantidas em memória pela API.",
    operation_id="listMicrowaves",
)
async def list_microwaves() -> MicrowaveCollectionResponse:
    return MicrowaveCollectionResponse(items=microwave_service.list_microwaves())


@router.post(
    "",
    response_model=MicrowaveStateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar micro-ondas",
    description="Cria uma nova instância de micro-ondas em memória já disponível para consulta e controle.",
    operation_id="createMicrowave",
    responses={
        201: {
            "description": "Micro-ondas criado com sucesso.",
        },
        422: VALIDATION_ERROR_RESPONSE,
    },
)
async def create_microwave(
    payload: MicrowaveCreateRequest = Body(
        ...,
        description="Dados iniciais do micro-ondas a ser criado.",
    )
) -> MicrowaveStateResponse:
    return MicrowaveStateResponse.model_validate(
        microwave_service.create_microwave(power=payload.power, content=payload.content)
    )


@router.get(
    "/{microwave_id}",
    response_model=MicrowaveStateResponse,
    summary="Consultar estado do micro-ondas",
    description="Retorna o estado atual de uma instância específica, incluindo tempo restante e status derivado.",
    operation_id="getMicrowave",
    responses={
        404: NOT_FOUND_RESPONSE,
    },
)
async def get_microwave(
    microwave_id: int = MICROWAVE_ID_PATH,
) -> MicrowaveStateResponse:
    return MicrowaveStateResponse.model_validate(microwave_service.get_microwave(microwave_id))


@router.delete(
    "/{microwave_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover micro-ondas",
    description="Remove uma instância de micro-ondas criada na API. Após a remoção, o ID deixa de ser válido.",
    operation_id="deleteMicrowave",
    responses={
        204: {"description": "Micro-ondas removido com sucesso."},
        404: NOT_FOUND_RESPONSE,
    },
)
async def delete_microwave(
    microwave_id: int = MICROWAVE_ID_PATH,
) -> Response:
    microwave_service.delete_microwave(microwave_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{microwave_id}/start",
    response_model=MicrowaveStateResponse,
    summary="Iniciar aquecimento",
    description="Inicia um ciclo de aquecimento para o micro-ondas informado. Exige conteúdo não vazio e rejeita a operação se o aparelho já estiver em execução.",
    operation_id="startMicrowave",
    responses={
        200: {"description": "Aquecimento iniciado com sucesso."},
        404: NOT_FOUND_RESPONSE,
        409: RUNNING_CONFLICT_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
async def start_microwave(
    microwave_id: int = MICROWAVE_ID_PATH,
    payload: MicrowaveStartRequest = Body(
        ...,
        description="Parâmetros do ciclo de aquecimento a ser iniciado.",
    ),
) -> MicrowaveStateResponse:
    return MicrowaveStateResponse.model_validate(
        microwave_service.start_microwave(
            microwave_id,
            duration_seconds=payload.duration_seconds,
            content=payload.content,
            power=payload.power,
        )
    )


@router.post(
    "/{microwave_id}/stop",
    response_model=MicrowaveStateResponse,
    summary="Parar aquecimento",
    description="Interrompe o ciclo atual de aquecimento. Mantém o conteúdo e a potência configurada no micro-ondas.",
    operation_id="stopMicrowave",
    responses={
        200: {"description": "Aquecimento interrompido com sucesso."},
        404: NOT_FOUND_RESPONSE,
        409: STOPPED_CONFLICT_RESPONSE,
    },
)
async def stop_microwave(
    microwave_id: int = MICROWAVE_ID_PATH,
) -> MicrowaveStateResponse:
    return MicrowaveStateResponse.model_validate(
        microwave_service.stop_microwave(microwave_id)
    )


@router.post(
    "/{microwave_id}/reset",
    response_model=MicrowaveStateResponse,
    summary="Resetar micro-ondas",
    description="Restaura o estado padrão do micro-ondas: desligado, sem temporizador, potência padrão e sem conteúdo.",
    operation_id="resetMicrowave",
    responses={
        200: {"description": "Micro-ondas resetado com sucesso."},
        404: NOT_FOUND_RESPONSE,
    },
)
async def reset_microwave(
    microwave_id: int = MICROWAVE_ID_PATH,
) -> MicrowaveStateResponse:
    return MicrowaveStateResponse.model_validate(
        microwave_service.reset_microwave(microwave_id)
    )
