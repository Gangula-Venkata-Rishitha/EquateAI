"""Text Preprocessing Agent - normalizes extracted text for equation detection."""
import re
from app.agents.base import TextLine


# Unicode replacements for math symbols
REPLACEMENTS = [
    ("×", "*"),
    ("÷", "/"),
    ("−", "-"),
    ("–", "-"),
    ("—", "-"),
    ("≤", "<="),
    ("≥", ">="),
    ("≠", "!="),
    ("≈", "~="),
    ("∑", "sum"),
    ("∫", "integral"),
    ("√", "sqrt"),
    ("∂", "d"),
    ("π", "pi"),
    ("∞", "inf"),
    ("∀", "forall"),
    ("∃", "exists"),
    ("→", "->"),
    ("←", "<-"),
    ("↔", "<->"),
]

# Normalize function names
FUNC_NORMALIZE = [
    (r"\bln\b", "log"),
    (r"\blog\s*(\d+)\s*", r"log\1 "),  # log base
]


class PreprocessingAgent:
    """Normalize text: replace Unicode math symbols, remove noise."""

    def __init__(self):
        self._noise_patterns = [
            re.compile(r"^\s*\d+\s*$"),  # page number only
            re.compile(r"^[-–—]\s*\d+\s*$"),
            re.compile(r"^\s*$"),
            re.compile(r"^(header|footer|page)\s*\d*$", re.I),
        ]

    def process(self, lines: list[TextLine]) -> list[TextLine]:
        """Normalize each line and filter out noise."""
        result: list[TextLine] = []
        for line in lines:
            content = self._normalize(line.content)
            if not content or self._is_noise(content):
                continue
            result.append(TextLine(content=content, page=line.page, line_no=line.line_no))
        return result

    def _normalize(self, text: str) -> str:
        """Replace Unicode symbols and normalize function names."""
        out = text
        for old, new in REPLACEMENTS:
            out = out.replace(old, new)
        for pattern, repl in FUNC_NORMALIZE:
            out = re.sub(pattern, repl, out)
        # Collapse whitespace
        out = " ".join(out.split())
        return out.strip()

    def _is_noise(self, text: str) -> bool:
        """Return True if line looks like header/footer/page number."""
        for pat in self._noise_patterns:
            if pat.match(text):
                return True
        return False
