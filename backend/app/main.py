import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, create_tables
from app.core.config import settings
import app.models  # noqa: F401 — ensure all models are registered with Base.metadata
from app.api.v1 import auth, projects, files, agents, chat, terminal, visualization, memory
from app.services.websocket_manager import ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CODEBUDDY...")
    await create_tables()
    await ws_manager.initialize()
    yield
    await engine.dispose()
    logger.info("Shutdown complete.")

app = FastAPI(title="CODEBUDDY API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(terminal.router, prefix="/api/v1/terminal", tags=["terminal"])
app.include_router(visualization.router, prefix="/api/v1/visualization", tags=["visualization"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["memory"])

@app.get("/")
async def root():
    return {"name": "CODEBUDDY API", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0", "service": "CODEBUDDY"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.handle_message(client_id, data)
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WS error: {e}")
        ws_manager.disconnect(client_id)
