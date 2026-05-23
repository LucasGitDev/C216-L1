from __future__ import annotations

from typing import Any

import asyncpg

PROFESSOR_COLUMNS = "id, nome, email, sala_de_atendimento, created_at, updated_at"


def _row_to_dict(row: asyncpg.Record | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


async def insert(
    conn: asyncpg.Connection,
    *,
    nome: str,
    email: str,
    sala_de_atendimento: str,
) -> dict[str, Any]:
    query = f"""
        INSERT INTO professores (nome, email, sala_de_atendimento)
        VALUES ($1, $2, $3)
        RETURNING {PROFESSOR_COLUMNS}
    """
    row = await conn.fetchrow(query, nome, email, sala_de_atendimento)
    assert row is not None
    return dict(row)


async def list_all(conn: asyncpg.Connection) -> list[dict[str, Any]]:
    rows = await conn.fetch(
        f"SELECT {PROFESSOR_COLUMNS} FROM professores ORDER BY id"
    )
    return [dict(row) for row in rows]


async def get_by_id(
    conn: asyncpg.Connection, professor_id: int
) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        f"SELECT {PROFESSOR_COLUMNS} FROM professores WHERE id = $1", professor_id
    )
    return _row_to_dict(row)


async def email_exists(
    conn: asyncpg.Connection, email: str, *, exclude_id: int | None = None
) -> bool:
    if exclude_id is None:
        row = await conn.fetchrow("SELECT 1 FROM professores WHERE email = $1", email)
    else:
        row = await conn.fetchrow(
            "SELECT 1 FROM professores WHERE email = $1 AND id <> $2",
            email,
            exclude_id,
        )
    return row is not None


async def update_fields(
    conn: asyncpg.Connection,
    professor_id: int,
    *,
    nome: str | None,
    email: str | None,
    sala_de_atendimento: str | None,
) -> dict[str, Any] | None:
    query = f"""
        UPDATE professores SET
            nome = COALESCE($2, nome),
            email = COALESCE($3, email),
            sala_de_atendimento = COALESCE($4, sala_de_atendimento),
            updated_at = now()
        WHERE id = $1
        RETURNING {PROFESSOR_COLUMNS}
    """
    row = await conn.fetchrow(query, professor_id, nome, email, sala_de_atendimento)
    return _row_to_dict(row)


async def delete(conn: asyncpg.Connection, professor_id: int) -> bool:
    result = await conn.execute("DELETE FROM professores WHERE id = $1", professor_id)
    return result.endswith(" 1")


async def delete_all(conn: asyncpg.Connection) -> None:
    await conn.execute("TRUNCATE professores RESTART IDENTITY")
