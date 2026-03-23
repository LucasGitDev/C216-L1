from inas_cli.domain.student import Student
from inas_cli.repositories.student_repository import StudentRepository


class InMemoryStudentRepository(StudentRepository):
    def __init__(self) -> None:
        self._items: dict[str, Student] = {}

    def insert(self, student: Student) -> None:
        self._items[student.enrollment] = student

    def list_all(self) -> list[Student]:
        return sorted(self._items.values(), key=lambda item: item.enrollment)

    def get_by_enrollment(self, enrollment: str) -> Student | None:
        return self._items.get(enrollment)

    def update(self, student: Student) -> None:
        self._items[student.enrollment] = student

    def delete(self, enrollment: str) -> bool:
        return self._items.pop(enrollment, None) is not None
