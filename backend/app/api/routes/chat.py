"""Chat with document / equation assistant API."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db, models
from app.schemas import ChatRequest, ChatResponse
from app.agents import LLMAssistantAgent

router = APIRouter(prefix="/chat", tags=["chat"])


def _document_context(db: Session, document_id: int | None) -> str:
    if not document_id:
        return ""
    doc = db.query(models.Document).filter(models.Document.document_id == document_id).first()
    if not doc:
        return ""
    eqs = db.query(models.Equation).filter(models.Equation.document_id == document_id).limit(50).all()
    lines = [f"Document: {doc.filename}", "Equations found:"]
    for e in eqs:
        lines.append(f"  - {e.raw_text}")
    return "\n".join(lines)


@router.post("", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
):
    """Send a message to the document assistant (Ollama). Optionally scoped to a document."""
    context = _document_context(db, body.document_id)
    agent = LLMAssistantAgent()
    history = []  # TODO: load from chat_history table by session_id
    response = agent.chat(body.message, document_context=context or None, history=history)
    return ChatResponse(response=response, session_id=body.session_id)
