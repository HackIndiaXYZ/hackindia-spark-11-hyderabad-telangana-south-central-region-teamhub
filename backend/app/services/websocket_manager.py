import json
import logging
from fastapi import WebSocket
from typing import Any

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}

    async def initialize(self):
        logger.info("WebSocket manager initialized")

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        self.connections.pop(client_id, None)
        logger.info(f"Client {client_id} disconnected")

    async def send_message(self, client_id: str, message: dict):
        ws = self.connections.get(client_id)
        if ws:
            await ws.send_json(message)

    async def broadcast(self, message: dict):
        for ws in self.connections.values():
            await ws.send_json(message)

    async def handle_message(self, client_id: str, data: dict[str, Any]):
        msg_type = data.get("type", "")
        if msg_type == "ping":
            await self.send_message(client_id, {"type": "pong"})
        elif msg_type == "chat":
            from app.services.llm_service import llm_service
            msgs = [{"role": "user", "content": data.get("message", "")}]
            async for chunk in await llm_service.chat(msgs, stream=True):
                await self.send_message(client_id, {"type": "chunk", "content": chunk})
            await self.send_message(client_id, {"type": "done"})
        else:
            await self.send_message(client_id, {"type": "error", "message": f"Unknown message type: {msg_type}"})

ws_manager = WebSocketManager()
