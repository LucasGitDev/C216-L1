from abc import ABC, abstractmethod

from inas_cli.domain.student import Student


class StudentRepository(ABC):
    @abstractmethod
    def insert(self, student: Student) -> None: ...

    @abstractmethod
    def list_all(self) -> list[Student]: ...

    @abstractmethod
    def get_by_enrollment(self, enrollment: str) -> Student | None: ...

    @abstractmethod
    def update(self, student: Student) -> None: ...

    @abstractmethod
    def delete(self, enrollment: str) -> bool: ...
