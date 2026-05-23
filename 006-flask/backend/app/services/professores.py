from __future__ import annotations

from typing import Any

import asyncpg
from fastapi import HTTPException, status

from app.repositories import professores as professores_repo


def _serialize(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "sala_de_atendimento": row["sala_de_atendimento"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


async def list_professores(conn: asyncpg.Connection) -> list[dict[str, Any]]:
    rows = await professores_repo.list_all(conn)
    return [_serialize(row) for row in rows]


async def get_professor(conn: asyncpg.Connection, professor_id: int) -> dict[str, Any]:
    row = await professores_repo.get_by_id(conn, professor_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="professor nao encontrado",
        )
    return _serialize(row)


async def create_professor(
    conn: asyncpg.Connection,
    *,
    nome: str,
    email: str,
    sala_de_atendimento: str,
) -> dict[str, Any]:
    if await professores_repo.email_exists(conn, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email ja cadastrado",
        )
    try:
        row = await professores_repo.insert(
            conn, nome=nome, email=email, sala_de_atendimento=sala_de_atendimento
        )
    except asyncpg.UniqueViolationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email ja cadastrado",
        ) from exc
    return _serialize(row)


async def update_professor(
    conn: asyncpg.Connection,
    professor_id: int,
    *,
    nome: str | None = None,
    email: str | None = None,
    sala_de_atendimento: str | None = None,
) -> dict[str, Any]:
    existing = await professores_repo.get_by_id(conn, professor_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="professor nao encontrado",
        )

    if email is not None and await professores_repo.email_exists(
        conn, email, exclude_id=professor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email ja cadastrado",
        )

    try:
        row = await professores_repo.update_fields(
            conn,
            professor_id,
            nome=nome,
            email=email,
            sala_de_atendimento=sala_de_atendimento,
        )
    except asyncpg.UniqueViolationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email ja cadastrado",
        ) from exc
    assert row is not None
    return _serialize(row)


async def delete_professor(conn: asyncpg.Connection, professor_id: int) -> None:
    deleted = await professores_repo.delete(conn, professor_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="professor nao encontrado",
        )


async def reset_professores(conn: asyncpg.Connection) -> None:
    await professores_repo.delete_all(conn)
