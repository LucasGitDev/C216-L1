import re

from inas_cli.domain.enums import Course
from inas_cli.domain.student import Student
from inas_cli.repositories.student_repository import StudentRepository
from inas_cli.services.errors import (
    InvalidCourseError,
    InvalidEmailError,
    StudentNotFoundError,
)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class StudentService:
    def __init__(self, repository: StudentRepository) -> None:
        self._repository = repository

    def create(self, name: str, email: str, course: str) -> Student:
        normalized_name = name.strip()
        normalized_email = email.strip().lower()
        course_enum = self._parse_course(course)
        self._validate_email(normalized_email)
        enrollment = self._generate_enrollment(course_enum)
        student = Student(
            name=normalized_name,
            email=normalized_email,
            course=course_enum,
            enrollment=enrollment,
        )
        self._repository.insert(student)
        return student

    def list_all(self) -> list[Student]:
        return self._repository.list_all()

    def get(self, enrollment: str) -> Student:
        student = self._repository.get_by_enrollment(enrollment.strip().upper())
        if student is None:
            raise StudentNotFoundError("Enrollment not found.")
        return student

    def update(
        self,
        enrollment: str,
        name: str | None = None,
        email: str | None = None,
        course: str | None = None,
    ) -> Student:
        student = self.get(enrollment)
        new_name = student.name if name is None else name.strip()
        new_email = student.email if email is None else email.strip().lower()
        new_course = student.course if course is None else self._parse_course(course)
        self._validate_email(new_email)

        if new_course != student.course:
            new_enrollment = self._generate_enrollment(new_course)
            self._repository.delete(student.enrollment)
        else:
            new_enrollment = student.enrollment

        updated_student = Student(
            name=new_name,
            email=new_email,
            course=new_course,
            enrollment=new_enrollment,
        )
        self._repository.update(updated_student)
        return updated_student

    def delete(self, enrollment: str) -> None:
        was_deleted = self._repository.delete(enrollment.strip().upper())
        if not was_deleted:
            raise StudentNotFoundError("Enrollment not found.")

    def _parse_course(self, course: str) -> Course:
        value = course.strip().upper()
        try:
            return Course(value)
        except ValueError as error:
            options = ", ".join(item.value for item in Course)
            raise InvalidCourseError(f"Invalid course. Use one of: {options}.") from error

    def _validate_email(self, email: str) -> None:
        if not EMAIL_REGEX.match(email):
            raise InvalidEmailError("Invalid email.")

    def _generate_enrollment(self, course: Course) -> str:
        prefix = course.value
        numbers: list[int] = []
        for student in self._repository.list_all():
            if student.enrollment.startswith(prefix):
                suffix = student.enrollment.removeprefix(prefix)
                if suffix.isdigit():
                    numbers.append(int(suffix))
        next_number = 1 if not numbers else max(numbers) + 1
        return f"{prefix}{next_number}"
