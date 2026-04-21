from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.schemas.student import CourseCode


@dataclass
class StudentState:
    id: str
    name: str
    email: str
    course: CourseCode
    matricula: int
    active: bool
    created_at: datetime
    updated_at: datetime


class StudentService:
    def __init__(self, *, initial_count: int) -> None:
        self._initial_count = initial_count
        self._lock = Lock()
        self._students: dict[str, StudentState] = {}
        self._next_matricula_by_course: dict[CourseCode, int] = self._build_initial_counters()
        self._seed_defaults(initial_count)

    def reset_store(self, *, initial_count: int | None = None) -> None:
        with self._lock:
            self._students = {}
            self._next_matricula_by_course = self._build_initial_counters()
            self._seed_defaults(self._initial_count if initial_count is None else initial_count)

    def list_students(self) -> list[dict[str, object]]:
        with self._lock:
            return [self._serialize(student) for student in self._students.values()]

    def get_student(self, student_id: str) -> dict[str, object]:
        with self._lock:
            student = self._get_student_or_404(student_id)
            return self._serialize(student)

    def create_student(
        self,
        *,
        name: str,
        email: str,
        course: CourseCode,
        active: bool = True,
    ) -> dict[str, object]:
        with self._lock:
            self._ensure_email_matches_course(email=email, course=course)
            self._ensure_unique(email=email)
            student = self._create_state(
                name=name,
                email=email,
                course=course,
                active=active,
            )
            return self._serialize(student)

    def update_student(
        self,
        student_id: str,
        *,
        name: str | None = None,
        email: str | None = None,
        course: CourseCode | None = None,
        active: bool | None = None,
    ) -> dict[str, object]:
        with self._lock:
            student = self._get_student_or_404(student_id)
            next_course = course if course is not None else student.course
            next_email = email if email is not None else student.email
            self._ensure_email_matches_course(email=next_email, course=next_course)

            if email is not None:
                self._ensure_unique(email=email, ignored_id=student_id)
                student.email = email
            if name is not None:
                student.name = name
            if active is not None:
                student.active = active
            if course is not None and course != student.course:
                old_id = student.id
                matricula = self._next_matricula_by_course[course]
                self._next_matricula_by_course[course] += 1
                student.course = course
                student.matricula = matricula
                student.id = f"{course.value}{matricula}"
                del self._students[old_id]
                self._students[student.id] = student
            student.updated_at = self._now()
            return self._serialize(student)

    def delete_student(self, student_id: str) -> None:
        with self._lock:
            self._get_student_or_404(student_id)
            del self._students[student_id]

    def reset_students(self) -> None:
        with self._lock:
            self._students = {}

    def _seed_defaults(self, initial_count: int) -> None:
        defaults = [
            {
                "name": "Ana Clara Souza",
                "email": "ana.clara@ges.inatel.br",
                "course": CourseCode.GES,
                "active": True,
            },
            {
                "name": "Bruno Lima",
                "email": "bruno.lima@gec.inatel.br",
                "course": CourseCode.GEC,
                "active": True,
            },
        ]

        for data in defaults[:initial_count]:
            self._create_state(**data)

        extra_count = max(initial_count - len(defaults), 0)
        for index in range(extra_count):
            self._create_state(
                name=f"Student {index + 3}",
                email=(
                    f"student.{index + 3}@"
                    f"{(CourseCode.GES if index % 4 == 0 else CourseCode.GEC if index % 4 == 1 else CourseCode.GEB if index % 4 == 2 else CourseCode.GEP).value.lower()}"
                    ".inatel.br"
                ),
                course=CourseCode.GES if index % 4 == 0 else CourseCode.GEC if index % 4 == 1 else CourseCode.GEB if index % 4 == 2 else CourseCode.GEP,
                active=True,
            )

    def _create_state(
        self,
        *,
        name: str,
        email: str,
        course: CourseCode,
        active: bool,
    ) -> StudentState:
        now = self._now()
        matricula = self._next_matricula_by_course[course]
        self._next_matricula_by_course[course] += 1
        student = StudentState(
            id=f"{course.value}{matricula}",
            name=name,
            email=email,
            course=course,
            matricula=matricula,
            active=active,
            created_at=now,
            updated_at=now,
        )
        self._students[student.id] = student
        return student

    def _ensure_unique(
        self,
        *,
        email: str,
        ignored_id: str | None = None,
    ) -> None:
        for student in self._students.values():
            if ignored_id is not None and student.id == ignored_id:
                continue
            if student.email == email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="email ja cadastrado",
                )

    def _get_student_or_404(self, student_id: str) -> StudentState:
        student = self._students.get(student_id)
        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="aluno nao encontrado",
            )
        return student

    @staticmethod
    def _serialize(student: StudentState) -> dict[str, object]:
        return {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "course": student.course,
            "matricula": student.matricula,
            "active": student.active,
            "created_at": student.created_at,
            "updated_at": student.updated_at,
        }

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    @staticmethod
    def _build_initial_counters() -> dict[CourseCode, int]:
        return {
            CourseCode.GES: 1,
            CourseCode.GEC: 1,
            CourseCode.GEB: 1,
            CourseCode.GEP: 1,
        }

    @staticmethod
    def _ensure_email_matches_course(*, email: str, course: CourseCode) -> None:
        email_course = email.split("@", maxsplit=1)[1].split(".", maxsplit=1)[0].upper()
        if email_course != course.value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="dominio do email deve corresponder ao curso informado",
            )


settings = get_settings()
student_service = StudentService(initial_count=settings.initial_student_count)
