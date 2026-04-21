from datetime import datetime
from enum import Enum
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


INATEL_EMAIL_PATTERN = re.compile(r"^[a-z]+(?:\.[a-z]+)+@(gec|ges|geb|gep)\.inatel\.br$")


class CourseCode(str, Enum):
    GES = "GES"
    GEC = "GEC"
    GEB = "GEB"
    GEP = "GEP"


class StudentBase(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        description="Nome completo do aluno.",
        examples=["Ana Clara Souza"],
    )
    email: EmailStr = Field(
        ...,
        description="E-mail institucional do aluno no formato `aluno.sobrenome@curso.inatel.br`.",
        examples=["ana.clara@ges.inatel.br"],
    )
    course: CourseCode = Field(
        ...,
        description="Curso do aluno. Valores aceitos: `GES`, `GEC`, `GEB` e `GEP`.",
        examples=["GES"],
    )
    active: bool = Field(
        default=True,
        description="Indica se a matrícula do aluno está ativa.",
        examples=[True],
    )

    @field_validator("email")
    @classmethod
    def validate_inatel_email_format(cls, value: EmailStr) -> EmailStr:
        normalized = value.lower()
        if not INATEL_EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError(
                "email must follow the format aluno.sobrenome@curso.inatel.br"
            )
        return normalized

    @model_validator(mode="after")
    def validate_email_matches_course(self) -> "StudentBase":
        email_course = self.email.split("@", maxsplit=1)[1].split(".", maxsplit=1)[0].upper()
        if email_course != self.course.value:
            raise ValueError("email domain course must match course field")
        return self


class StudentCreateRequest(StudentBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Ana Clara Souza",
                "email": "ana.clara@ges.inatel.br",
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
                "email": "ana.souza@gec.inatel.br",
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
        description="E-mail institucional do aluno no formato `aluno.sobrenome@curso.inatel.br`.",
        examples=["ana.souza@gec.inatel.br"],
    )
    course: CourseCode | None = Field(
        default=None,
        description="Curso do aluno. Valores aceitos: `GES`, `GEC`, `GEB` e `GEP`.",
        examples=["GEC"],
    )
    active: bool | None = Field(
        default=None,
        description="Indica se a matrícula do aluno está ativa.",
        examples=[False],
    )

    @field_validator("email")
    @classmethod
    def validate_optional_inatel_email_format(cls, value: EmailStr | None) -> EmailStr | None:
        if value is None:
            return None
        normalized = value.lower()
        if not INATEL_EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError(
                "email must follow the format aluno.sobrenome@curso.inatel.br"
            )
        return normalized

    @model_validator(mode="after")
    def validate_optional_email_matches_course(self) -> "StudentUpdateRequest":
        if self.email is None or self.course is None:
            return self
        email_course = self.email.split("@", maxsplit=1)[1].split(".", maxsplit=1)[0].upper()
        if email_course != self.course.value:
            raise ValueError("email domain course must match course field")
        return self


class StudentResponse(StudentBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "GES1",
                "name": "Ana Clara Souza",
                "email": "ana.clara@ges.inatel.br",
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
                        "email": "ana.clara@ges.inatel.br",
                        "course": "GES",
                        "matricula": 1,
                        "active": True,
                        "created_at": "2026-04-21T12:00:00Z",
                        "updated_at": "2026-04-21T12:00:00Z",
                    },
                    {
                        "id": "GEC1",
                        "name": "Bruno Lima",
                        "email": "bruno.lima@gec.inatel.br",
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
