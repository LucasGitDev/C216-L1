from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CourseCode(str, Enum):
    GES = "GES"
    GEC = "GEC"


class StudentBase(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        description="Nome completo do aluno.",
        examples=["Ana Clara Souza"],
    )
    email: EmailStr = Field(
        ...,
        description="E-mail principal do aluno. Deve ser único.",
        examples=["ana.clara@example.com"],
    )
    course: CourseCode = Field(
        ...,
        description="Curso do aluno. Valores aceitos: `GES` e `GEC`.",
        examples=["GES"],
    )
    active: bool = Field(
        default=True,
        description="Indica se a matrícula do aluno está ativa.",
        examples=[True],
    )


class StudentCreateRequest(StudentBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Ana Clara Souza",
                "email": "ana.clara@example.com",
                "course": "GES",
                "active": True,
            }
        }
    )


class StudentUpdateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Ana Souza",
                "email": "ana.souza@example.com",
                "course": "GEC",
                "active": False,
            }
        }
    )

    name: str | None = Field(
        default=None,
        min_length=3,
        description="Nome completo do aluno.",
        examples=["Ana Souza"],
    )
    email: EmailStr | None = Field(
        default=None,
        description="E-mail principal do aluno. Deve ser único.",
        examples=["ana.souza@example.com"],
    )
    course: CourseCode | None = Field(
        default=None,
        description="Curso do aluno. Valores aceitos: `GES` e `GEC`.",
        examples=["GEC"],
    )
    active: bool | None = Field(
        default=None,
        description="Indica se a matrícula do aluno está ativa.",
        examples=[False],
    )


class StudentResponse(StudentBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "GES1",
                "name": "Ana Clara Souza",
                "email": "ana.clara@example.com",
                "course": "GES",
                "matricula": 1,
                "active": True,
                "created_at": "2026-04-21T12:00:00Z",
                "updated_at": "2026-04-21T12:00:00Z",
            }
        },
    )

    id: str = Field(
        description="Identificador único do aluno no formato `CURSO + matrícula`, como `GES1`.",
        examples=["GES1"],
    )
    matricula: int = Field(
        description="Número sequencial da matrícula dentro do curso do aluno.",
        examples=[1],
    )
    created_at: datetime = Field(
        description="Data e hora de criação do registro do aluno.",
        examples=["2026-04-21T12:00:00Z"],
    )
    updated_at: datetime = Field(
        description="Data e hora da última atualização do registro do aluno.",
        examples=["2026-04-21T12:00:00Z"],
    )


class StudentCollectionResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "GES1",
                        "name": "Ana Clara Souza",
                        "email": "ana.clara@example.com",
                        "course": "GES",
                        "matricula": 1,
                        "active": True,
                        "created_at": "2026-04-21T12:00:00Z",
                        "updated_at": "2026-04-21T12:00:00Z",
                    },
                    {
                        "id": "GEC1",
                        "name": "Bruno Lima",
                        "email": "bruno.lima@example.com",
                        "course": "GEC",
                        "matricula": 1,
                        "active": True,
                        "created_at": "2026-04-21T12:00:00Z",
                        "updated_at": "2026-04-21T12:00:00Z",
                    },
                ]
            }
        }
    )

    items: list[StudentResponse] = Field(
        description="Lista de alunos disponíveis no processo da API."
    )


class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "aluno nao encontrado"}}
    )

    detail: str = Field(
        description="Mensagem resumida que descreve o erro retornado pela API.",
        examples=["aluno nao encontrado"],
    )
