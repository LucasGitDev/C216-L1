import json
from pathlib import Path

from inas_cli.domain.enums import Course
from inas_cli.domain.student import Student
from inas_cli.repositories.in_memory_student_repository import InMemoryStudentRepository


class JsonStudentRepository(InMemoryStudentRepository):
    def __init__(self, file_path: str) -> None:
        super().__init__()
        self._path = Path(file_path)
        self._load()

    def insert(self, student: Student) -> None:
        super().insert(student)
        self._save()

    def update(self, student: Student) -> None:
        super().update(student)
        self._save()

    def delete(self, enrollment: str) -> bool:
        was_deleted = super().delete(enrollment)
        if was_deleted:
            self._save()
        return was_deleted

    def _load(self) -> None:
        if not self._path.exists():
            return
        raw_data = json.loads(self._path.read_text(encoding="utf-8"))
        for item in raw_data:
            student = Student(
                name=item["name"],
                email=item["email"],
                course=Course(item["course"]),
                enrollment=item["enrollment"],
            )
            super().insert(student)

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        content = [
            {
                "name": student.name,
                "email": student.email,
                "course": student.course.value,
                "enrollment": student.enrollment,
            }
            for student in self.list_all()
        ]
        self._path.write_text(
            json.dumps(content, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
