from time import sleep

from fastapi.testclient import TestClient


def test_list_microwaves_returns_two_preloaded_instances(client: TestClient) -> None:
    response = client.get("/api/v1/microwaves")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 2
    assert [item["id"] for item in payload["items"]] == [1, 2]


def test_create_microwave_returns_new_instance(client: TestClient) -> None:
    response = client.post("/api/v1/microwaves", json={})

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == 3
    assert payload["status"] == "idle"
    assert payload["power"] == 5
    assert payload["content"] == ""


def test_get_microwave_returns_specific_state(client: TestClient) -> None:
    response = client.get("/api/v1/microwaves/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert payload["is_on"] is False


def test_start_microwave_updates_state(client: TestClient) -> None:
    response = client.post(
        "/api/v1/microwaves/1/start",
        json={"duration_seconds": 30, "power": 7, "content": "pizza"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_on"] is True
    assert payload["status"] == "running"
    assert payload["power"] == 7
    assert payload["content"] == "pizza"
    assert 0 < payload["remaining_seconds"] <= 30
    assert payload["ends_at"] is not None


def test_start_microwave_rejects_empty_content(client: TestClient) -> None:
    response = client.post(
        "/api/v1/microwaves/1/start",
        json={"duration_seconds": 30, "content": "   "},
    )

    assert response.status_code == 422


def test_start_microwave_rejects_when_running(client: TestClient) -> None:
    client.post(
        "/api/v1/microwaves/1/start",
        json={"duration_seconds": 30, "content": "soup"},
    )

    response = client.post(
        "/api/v1/microwaves/1/start",
        json={"duration_seconds": 15, "content": "rice"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "microwave is already running"


def test_stop_microwave_turns_it_off(client: TestClient) -> None:
    client.post(
        "/api/v1/microwaves/1/start",
        json={"duration_seconds": 30, "content": "coffee"},
    )

    response = client.post("/api/v1/microwaves/1/stop")

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_on"] is False
    assert payload["status"] == "idle"
    assert payload["remaining_seconds"] == 0
    assert payload["ends_at"] is None
    assert payload["content"] == "coffee"


def test_stop_microwave_rejects_when_already_stopped(client: TestClient) -> None:
    response = client.post("/api/v1/microwaves/1/stop")

    assert response.status_code == 409
    assert response.json()["detail"] == "microwave is already stopped"


def test_reset_microwave_returns_default_state(client: TestClient) -> None:
    client.post(
        "/api/v1/microwaves/1/start",
        json={"duration_seconds": 30, "power": 7, "content": "lasagna"},
    )

    response = client.post("/api/v1/microwaves/1/reset")

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_on"] is False
    assert payload["status"] == "idle"
    assert payload["power"] == 5
    assert payload["content"] == ""
    assert payload["remaining_seconds"] == 0
    assert payload["ends_at"] is None


def test_delete_created_microwave_removes_instance(client: TestClient) -> None:
    create_response = client.post("/api/v1/microwaves", json={})
    microwave_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/microwaves/{microwave_id}")
    get_response = client.get(f"/api/v1/microwaves/{microwave_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_operations_fail_for_removed_id(client: TestClient) -> None:
    create_response = client.post("/api/v1/microwaves", json={})
    microwave_id = create_response.json()["id"]
    client.delete(f"/api/v1/microwaves/{microwave_id}")

    response = client.post(
        f"/api/v1/microwaves/{microwave_id}/start",
        json={"duration_seconds": 30, "content": "tea"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "microwave not found"


def test_expired_timer_is_reflected_as_finished(client: TestClient) -> None:
    client.post(
        "/api/v1/microwaves/1/start",
        json={"duration_seconds": 1, "content": "bread"},
    )

    sleep(1.1)
    response = client.get("/api/v1/microwaves/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_on"] is False
    assert payload["status"] == "finished"
    assert payload["remaining_seconds"] == 0
    assert payload["ends_at"] is None
