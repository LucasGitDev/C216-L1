import pytest
from fastapi.testclient import TestClient

from app.main import create_application
from app.services.students import student_service


@pytest.fixture
def client() -> TestClient:
    student_service.reset_store(initial_count=0)
    return TestClient(create_application())
