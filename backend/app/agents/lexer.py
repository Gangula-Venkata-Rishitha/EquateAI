"""Lexical Analysis Agent - tokenizes equation strings."""
import re
from app.agents.base import Token


# Token types
VAR = "VAR"
NUMBER = "NUMBER"
OP = "OP"
EQUAL = "EQUAL"
LPAREN = "LPAREN"
RPAREN = "RPAREN"
FUNC = "FUNC"
COMMA = "COMMA"
SUBSCRIPT = "SUBSCRIPT"

OPERATORS = {"+", "-", "*", "/", "^", "**"}
FUNCTIONS = {"sin", "cos", "tan", "log", "exp", "sqrt", "sum", "integral", "lim", "ln"}


class LexerAgent:
    """Tokenize mathematical equation strings."""

    def tokenize(self, equation: str) -> list[Token]:
        """Return list of tokens for the equation string."""
        equation = equation.strip()
        tokens: list[Token] = []
        i = 0
        n = len(equation)
        pos = 0

        while i < n:
            c = equation[i]
            # Skip whitespace
            if c.isspace():
                i += 1
                continue
            # Number
            if c.isdigit() or (c == "." and i + 1 < n and equation[i + 1].isdigit()):
                start = i
                while i < n and (equation[i].isdigit() or equation[i] == "."):
                    i += 1
                tokens.append(Token(NUMBER, equation[start:i], pos))
                pos += 1
                continue
            # Identifier or function
            if c.isalpha() or c == "_":
                start = i
                while i < n and (equation[i].isalnum() or equation[i] == "_"):
                    i += 1
                word = equation[start:i]
                if word.lower() in FUNCTIONS:
                    tokens.append(Token(FUNC, word, pos))
                else:
                    tokens.append(Token(VAR, word, pos))
                pos += 1
                continue
            # Operators and symbols
            if c == "=":
                tokens.append(Token(EQUAL, "=", pos))
                pos += 1
                i += 1
                continue
            if c == "(":
                tokens.append(Token(LPAREN, "(", pos))
                pos += 1
                i += 1
                continue
            if c == ")":
                tokens.append(Token(RPAREN, ")", pos))
                pos += 1
                i += 1
                continue
            if c == ",":
                tokens.append(Token(COMMA, ",", pos))
                pos += 1
                i += 1
                continue
            # ** or *
            if c == "*" and i + 1 < n and equation[i + 1] == "*":
                tokens.append(Token(OP, "**", pos))
                pos += 1
                i += 2
                continue
            if c in OPERATORS:
                tokens.append(Token(OP, c, pos))
                pos += 1
                i += 1
                continue
            # Unknown: skip or treat as VAR for single chars
            i += 1

        return tokens
