from fastapi import APIRouter, Body, Path, Response, status

from app.schemas.student import (
    ErrorResponse,
    StudentCollectionResponse,
    StudentCreateRequest,
    StudentResponse,
    StudentUpdateRequest,
)
from app.services.students import student_service

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
    description="Retorna todos os alunos atualmente mantidos em memória pela API.",
    operation_id="listStudents",
)
async def list_students() -> StudentCollectionResponse:
    return StudentCollectionResponse(items=student_service.list_students())


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar aluno",
    description="Cria um novo aluno em memória com matrícula automática e ID derivado do curso.",
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
) -> StudentResponse:
    return StudentResponse.model_validate(student_service.create_student(**payload.model_dump()))


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Buscar aluno por ID",
    description="Retorna os dados do aluno informado.",
    operation_id="getStudent",
    responses={404: NOT_FOUND_RESPONSE},
)
async def get_student(student_id: str = STUDENT_ID_PATH) -> StudentResponse:
    return StudentResponse.model_validate(student_service.get_student(student_id))


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
) -> StudentResponse:
    return StudentResponse.model_validate(
        student_service.update_student(
            student_id,
            **payload.model_dump(exclude_none=True),
        )
    )


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover aluno",
    description="Remove um aluno da coleção em memória. Após a remoção, o ID deixa de ser válido.",
    operation_id="deleteStudent",
    responses={
        204: {"description": "Aluno removido com sucesso."},
        404: NOT_FOUND_RESPONSE,
    },
)
async def delete_student(student_id: str = STUDENT_ID_PATH) -> Response:
    student_service.delete_student(student_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Resetar lista de alunos",
    description="Remove todos os alunos atualmente carregados, preservando a sequência de geração de IDs por curso.",
    operation_id="resetStudents",
    responses={
        204: {"description": "Lista de alunos resetada com sucesso."},
    },
)
async def reset_students() -> Response:
    student_service.reset_students()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
