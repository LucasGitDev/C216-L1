from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProfessorBase(BaseModel):
    nome: str = Field(
        ...,
        min_length=3,
        description="Nome completo do professor.",
        examples=["Lucas Teles"],
    )
    email: EmailStr = Field(
        ...,
        description="E-mail institucional do professor.",
        examples=["lucas.teles@inatel.br"],
    )
    sala_de_atendimento: str = Field(
        ...,
        min_length=1,
        description="Identificação da sala de atendimento.",
        examples=["Sala 101"],
    )


class ProfessorCreateRequest(ProfessorBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Lucas Teles",
                "email": "lucas.teles@inatel.br",
                "sala_de_atendimento": "Sala 101",
            }
        }
    )


class ProfessorUpdateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "Lucas T.",
                "email": "lucas.t@inatel.br",
                "sala_de_atendimento": "Sala 202",
            }
        }
    )

    nome: str | None = Field(default=None, min_length=3)
    email: EmailStr | None = Field(default=None)
    sala_de_atendimento: str | None = Field(default=None, min_length=1)


class ProfessorResponse(ProfessorBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nome": "Lucas Teles",
                "email": "lucas.teles@inatel.br",
                "sala_de_atendimento": "Sala 101",
                "created_at": "2026-05-22T12:00:00Z",
                "updated_at": "2026-05-22T12:00:00Z",
            }
        },
    )

    id: int = Field(description="Identificador serial do professor.")
    created_at: datetime
    updated_at: datetime


class ProfessorCollectionResponse(BaseModel):
    items: list[ProfessorResponse]


class ErrorResponse(BaseModel):
    detail: str
