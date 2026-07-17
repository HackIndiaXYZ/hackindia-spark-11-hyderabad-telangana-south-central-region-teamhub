import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws")
async def terminal_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            cmd = await websocket.receive_text()
            process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            if stdout:
                await websocket.send_text(stdout.decode())
            if stderr:
                await websocket.send_text(stderr.decode())
            await websocket.send_text(f"EXIT:{process.returncode}")
    except WebSocketDisconnect:
        logger.info("Terminal WebSocket disconnected")
