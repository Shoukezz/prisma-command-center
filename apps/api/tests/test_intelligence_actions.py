from fastapi.testclient import TestClient


def _create_report(client: TestClient) -> dict:
    client.post("/api/v1/world/advance", json={"minutes": 120})
    reports = client.get("/api/v1/intelligence/reports").json()
    assert reports
    return reports[0]


def test_request_more_intelligence_creates_follow_up(client: TestClient) -> None:
    report = _create_report(client)

    response = client.post(
        f"/api/v1/intelligence/reports/{report['id']}/action",
        json={"action_type": "request_more_intel"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"

    reports = client.get("/api/v1/intelligence/reports").json()
    assert any("Додатковий збір даних" in item["title"] for item in reports)


def test_websocket_announces_manual_world_update(client: TestClient) -> None:
    with client.websocket_connect("/ws") as websocket:
        assert websocket.receive_json()["type"] == "connected"
        response = client.post("/api/v1/world/advance", json={"minutes": 15})
        assert response.status_code == 200
        assert websocket.receive_json()["type"] == "world.updated"
