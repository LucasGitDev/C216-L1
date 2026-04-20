import pytest
from fastapi.testclient import TestClient

from app.main import create_application
from app.services.microwaves import microwave_service


@pytest.fixture
def client() -> TestClient:
    microwave_service.reset_store()
    return TestClient(create_application())
