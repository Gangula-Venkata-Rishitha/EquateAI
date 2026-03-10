"""Equation reasoning API: explanations, text conversions."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db import get_db, models
from app.schemas import EquationExplainRequest
from app.agents import LLMAssistantAgent
from app.services import NaturalLanguageConverter, TextToEquationService

router = APIRouter(prefix="/equations", tags=["equations"])


@router.post("/{equation_id}/explain")
def explain_equation(
    equation_id: int,
    body: EquationExplainRequest | None = None,
    db: Session = Depends(get_db),
):
    """Get natural language explanation of an equation via LLM (Ollama)."""
    eq = db.query(models.Equation).filter(models.Equation.equation_id == equation_id).first()
    if not eq:
        raise HTTPException(404, "Equation not found")
    context = body.context if body else None
    agent = LLMAssistantAgent()
    explanation = agent.explain_equation(eq.raw_text, context=context)
    return {"equation_id": equation_id, "raw_text": eq.raw_text, "explanation": explanation}


@router.post("/{equation_id}/to-text")
def equation_to_text(
    equation_id: int,
    db: Session = Depends(get_db),
):
    """Deterministic equation → natural-language conversion with LLM fallback."""
    eq = db.query(models.Equation).filter(models.Equation.equation_id == equation_id).first()
    if not eq:
        raise HTTPException(404, "Equation not found")
    conv = NaturalLanguageConverter()
    text = conv.to_text(eq)
    db.commit()
    return {"equation_id": equation_id, "raw_text": eq.raw_text, "explanation": text, "readable": True}


@router.post("/from-text")
def equation_from_text(
    body: dict,
    db: Session = Depends(get_db),
):
    """Create an equation object from natural-language text (not yet stored)."""
    text = (body or {}).get("text")
    if not text:
        raise HTTPException(400, "Missing 'text' field")
    svc = TextToEquationService(db)
    parsed = svc.from_text(text)
    return {"raw_text": parsed.raw_text}
