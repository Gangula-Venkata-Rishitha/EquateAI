"""Chat-related Pydantic schemas."""
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str  # user, assistant
    content: str


class ChatRequest(BaseModel):
    session_id: str
    document_id: int | None = None
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str
