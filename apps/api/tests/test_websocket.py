from fastapi.testclient import TestClient


def test_websocket_sends_connected_message_on_connect(client: TestClient) -> None:
    with client.websocket_connect("/ws") as websocket:
        message = websocket.receive_json()
        assert message == {"type": "connected"}


def test_websocket_responds_to_ping_with_pong(client: TestClient) -> None:
    with client.websocket_connect("/ws") as websocket:
        websocket.receive_json()  # connected
        websocket.send_text("ping")
        message = websocket.receive_json()
        assert message == {"type": "pong"}


def test_websocket_receives_world_update_broadcast_on_advance(client: TestClient) -> None:
    with client.websocket_connect("/ws") as websocket:
        websocket.receive_json()  # connected

        response = client.post("/api/v1/world/advance", json={"minutes": 60})
        assert response.status_code == 200

        message = websocket.receive_json()
        assert message["type"] == "world.updated"
        assert message["payload"]["clock"]["game_minutes"] == 60
