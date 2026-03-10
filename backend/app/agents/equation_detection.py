"""Equation Detection Agent - detects equation-like expressions with confidence scoring."""
import re
from app.agents.base import TextLine, EquationCandidate


# Operators and symbols that suggest an equation
EQUATION_INDICATORS = set("=+-*/^∑∫∀∃→←")
FUNCTION_NAMES = {"sin", "cos", "tan", "log", "exp", "sqrt", "sum", "integral", "lim", "max", "min"}


class EquationDetectionAgent:
    """Detect equation candidates using heuristics and confidence scoring."""

    def detect(self, lines: list[TextLine]) -> list[EquationCandidate]:
        """Return equation candidates with confidence scores."""
        candidates: list[EquationCandidate] = []
        for line in lines:
            score = self._score(line.content)
            if score > 0.3:
                candidates.append(
                    EquationCandidate(
                        raw_text=line.content,
                        page=line.page,
                        line_no=line.line_no,
                        confidence=min(1.0, score),
                    )
                )
        return candidates

    def _score(self, text: str) -> float:
        """Compute confidence that the line is an equation (0..1)."""
        if not text or len(text) > 500:
            return 0.0
        score = 0.0
        # Contains equals (strong signal)
        if "=" in text:
            score += 0.4
            # Single equals is better than multiple for definition
            eq_count = text.count("=")
            if eq_count == 1:
                score += 0.1
        # Contains operators
        for op in "+-*/^":
            if op in text:
                score += 0.05
                break
        # Contains math symbols
        for sym in EQUATION_INDICATORS:
            if sym in text:
                score += 0.03
                break
        # Contains function names
        words = re.findall(r"[a-zA-Z_]+", text)
        for w in words:
            if w.lower() in FUNCTION_NAMES:
                score += 0.1
                break
        # Looks like variable = expression (e.g. F = m * a)
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*=", text):
            score += 0.2
        # Contains numbers
        if re.search(r"\d", text):
            score += 0.05
        return score
