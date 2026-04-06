"""Convert natural-language descriptions to equations."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db import models
from app.services.llm_client import LLMClient


@dataclass
class ParsedEquationText:
    raw_text: str


class TextToEquationService:
    """Hybrid rule-based + LLM text → equation converter."""

    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMClient()

    def _rule_based(self, text: str) -> str | None:
        t = text.lower().strip()
        # Very small set of canonical physics examples
        if "force" in t and "mass" in t and "acceleration" in t:
            return "F = m * a"
        if "kinetic energy" in t and "half" in t and "mass" in t and "velocity" in t:
            return "E_k = 1/2 * m * v^2"
        return None

    def from_text(self, text: str) -> ParsedEquationText:
        """Convert English description to equation string."""
        rb = self._rule_based(text)
        if rb:
            return ParsedEquationText(raw_text=rb)

        prompt = (
            "Convert the following natural-language description into a single mathematical equation.\n"
            "Return only the equation, in plain ASCII math (use *, /, ^, parentheses) and a single '=' if needed.\n\n"
            f"Description: {text}"
        )
        eq = self.llm.chat(
            prompt,
            model=self.llm.equation_model,
            query=text,
            domain_context=None,
            require_context=False,
        )
        # Best-effort cleanup: take first line
        eq_line = eq.splitlines()[0].strip()
        return ParsedEquationText(raw_text=eq_line)

