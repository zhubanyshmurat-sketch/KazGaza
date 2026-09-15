import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """In-process WebSocket fan-out for dashboard realtime updates.

    Single-backend-instance friendly; if the backend is ever scaled
    horizontally this should be swapped for a Redis pub/sub backed
    broadcaster (the RATE_LIMIT/REDIS_URL setting is already available).
    """

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.discard(ws)

    async def broadcast(self, event: str, payload: dict[str, Any]) -> None:
        message = json.dumps({"event": event, "payload": payload}, default=str)
        dead = []
        for ws in self._connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()
