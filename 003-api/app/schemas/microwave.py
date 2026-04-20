from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MicrowaveCreateRequest(BaseModel):
    power: int = Field(default=5, ge=1, le=10)
    content: str = ""


class MicrowaveStartRequest(BaseModel):
    duration_seconds: int = Field(..., gt=0, le=3600)
    power: int | None = Field(default=None, ge=1, le=10)
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("content must not be empty")
        return stripped_value


class MicrowaveStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_on: bool
    status: Literal["idle", "running", "finished"]
    power: int
    content: str
    ends_at: datetime | None
    remaining_seconds: int
    created_at: datetime
    updated_at: datetime


class MicrowaveCollectionResponse(BaseModel):
    items: list[MicrowaveStateResponse]
