from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessageSchema(BaseModel):
    role: str
    content: str
    agent_name: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None
    stream: bool = False

class ChatResponse(BaseModel):
    chat_id: str
    message: str
    agent_name: Optional[str] = None

class ChatHistory(BaseModel):
    id: str
    title: str
    pinned: bool = False
    created_at: datetime
    updated_at: datetime
    messages: List[MessageSchema] = []

    class Config:
        from_attributes = True
