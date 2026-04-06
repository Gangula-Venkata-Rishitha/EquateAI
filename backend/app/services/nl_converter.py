"""Convert equations to natural-language text."""
from __future__ import annotations

from typing import Any

from sympy import Eq
from sympy.parsing.sympy_parser import parse_expr

from app.db import models
from app.services.llm_client import LLMClient


OP_WORDS = {
    "+": "plus",
    "-": "minus",
    "*": "multiplied by",
    "/": "divided by",
    "^": "to the power of",
}


class NaturalLanguageConverter:
    """Rule-based equation → text converter with LLM fallback."""

    def __init__(self) -> None:
        self.llm = LLMClient()

    def _rule_based(self, raw: str) -> str | None:
        text = raw.strip()
        if not text:
            return None
        # Very lightweight replacement; this is intentionally simple.
        out = text
        for sym, word in OP_WORDS.items():
            out = out.replace(sym, f" {word} ")
        # Normalize spaces
        out = " ".join(out.split())
        # Add basic template
        if "=" in out:
            lhs, rhs = out.split("=", 1)
            return f"{lhs.strip()} equals {rhs.strip()}."
        return None

    def to_text(self, eq: models.Equation) -> str:
        """Produce a natural-language description for a stored equation."""
        # Use cached value if present
        if eq.natural_language:
            return eq.natural_language

        raw = eq.raw_text or ""
        rb = self._rule_based(raw)
        if rb:
            eq.natural_language = rb
            return rb

        # Fallback to LLM for complex expressions
        prompt = (
            "Explain the following scientific/mathematical equation in clear natural language. "
            "Avoid extra commentary; just describe what the equation is saying.\n\n"
            f"Equation: {raw}"
        )
        explanation = self.llm.chat(
            prompt,
            model=self.llm.equation_model,
            query=raw,
            domain_context=f"Equation: {raw}",
            require_context=False,
        )
        eq.natural_language = explanation
        return explanation

