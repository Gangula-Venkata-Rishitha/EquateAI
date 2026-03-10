"""Symbolic Reasoning Engine - uses SymPy for simplify, solve, differentiate, integrate."""
from typing import Any
from sympy import sympify, solve, diff, integrate, simplify, Symbol, Eq
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication


class ReasoningAgent:
    """Symbolic math via SymPy: simplify, solve, differentiate, integrate."""

    def _parse_safe(self, expr_str: str):
        """Safely parse expression string to SymPy."""
        try:
            transformations = standard_transformations + (implicit_multiplication,)
            return parse_expr(expr_str, transformations=transformations)
        except Exception:
            return sympify(expr_str)

    def simplify_expression(self, expr_str: str) -> dict[str, Any]:
        """Simplify expression. Returns {success, result_str, error}."""
        try:
            expr = self._parse_safe(expr_str)
            result = simplify(expr)
            return {"success": True, "result": str(result), "error": None}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def solve_for(self, equation_str: str, variable: str) -> dict[str, Any]:
        """Solve equation for variable. equation_str like 'F - m*a' or 'F = m*a'."""
        try:
            eq_clean = equation_str.replace("=", "-")
            expr = self._parse_safe(eq_clean)
            sym = Symbol(variable)
            solutions = solve(expr, sym)
            if not solutions:
                return {"success": False, "solutions": [], "error": "No solution found"}
            return {"success": True, "solutions": [str(s) for s in solutions], "error": None}
        except Exception as e:
            return {"success": False, "solutions": [], "error": str(e)}

    def differentiate(self, expr_str: str, variable: str) -> dict[str, Any]:
        """Differentiate expression with respect to variable."""
        try:
            expr = self._parse_safe(expr_str)
            sym = Symbol(variable)
            result = diff(expr, sym)
            return {"success": True, "result": str(result), "error": None}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}

    def integrate_expr(self, expr_str: str, variable: str) -> dict[str, Any]:
        """Integrate expression with respect to variable."""
        try:
            expr = self._parse_safe(expr_str)
            sym = Symbol(variable)
            result = integrate(expr, sym)
            return {"success": True, "result": str(result), "error": None}
        except Exception as e:
            return {"success": False, "result": None, "error": str(e)}
