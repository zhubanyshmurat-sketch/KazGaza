from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.auth.security import decode_token
from app.notifications.ws_manager import manager

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    token = websocket.cookies.get("access_token")
    payload = decode_token(token) if token else None
    if not payload or payload.get("type") != "access":
        await websocket.close(code=4401)
        return

    await manager.connect(websocket)
    try:
        while True:
            # Clients don't need to send anything; we just keep the
            # connection open and use it for server -> client broadcasts.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
