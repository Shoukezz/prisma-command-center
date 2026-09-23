from fastapi.testclient import TestClient


def test_list_events(client: TestClient) -> None:
    client.post("/api/v1/world/advance", json={"minutes": 90})
    response = client.get("/api/v1/events")
    assert response.status_code == 200
    events = response.json()
    assert events
    first = events[0]
    assert "title" in first
    assert "summary" in first
    assert "severity" in first
    assert "coordinates" in first


def test_list_events_respects_limit(client: TestClient) -> None:
    client.post("/api/v1/world/advance", json={"minutes": 600})
    response = client.get("/api/v1/events", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()) <= 2


def test_list_events_rejects_out_of_range_limit(client: TestClient) -> None:
    response = client.get("/api/v1/events", params={"limit": 0})
    assert response.status_code == 422

    response = client.get("/api/v1/events", params={"limit": 500})
    assert response.status_code == 422
