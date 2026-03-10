"""Base types for pipeline data structures."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TextLine:
    """A single line of text extracted from a document."""
    content: str
    page: int
    line_no: int


@dataclass
class EquationCandidate:
    """A detected equation candidate with confidence."""
    raw_text: str
    page: int
    line_no: int
    confidence: float


@dataclass
class Token:
    """Lexical token from equation."""
    type: str
    value: str
    position: int = 0


@dataclass
class ASTNode:
    """Node in Abstract Syntax Tree."""
    type: str
    value: str | None = None
    left: "ASTNode | None" = None
    right: "ASTNode | None" = None
    children: list["ASTNode"] = field(default_factory=list)


@dataclass
class ParsedEquation:
    """Fully parsed equation with AST and metadata."""
    raw_text: str
    page: int
    line_no: int
    confidence: float
    ast: ASTNode | None
    tokens: list[Token]
    lhs_var: str | None = None  # left-hand side variable if assignment
    syntax_errors: list[str] = field(default_factory=list)


@dataclass
class VariableInfo:
    """Variable usage in an equation."""
    name: str
    role: str  # defined, used, undefined


@dataclass
class SemanticEquation:
    """Equation with semantic analysis."""
    parsed: ParsedEquation
    variables: list[VariableInfo]
    defined_vars: list[str] = field(default_factory=list)
    used_vars: list[str] = field(default_factory=list)
    undefined_vars: list[str] = field(default_factory=list)
