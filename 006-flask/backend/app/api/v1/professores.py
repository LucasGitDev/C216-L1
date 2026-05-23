from __future__ import annotations

import asyncpg
from fastapi import APIRouter, Body, Depends, Path, Response, status

from app.api.deps import get_conn
from app.schemas.professor import (
    ErrorResponse,
    ProfessorCollectionResponse,
    ProfessorCreateRequest,
    ProfessorResponse,
    ProfessorUpdateRequest,
)
from app.services import professores as professores_service

router = APIRouter(prefix="/professores")

PROFESSOR_ID_PATH = Path(..., description="ID serial do professor.", examples=[1])

NOT_FOUND_RESPONSE = {
    "model": ErrorResponse,
    "description": "Professor não encontrado.",
    "content": {"application/json": {"example": {"detail": "professor nao encontrado"}}},
}

CONFLICT_RESPONSE = {
    "model": ErrorResponse,
    "description": "Conflito de unicidade para `email`.",
    "content": {"application/json": {"example": {"detail": "email ja cadastrado"}}},
}


@router.get(
    "",
    response_model=ProfessorCollectionResponse,
    summary="Listar professores",
    operation_id="listProfessores",
)
async def list_professores(
    conn: asyncpg.Connection = Depends(get_conn),
) -> ProfessorCollectionResponse:
    items = await professores_service.list_professores(conn)
    return ProfessorCollectionResponse(items=items)


@router.post(
    "",
    response_model=ProfessorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar professor",
    operation_id="createProfessor",
    responses={201: {"description": "Professor criado com sucesso."}, 409: CONFLICT_RESPONSE},
)
async def create_professor(
    payload: ProfessorCreateRequest = Body(..., description="Dados do professor."),
    conn: asyncpg.Connection = Depends(get_conn),
) -> ProfessorResponse:
    row = await professores_service.create_professor(conn, **payload.model_dump())
    return ProfessorResponse.model_validate(row)


@router.get(
    "/{professor_id}",
    response_model=ProfessorResponse,
    summary="Buscar professor por ID",
    operation_id="getProfessor",
    responses={404: NOT_FOUND_RESPONSE},
)
async def get_professor(
    professor_id: int = PROFESSOR_ID_PATH,
    conn: asyncpg.Connection = Depends(get_conn),
) -> ProfessorResponse:
    row = await professores_service.get_professor(conn, professor_id)
    return ProfessorResponse.model_validate(row)


@router.patch(
    "/{professor_id}",
    response_model=ProfessorResponse,
    summary="Atualizar professor",
    operation_id="updateProfessor",
    responses={404: NOT_FOUND_RESPONSE, 409: CONFLICT_RESPONSE},
)
async def update_professor(
    professor_id: int = PROFESSOR_ID_PATH,
    payload: ProfessorUpdateRequest = Body(..., description="Dados parciais do professor."),
    conn: asyncpg.Connection = Depends(get_conn),
) -> ProfessorResponse:
    row = await professores_service.update_professor(
        conn, professor_id, **payload.model_dump(exclude_none=True)
    )
    return ProfessorResponse.model_validate(row)


@router.delete(
    "/{professor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover professor",
    operation_id="deleteProfessor",
    responses={204: {"description": "Professor removido."}, 404: NOT_FOUND_RESPONSE},
)
async def delete_professor(
    professor_id: int = PROFESSOR_ID_PATH,
    conn: asyncpg.Connection = Depends(get_conn),
) -> Response:
    await professores_service.delete_professor(conn, professor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Resetar lista de professores",
    operation_id="resetProfessores",
    responses={204: {"description": "Lista resetada."}},
)
async def reset_professores(
    conn: asyncpg.Connection = Depends(get_conn),
) -> Response:
    await professores_service.reset_professores(conn)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
