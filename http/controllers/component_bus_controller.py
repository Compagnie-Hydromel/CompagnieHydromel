from fastapi import APIRouter, WebSocket


router = APIRouter()


@router.websocket("/internal/bus")
async def component_bus(socket: WebSocket):
    await socket.app.state.component_hub.serve(socket)
