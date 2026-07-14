from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileCreate(BaseModel):
    path: str
    content: Optional[str] = None
    language: Optional[str] = None

class FileUpdate(BaseModel):
    content: Optional[str] = None
    language: Optional[str] = None

class FileResponse(BaseModel):
    id: str
    project_id: str
    path: str
    content: Optional[str] = None
    language: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
