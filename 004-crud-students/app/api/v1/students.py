from __future__ import annotations

import asyncpg
from fastapi import APIRouter, Body, Depends, Path, Response, status

from app.api.deps import get_conn
from app.schemas.student import (
    ErrorResponse,
    StudentCollectionResponse,
    StudentCreateRequest,
    StudentResponse,
    StudentUpdateRequest,
)
from app.services import students as students_service

router = APIRouter(prefix="/alunos")

STUDENT_ID_PATH = Path(
    ...,
    description="ID do aluno no formato `CURSO + matrícula`, como `GES1` ou `GEC2`.",
    examples=["GES1"],
)

NOT_FOUND_RESPONSE = {
    "model": ErrorResponse,
    "description": "Aluno não encontrado.",
    "content": {
        "application/json": {
            "example": {"detail": "aluno nao encontrado"},
        }
    },
}

CONFLICT_RESPONSE = {
    "model": ErrorResponse,
    "description": "Conflito de unicidade para `email`.",
    "content": {
        "application/json": {
            "examples": {
                "email_conflict": {"value": {"detail": "email ja cadastrado"}},
            }
        }
    },
}


@router.get(
    "",
    response_model=StudentCollectionResponse,
    summary="Listar alunos",
    description="Retorna todos os alunos persistidos no banco de dados PostgreSQL.",
    operation_id="listStudents",
)
async def list_students(
    conn: asyncpg.Connection = Depends(get_conn),
) -> StudentCollectionResponse:
    items = await students_service.list_students(conn)
    return StudentCollectionResponse(items=items)


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar aluno",
    description="Cria um novo aluno com matrícula automática e ID derivado do curso.",
    operation_id="createStudent",
    responses={
        201: {"description": "Aluno criado com sucesso."},
        409: CONFLICT_RESPONSE,
    },
)
async def create_student(
    payload: StudentCreateRequest = Body(
        ...,
        description="Dados do aluno a ser criado.",
    ),
    conn: asyncpg.Connection = Depends(get_conn),
) -> StudentResponse:
    row = await students_service.create_student(conn, **payload.model_dump())
    return StudentResponse.model_validate(row)


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Buscar aluno por ID",
    description="Retorna os dados do aluno informado.",
    operation_id="getStudent",
    responses={404: NOT_FOUND_RESPONSE},
)
async def get_student(
    student_id: str = STUDENT_ID_PATH,
    conn: asyncpg.Connection = Depends(get_conn),
) -> StudentResponse:
    row = await students_service.get_student(conn, student_id)
    return StudentResponse.model_validate(row)


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Atualizar aluno",
    description="Atualiza apenas os campos enviados para o aluno informado. Se o curso mudar, um novo ID é gerado sem reutilizar sequência anterior.",
    operation_id="updateStudent",
    responses={
        404: NOT_FOUND_RESPONSE,
        409: CONFLICT_RESPONSE,
    },
)
async def update_student(
    student_id: str = STUDENT_ID_PATH,
    payload: StudentUpdateRequest = Body(
        ...,
        description="Dados parciais do aluno a serem atualizados.",
    ),
    conn: asyncpg.Connection = Depends(get_conn),
) -> StudentResponse:
    row = await students_service.update_student(
        conn,
        student_id,
        **payload.model_dump(exclude_none=True),
    )
    return StudentResponse.model_validate(row)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover aluno",
    description="Remove um aluno do banco. Após a remoção, o ID deixa de ser válido.",
    operation_id="deleteStudent",
    responses={
        204: {"description": "Aluno removido com sucesso."},
        404: NOT_FOUND_RESPONSE,
    },
)
async def delete_student(
    student_id: str = STUDENT_ID_PATH,
    conn: asyncpg.Connection = Depends(get_conn),
) -> Response:
    await students_service.delete_student(conn, student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Resetar lista de alunos",
    description="Remove todos os alunos atualmente cadastrados, preservando a sequência de geração de IDs por curso.",
    operation_id="resetStudents",
    responses={
        204: {"description": "Lista de alunos resetada com sucesso."},
    },
)
async def reset_students(
    conn: asyncpg.Connection = Depends(get_conn),
) -> Response:
    await students_service.reset_students(conn)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
