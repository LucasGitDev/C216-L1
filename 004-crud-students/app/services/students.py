from __future__ import annotations

from typing import Any

import asyncpg
from fastapi import HTTPException, status

from app.repositories import students as students_repo
from app.schemas.student import CourseCode


def _ensure_email_matches_course(*, email: str, course: CourseCode) -> None:
    email_course = email.split("@", maxsplit=1)[1].split(".", maxsplit=1)[0].upper()
    if email_course != course.value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="dominio do email deve corresponder ao curso informado",
        )


def _serialize(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "course": CourseCode(row["course"]),
        "matricula": row["matricula"],
        "active": row["active"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


async def list_students(conn: asyncpg.Connection) -> list[dict[str, Any]]:
    rows = await students_repo.list_all(conn)
    return [_serialize(row) for row in rows]


async def get_student(conn: asyncpg.Connection, student_id: str) -> dict[str, Any]:
    row = await students_repo.get_by_id(conn, student_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="aluno nao encontrado",
        )
    return _serialize(row)


async def create_student(
    conn: asyncpg.Connection,
    *,
    name: str,
    email: str,
    course: CourseCode,
    active: bool = True,
) -> dict[str, Any]:
    _ensure_email_matches_course(email=email, course=course)
    try:
        row = await students_repo.insert(
            conn, name=name, email=email, course=course, active=active
        )
    except asyncpg.UniqueViolationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email ja cadastrado",
        ) from exc
    return _serialize(row)


async def update_student(
    conn: asyncpg.Connection,
    student_id: str,
    *,
    name: str | None = None,
    email: str | None = None,
    course: CourseCode | None = None,
    active: bool | None = None,
) -> dict[str, Any]:
    existing = await students_repo.get_by_id(conn, student_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="aluno nao encontrado",
        )

    current_course = CourseCode(existing["course"])
    next_course = course if course is not None else current_course
    next_email = email if email is not None else existing["email"]
    _ensure_email_matches_course(email=next_email, course=next_course)

    try:
        if course is not None and course != current_course:
            row = await students_repo.reassign_course(
                conn,
                student_id,
                new_course=course,
                name=name,
                email=email,
                active=active,
            )
        else:
            row = await students_repo.update_fields(
                conn,
                student_id,
                name=name,
                email=email,
                active=active,
            )
    except asyncpg.UniqueViolationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email ja cadastrado",
        ) from exc

    assert row is not None
    return _serialize(row)


async def delete_student(conn: asyncpg.Connection, student_id: str) -> None:
    deleted = await students_repo.delete(conn, student_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="aluno nao encontrado",
        )


async def reset_students(conn: asyncpg.Connection) -> None:
    await students_repo.delete_all(conn)
