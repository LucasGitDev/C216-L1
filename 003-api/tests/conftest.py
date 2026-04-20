import pytest
from fastapi.testclient import TestClient

from app.main import create_application


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_application())
