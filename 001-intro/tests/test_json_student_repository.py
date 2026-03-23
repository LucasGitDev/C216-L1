import json
import tempfile
import unittest
from pathlib import Path

from inas_cli.domain.enums import Course
from inas_cli.domain.student import Student
from inas_cli.repositories.json_student_repository import JsonStudentRepository


class TestJsonStudentRepository(unittest.TestCase):
    def test_should_persist_student_on_insert(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "students.json"
            repository = JsonStudentRepository(str(file_path))

            repository.insert(
                Student(
                    name="Ana",
                    email="ana@inatel.br",
                    course=Course.GES,
                    enrollment="GES1",
                )
            )

            content = json.loads(file_path.read_text(encoding="utf-8"))
            self.assertEqual(len(content), 1)
            self.assertEqual(content[0]["name"], "Ana")
            self.assertEqual(content[0]["enrollment"], "GES1")

    def test_should_load_existing_file_data(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "students.json"
            file_path.write_text(
                json.dumps(
                    [
                        {
                            "name": "Ana",
                            "email": "ana@inatel.br",
                            "course": "GES",
                            "enrollment": "GES1",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            repository = JsonStudentRepository(str(file_path))
            student = repository.get_by_enrollment("GES1")

            self.assertIsNotNone(student)
            assert student is not None
            self.assertEqual(student.name, "Ana")
            self.assertEqual(student.course, Course.GES)

    def test_should_persist_updates_and_deletions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "students.json"
            repository = JsonStudentRepository(str(file_path))

            repository.insert(
                Student(
                    name="Ana",
                    email="ana@inatel.br",
                    course=Course.GES,
                    enrollment="GES1",
                )
            )
            repository.update(
                Student(
                    name="Ana Maria",
                    email="anamaria@inatel.br",
                    course=Course.GES,
                    enrollment="GES1",
                )
            )
            repository.delete("GES1")

            content = json.loads(file_path.read_text(encoding="utf-8"))
            self.assertEqual(content, [])


if __name__ == "__main__":
    unittest.main()
