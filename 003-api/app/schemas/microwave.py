from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MicrowaveCreateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "power": 5,
                "content": "prato vazio para aquecer depois",
            }
        }
    )

    power: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Potência inicial do micro-ondas criado. Deve ficar entre 1 e 10.",
        examples=[5],
    )
    content: str = Field(
        default="",
        description="Conteúdo atualmente dentro do micro-ondas. Pode começar vazio.",
        examples=["prato vazio para aquecer depois"],
    )


class MicrowaveStartRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "duration_seconds": 30,
                "power": 7,
                "content": "pizza",
            }
        }
    )

    duration_seconds: int = Field(
        ...,
        gt=0,
        le=3600,
        description="Duração do aquecimento em segundos. Valor máximo: 3600.",
        examples=[30],
    )
    power: int | None = Field(
        default=None,
        ge=1,
        le=10,
        description="Potência usada no ciclo atual. Quando omitida, reaproveita a potência atual do micro-ondas.",
        examples=[7],
    )
    content: str = Field(
        ...,
        description="Conteúdo a ser aquecido. Não pode ser vazio ou conter apenas espaços.",
        examples=["pizza"],
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("content must not be empty")
        return stripped_value


class MicrowaveStateResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "is_on": True,
                "status": "running",
                "power": 7,
                "content": "pizza",
                "ends_at": "2026-04-20T12:00:30Z",
                "remaining_seconds": 29,
                "created_at": "2026-04-20T12:00:00Z",
                "updated_at": "2026-04-20T12:00:01Z",
            }
        },
    )

    id: int = Field(description="Identificador numérico único do micro-ondas.", examples=[1])
    is_on: bool = Field(
        description="Indica se o micro-ondas está aquecendo neste momento.",
        examples=[True],
    )
    status: Literal["idle", "running", "finished"] = Field(
        description="Estado derivado do micro-ondas: parado (`idle`), em execução (`running`) ou ciclo concluído (`finished`).",
        examples=["running"],
    )
    power: int = Field(description="Potência atual configurada no micro-ondas.", examples=[7])
    content: str = Field(
        description="Conteúdo atualmente armazenado dentro do micro-ondas.",
        examples=["pizza"],
    )
    ends_at: datetime | None = Field(
        description="Data e hora previstas para o fim do ciclo atual. Fica `null` quando não há aquecimento ativo.",
        examples=["2026-04-20T12:00:30Z"],
    )
    remaining_seconds: int = Field(
        description="Quantidade de segundos restantes para o término do aquecimento.",
        examples=[29],
    )
    created_at: datetime = Field(
        description="Data e hora de criação da instância do micro-ondas.",
        examples=["2026-04-20T12:00:00Z"],
    )
    updated_at: datetime = Field(
        description="Data e hora da última alteração de estado do micro-ondas.",
        examples=["2026-04-20T12:00:01Z"],
    )


class MicrowaveCollectionResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "is_on": False,
                        "status": "idle",
                        "power": 5,
                        "content": "",
                        "ends_at": None,
                        "remaining_seconds": 0,
                        "created_at": "2026-04-20T12:00:00Z",
                        "updated_at": "2026-04-20T12:00:00Z",
                    },
                    {
                        "id": 2,
                        "is_on": True,
                        "status": "running",
                        "power": 8,
                        "content": "lasanha",
                        "ends_at": "2026-04-20T12:01:00Z",
                        "remaining_seconds": 45,
                        "created_at": "2026-04-20T12:00:00Z",
                        "updated_at": "2026-04-20T12:00:15Z",
                    },
                ]
            }
        }
    )

    items: list[MicrowaveStateResponse] = Field(
        description="Lista de micro-ondas disponíveis no processo da API."
    )


class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "microwave not found"}}
    )

    detail: str = Field(
        description="Mensagem resumida que descreve o erro retornado pela API.",
        examples=["microwave not found"],
    )
