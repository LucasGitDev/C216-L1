from __future__ import annotations

from typing import Any

import asyncpg

from app.schemas.student import CourseCode

STUDENT_COLUMNS = "id, name, email, course, matricula, active, created_at, updated_at"

_SEQUENCE_BY_COURSE: dict[CourseCode, str] = {
    CourseCode.GES: "seq_matricula_ges",
    CourseCode.GEC: "seq_matricula_gec",
    CourseCode.GEB: "seq_matricula_geb",
    CourseCode.GEP: "seq_matricula_gep",
}


def _sequence_for(course: CourseCode) -> str:
    return _SEQUENCE_BY_COURSE[course]


def _row_to_dict(row: asyncpg.Record | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


async def insert(
    conn: asyncpg.Connection,
    *,
    name: str,
    email: str,
    course: CourseCode,
    active: bool,
) -> dict[str, Any]:
    sequence = _sequence_for(course)
    query = f"""
        WITH next_id AS (
            SELECT nextval('{sequence}') AS matricula
        )
        INSERT INTO students (id, name, email, course, matricula, active)
        SELECT $1 || matricula::text, $2, $3, $1::course_code, matricula, $4
        FROM next_id
        RETURNING {STUDENT_COLUMNS}
    """
    row = await conn.fetchrow(query, course.value, name, email, active)
    assert row is not None
    return dict(row)


async def list_all(conn: asyncpg.Connection) -> list[dict[str, Any]]:
    rows = await conn.fetch(
        f"SELECT {STUDENT_COLUMNS} FROM students ORDER BY created_at, id"
    )
    return [dict(row) for row in rows]


async def get_by_id(
    conn: asyncpg.Connection, student_id: str
) -> dict[str, Any] | None:
    row = await conn.fetchrow(
        f"SELECT {STUDENT_COLUMNS} FROM students WHERE id = $1", student_id
    )
    return _row_to_dict(row)


async def email_exists(
    conn: asyncpg.Connection, email: str, *, exclude_id: str | None = None
) -> bool:
    if exclude_id is None:
        row = await conn.fetchrow("SELECT 1 FROM students WHERE email = $1", email)
    else:
        row = await conn.fetchrow(
            "SELECT 1 FROM students WHERE email = $1 AND id <> $2",
            email,
            exclude_id,
        )
    return row is not None


async def update_fields(
    conn: asyncpg.Connection,
    student_id: str,
    *,
    name: str | None,
    email: str | None,
    active: bool | None,
) -> dict[str, Any] | None:
    query = f"""
        UPDATE students SET
            name = COALESCE($2, name),
            email = COALESCE($3, email),
            active = COALESCE($4, active),
            updated_at = now()
        WHERE id = $1
        RETURNING {STUDENT_COLUMNS}
    """
    row = await conn.fetchrow(query, student_id, name, email, active)
    return _row_to_dict(row)


async def reassign_course(
    conn: asyncpg.Connection,
    student_id: str,
    *,
    new_course: CourseCode,
    name: str | None,
    email: str | None,
    active: bool | None,
) -> dict[str, Any] | None:
    sequence = _sequence_for(new_course)
    query = f"""
        WITH next_id AS (
            SELECT nextval('{sequence}') AS new_matricula
        )
        UPDATE students SET
            id = $2 || next_id.new_matricula::text,
            course = $2::course_code,
            matricula = next_id.new_matricula,
            name = COALESCE($3, name),
            email = COALESCE($4, email),
            active = COALESCE($5, active),
            updated_at = now()
        FROM next_id
        WHERE students.id = $1
        RETURNING {STUDENT_COLUMNS}
    """
    row = await conn.fetchrow(query, student_id, new_course.value, name, email, active)
    return _row_to_dict(row)


async def delete(conn: asyncpg.Connection, student_id: str) -> bool:
    result = await conn.execute("DELETE FROM students WHERE id = $1", student_id)
    return result.endswith(" 1")


async def delete_all(conn: asyncpg.Connection) -> None:
    await conn.execute("DELETE FROM students")
