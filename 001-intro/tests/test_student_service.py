import unittest

from inas_cli.repositories.in_memory_student_repository import InMemoryStudentRepository
from inas_cli.services.errors import (
    InvalidCourseError,
    InvalidEmailError,
    StudentNotFoundError,
)
from inas_cli.services.student_service import StudentService


class TestStudentService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = StudentService(InMemoryStudentRepository())

    def test_should_create_sequential_enrollment_by_course(self) -> None:
        student1 = self.service.create("Ana", "ana@inatel.br", "GES")
        student2 = self.service.create("Bia", "bia@inatel.br", "GES")
        student3 = self.service.create("Cadu", "cadu@inatel.br", "GET")

        self.assertEqual(student1.enrollment, "GES1")
        self.assertEqual(student2.enrollment, "GES2")
        self.assertEqual(student3.enrollment, "GET1")

    def test_should_fail_with_invalid_email(self) -> None:
        with self.assertRaises(InvalidEmailError):
            self.service.create("Ana", "email-invalido", "GES")

    def test_should_fail_with_invalid_course(self) -> None:
        with self.assertRaises(InvalidCourseError):
            self.service.create("Ana", "ana@inatel.br", "ABC")

    def test_should_update_and_generate_new_enrollment_on_course_change(self) -> None:
        student = self.service.create("Ana", "ana@inatel.br", "GES")
        updated = self.service.update(
            student.enrollment,
            name="Ana Maria",
            email="anamaria@inatel.br",
            course="GET",
        )

        self.assertEqual(updated.name, "Ana Maria")
        self.assertEqual(updated.email, "anamaria@inatel.br")
        self.assertEqual(updated.enrollment, "GET1")
        with self.assertRaises(StudentNotFoundError):
            self.service.get("GES1")

    def test_should_delete_student(self) -> None:
        student = self.service.create("Ana", "ana@inatel.br", "GES")
        self.service.delete(student.enrollment)

        with self.assertRaises(StudentNotFoundError):
            self.service.get(student.enrollment)

    def test_should_normalize_name_email_and_course_on_create(self) -> None:
        student = self.service.create("  Ana  ", "  ANA@INATEL.BR  ", "ges")

        self.assertEqual(student.name, "Ana")
        self.assertEqual(student.email, "ana@inatel.br")
        self.assertEqual(student.course.value, "GES")

    def test_should_keep_enrollment_when_updating_same_course(self) -> None:
        student = self.service.create("Ana", "ana@inatel.br", "GES")
        updated = self.service.update(student.enrollment, name="Ana Clara", course="GES")

        self.assertEqual(updated.enrollment, student.enrollment)
        self.assertEqual(updated.name, "Ana Clara")

    def test_should_raise_not_found_when_getting_missing_student(self) -> None:
        with self.assertRaises(StudentNotFoundError):
            self.service.get("GES999")

    def test_should_raise_not_found_when_updating_missing_student(self) -> None:
        with self.assertRaises(StudentNotFoundError):
            self.service.update("GES404", name="Ghost")

    def test_should_raise_not_found_when_deleting_missing_student(self) -> None:
        with self.assertRaises(StudentNotFoundError):
            self.service.delete("GET777")

    def test_should_list_students_sorted_by_enrollment(self) -> None:
        self.service.create("Carlos", "carlos@inatel.br", "GET")
        self.service.create("Ana", "ana@inatel.br", "GES")
        self.service.create("Bia", "bia@inatel.br", "GES")

        enrollments = [student.enrollment for student in self.service.list_all()]
        self.assertEqual(enrollments, ["GES1", "GES2", "GET1"])


if __name__ == "__main__":
    unittest.main()
