from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.schemas.todo import TodoResponse


class ChatRequest(BaseModel):
    """Request schema for chat messages."""
    content: str


class ChatResponse(BaseModel):
    """Response schema for chat messages."""
    message: str
    todos_affected: Optional[List[TodoResponse]] = None


class ChatHistoryItem(BaseModel):
    """Schema for individual chat history items."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
