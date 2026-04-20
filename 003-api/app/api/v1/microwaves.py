from fastapi import APIRouter, Response, status

from app.schemas.microwave import (
    MicrowaveCollectionResponse,
    MicrowaveCreateRequest,
    MicrowaveStartRequest,
    MicrowaveStateResponse,
)
from app.services.microwaves import microwave_service

router = APIRouter(prefix="/microwaves")


@router.get("", response_model=MicrowaveCollectionResponse, summary="List microwaves")
async def list_microwaves() -> MicrowaveCollectionResponse:
    return MicrowaveCollectionResponse(items=microwave_service.list_microwaves())


@router.post(
    "",
    response_model=MicrowaveStateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create microwave",
)
async def create_microwave(payload: MicrowaveCreateRequest) -> MicrowaveStateResponse:
    return MicrowaveStateResponse.model_validate(
        microwave_service.create_microwave(power=payload.power, content=payload.content)
    )


@router.get(
    "/{microwave_id}",
    response_model=MicrowaveStateResponse,
    summary="Get microwave state",
)
async def get_microwave(microwave_id: int) -> MicrowaveStateResponse:
    return MicrowaveStateResponse.model_validate(microwave_service.get_microwave(microwave_id))


@router.delete(
    "/{microwave_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete microwave",
)
async def delete_microwave(microwave_id: int) -> Response:
    microwave_service.delete_microwave(microwave_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{microwave_id}/start",
    response_model=MicrowaveStateResponse,
    summary="Start microwave",
)
async def start_microwave(
    microwave_id: int, payload: MicrowaveStartRequest
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
    summary="Stop microwave",
)
async def stop_microwave(microwave_id: int) -> MicrowaveStateResponse:
    return MicrowaveStateResponse.model_validate(
        microwave_service.stop_microwave(microwave_id)
    )


@router.post(
    "/{microwave_id}/reset",
    response_model=MicrowaveStateResponse,
    summary="Reset microwave",
)
async def reset_microwave(microwave_id: int) -> MicrowaveStateResponse:
    return MicrowaveStateResponse.model_validate(
        microwave_service.reset_microwave(microwave_id)
    )
