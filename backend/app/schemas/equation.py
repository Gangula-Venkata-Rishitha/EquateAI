"""Equation-related Pydantic schemas."""
from pydantic import BaseModel


class EquationResponse(BaseModel):
    equation_id: int
    document_id: int
    page: int | None
    line_no: int | None
    raw_text: str
    confidence_score: float | None
    variables: list[str] | None = None
    ast_json: dict | None = None

    class Config:
        from_attributes = True


class EquationExplainRequest(BaseModel):
    equation_id: int | None = None  # optional when provided in path
    context: str | None = None
