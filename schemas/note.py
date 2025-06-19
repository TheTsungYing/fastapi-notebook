from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class NoteCreate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None

class NoteOutput(BaseModel):
    id: int
    title: Optional[str]
    content: Optional[str]
    tags: Optional[list[str]]
    created_time: datetime
    updated_time: datetime
