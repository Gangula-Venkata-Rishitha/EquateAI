"""Syntax Parsing Agent - builds AST and detects syntax errors."""
from app.agents.base import Token, ASTNode, ParsedEquation, EquationCandidate


class ParseError(Exception):
    def __init__(self, message: str, position: int = 0):
        self.message = message
        self.position = position
        super().__init__(message)


class ParserAgent:
    """Parse token stream into AST. Validates structure and reports errors."""

    def __init__(self):
        self.tokens: list[Token] = []
        self.pos = 0
        self.errors: list[str] = []

    def parse(self, candidate: EquationCandidate) -> ParsedEquation:
        """Parse equation candidate into ParsedEquation with AST and errors."""
        from app.agents.lexer import LexerAgent
        lexer = LexerAgent()
        self.tokens = lexer.tokenize(candidate.raw_text)
        self.pos = 0
        self.errors = []

        ast = None
        lhs_var = None
        try:
            if self._peek() and self._peek().type == "VAR" and self._at_equals():
                # LHS variable (e.g. F in "F = m * a")
                lhs_var = self._peek().value
                self._advance()  # VAR
                if self._peek() and self._peek().type == "EQUAL":
                    self._advance()  # =
                    ast = self._parse_expression()
                else:
                    self.errors.append("Expected '=' after left-hand side variable")
            else:
                ast = self._parse_expression()
        except ParseError as e:
            self.errors.append(e.message)

        self._check_extra_tokens()
        return ParsedEquation(
            raw_text=candidate.raw_text,
            page=candidate.page,
            line_no=candidate.line_no,
            confidence=candidate.confidence,
            ast=ast,
            tokens=self.tokens,
            lhs_var=lhs_var,
            syntax_errors=self.errors,
        )

    def _peek(self) -> Token | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _advance(self) -> Token | None:
        if self.pos < len(self.tokens):
            t = self.tokens[self.pos]
            self.pos += 1
            return t
        return None

    def _at_equals(self) -> bool:
        """Check if next token after current is EQUAL (for VAR = expr)."""
        p = self.pos
        if p + 1 < len(self.tokens) and self.tokens[p].type == "VAR" and self.tokens[p + 1].type == "EQUAL":
            return True
        return False

    def _parse_expression(self) -> ASTNode:
        return self._parse_additive()

    def _parse_additive(self) -> ASTNode:
        left = self._parse_multiplicative()
        while self._peek() and self._peek().type == "OP" and self._peek().value in ("+", "-"):
            op = self._advance()
            right = self._parse_multiplicative()
            left = ASTNode(type="BINARY", value=op.value, left=left, right=right)
        return left

    def _parse_multiplicative(self) -> ASTNode:
        left = self._parse_power()
        while self._peek() and self._peek().type == "OP" and self._peek().value in ("*", "/"):
            op = self._advance()
            right = self._parse_power()
            left = ASTNode(type="BINARY", value=op.value, left=left, right=right)
        return left

    def _parse_power(self) -> ASTNode:
        left = self._parse_unary()
        if self._peek() and self._peek().type == "OP" and self._peek().value in ("^", "**"):
            op = self._advance()
            right = self._parse_power()
            return ASTNode(type="BINARY", value="**", left=left, right=right)
        return left

    def _parse_unary(self) -> ASTNode:
        if self._peek() and self._peek().type == "OP" and self._peek().value == "-":
            self._advance()
            child = self._parse_unary()
            return ASTNode(type="UNARY", value="-", left=child, right=None)
        return self._parse_primary()

    def _parse_primary(self) -> ASTNode:
        t = self._peek()
        if not t:
            raise ParseError("Unexpected end of expression", self.pos)
        if t.type == "NUMBER":
            self._advance()
            return ASTNode(type="NUMBER", value=t.value)
        if t.type == "VAR":
            self._advance()
            return ASTNode(type="VAR", value=t.value)
        if t.type == "FUNC":
            func = self._advance()
            if self._peek() and self._peek().type == "LPAREN":
                self._advance()
                arg = self._parse_expression()
                if self._peek() and self._peek().type == "RPAREN":
                    self._advance()
                else:
                    self.errors.append("Missing ')' after function argument")
                return ASTNode(type="CALL", value=func.value, left=arg, right=None)
            self.errors.append(f"Function {func.value} must be followed by '('")
            return ASTNode(type="CALL", value=func.value, left=None, right=None)
        if t.type == "LPAREN":
            self._advance()
            expr = self._parse_expression()
            if self._peek() and self._peek().type == "RPAREN":
                self._advance()
            else:
                self.errors.append("Unbalanced parentheses: missing ')'")
            return expr
        raise ParseError(f"Unexpected token: {t.type} '{t.value}'", self.pos)

    def _check_extra_tokens(self) -> None:
        if self._peek():
            self.errors.append("Extra tokens after expression")
