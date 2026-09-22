"""WebSocket endpoints for realtime simulation updates."""

import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """In-process broadcast manager for this single-process local API."""

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for connection in self._connections:
            try:
                await connection.send_json(message)
            except (RuntimeError, WebSocketDisconnect):
                stale.append(connection)
            except Exception:
                logger.exception("Failed to broadcast simulation update")
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


connections = ConnectionManager()


async def broadcast_world_update(kind: str, payload: dict[str, Any]) -> None:
    await connections.broadcast({"type": kind, "payload": payload})


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await connections.connect(websocket)
    await websocket.send_json({"type": "connected"})
    try:
        while True:
            message = await websocket.receive_text()
            if message == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        connections.disconnect(websocket)
