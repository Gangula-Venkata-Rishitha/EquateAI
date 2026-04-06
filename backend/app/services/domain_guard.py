"""Domain guard for restricting LLM answers to EquateAI scope."""
from __future__ import annotations

import re
from dataclasses import dataclass


OUT_OF_SCOPE_MESSAGE = (
    "I can only answer questions related to the EquateAI document, equations, variables, and analysis."
)
INSUFFICIENT_CONTEXT_MESSAGE = "The requested information is not available in the EquateAI context."


STRICT_SYSTEM_PROMPT_TEMPLATE = """You are a restricted domain assistant for EquateAI.

Your scope is strictly limited to:
- uploaded document contents
- parsed equations
- variables and symbol definitions
- dependencies between equations and variables
- conflicts, inconsistencies, and missing variables
- equation explanations and scientific reasoning based only on the provided context

Rules:
1. Answer only if the question is related to the EquateAI project context.
2. If the question is unrelated, respond exactly with:
   'I can only answer questions related to the EquateAI document, equations, variables, and analysis.'
3. Do not answer general knowledge, politics, geography, entertainment, sports, weather, or casual questions.
4. Do not use external world knowledge unless directly needed to explain the provided document.
5. If the provided context is insufficient, say:
   'The requested information is not available in the EquateAI context.'
"""


ALLOWLIST_TERMS = {
    "equation",
    "formula",
    "variable",
    "symbol",
    "dependency",
    "graph",
    "knowledge graph",
    "scientific document",
    "parse",
    "parser",
    "ast",
    "expression",
    "conflict",
    "inconsistency",
    "undefined variable",
    "missing variable",
    "derivation",
    "explanation",
    "extracted content",
    "document summary",
    "equation reasoning",
    "document",
    "equateai",
}


OUT_OF_SCOPE_HINTS = {
    "population",
    "capital",
    "president",
    "prime minister",
    "weather",
    "sports",
    "movie",
    "song",
    "news",
    "politics",
    "cricket",
    "football",
    "stock",
    "bitcoin",
    "celebrity",
}


INTENT_PATTERNS: dict[str, tuple[str, ...]] = {
    "equation_explanation": ("equation", "formula", "explain", "means", "interpret"),
    "variable_analysis": ("variable", "symbol", "defined", "undefined", "value"),
    "dependency_analysis": ("dependency", "depends", "graph", "relation", "linked"),
    "conflict_analysis": ("conflict", "inconsistency", "contradiction", "mismatch"),
    "missing_variable_analysis": ("missing variable", "undefined variable", "not defined"),
    "document_summary": ("summary", "summarize", "document overview", "key points"),
    "scientific_reasoning_from_document": ("reason", "derive", "prove", "from document", "based on document"),
}


@dataclass
class DomainCheckResult:
    intent: str
    allowed: bool
    reason: str | None = None


class DomainGuard:
    """Deterministic query guard with conservative allow policy."""

    def classify_intent(self, query: str) -> str:
        q = (query or "").strip().lower()
        if not q:
            return "out_of_scope"
        if any(hint in q for hint in OUT_OF_SCOPE_HINTS):
            return "out_of_scope"

        for intent, patterns in INTENT_PATTERNS.items():
            if any(p in q for p in patterns):
                return intent

        # Equation-like strings are treated as in-domain.
        if self._looks_like_equation(q):
            return "equation_explanation"

        # Soft allowlist check for EquateAI-specific terms.
        if any(term in q for term in ALLOWLIST_TERMS):
            return "scientific_reasoning_from_document"

        # Conservative fallback: refuse if uncertain.
        return "out_of_scope"

    def check(self, query: str, context: str | None = None, require_context: bool = False) -> DomainCheckResult:
        intent = self.classify_intent(query)
        if intent == "out_of_scope":
            return DomainCheckResult(intent=intent, allowed=False, reason=OUT_OF_SCOPE_MESSAGE)

        if require_context and not self._has_relevant_context(query, context):
            return DomainCheckResult(intent=intent, allowed=False, reason=OUT_OF_SCOPE_MESSAGE)

        return DomainCheckResult(intent=intent, allowed=True, reason=None)

    def build_system_prompt(self, context: str | None = None) -> str:
        if context and context.strip():
            return f"{STRICT_SYSTEM_PROMPT_TEMPLATE}\n\nEquateAI context:\n{context.strip()}"
        return f"{STRICT_SYSTEM_PROMPT_TEMPLATE}\n\nEquateAI context: (none provided)"

    def _has_relevant_context(self, query: str, context: str | None) -> bool:
        if not context or not context.strip():
            return False

        q_tokens = set(re.findall(r"[a-zA-Z_]{3,}", query.lower()))
        c_tokens = set(re.findall(r"[a-zA-Z_]{3,}", context.lower()))
        if not c_tokens:
            return False

        # Strong context match for likely equation/document terms.
        overlap = q_tokens.intersection(c_tokens)
        if overlap:
            return True

        # If query is explicitly EquateAI analytical intent and context exists, allow.
        return any(term in query.lower() for term in ALLOWLIST_TERMS)

    def _looks_like_equation(self, text: str) -> bool:
        if "=" in text:
            return True
        return bool(re.search(r"[a-zA-Z]\s*[\+\-\*/\^]\s*[a-zA-Z0-9]", text))


if __name__ == "__main__":
    # Lightweight manual verification when no formal tests exist.
    guard = DomainGuard()
    samples = [
        ("Explain F = m * a", "Equation: F = m * a", False),
        ("Find missing variables in this document", "Document: paper.pdf\nEquations found: F = m*a", True),
        ("What is the population of India?", "Document: paper.pdf", True),
    ]
    for query, ctx, require_ctx in samples:
        result = guard.check(query=query, context=ctx, require_context=require_ctx)
        print({"query": query, "intent": result.intent, "allowed": result.allowed, "reason": result.reason})

