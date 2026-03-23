from dataclasses import dataclass

from inas_cli.domain.enums import Course


@dataclass(slots=True)
class Student:
    name: str
    email: str
    course: Course
    enrollment: str
