"""Detect conflicts between equations for a document."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session
from sympy import Eq, simplify
from sympy.parsing.sympy_parser import parse_expr

from app.db import models


class ConflictDetectionService:
    """Detect multiple definitions and symbolic conflicts between equations."""

    def __init__(self, db: Session):
        self.db = db

    def _parse_rhs(self, raw: str) -> Any | None:
        """Parse RHS of 'lhs = rhs' using SymPy. Returns expression or None."""
        if "=" not in raw:
            return None
        try:
            lhs, rhs = raw.split("=", 1)
            expr = parse_expr(rhs, evaluate=False)
            return expr
        except Exception:
            return None

    def detect_for_document(self, document_id: int) -> list[models.Conflict]:
        """Compute conflicts for a document and persist them."""
        equations = (
            self.db.query(models.Equation)
            .filter(models.Equation.document_id == document_id)
            .order_by(models.Equation.equation_id)
            .all()
        )
        if not equations:
            return []

        # Group equations by apparent LHS variable name (before '=')
        groups: dict[str, list[models.Equation]] = defaultdict(list)
        for e in equations:
            raw = e.raw_text or ""
            if "=" not in raw:
                continue
            lhs = raw.split("=", 1)[0].strip()
            if lhs:
                groups[lhs].append(e)

        # Clear existing conflicts for this document
        self.db.query(models.Conflict).filter(models.Conflict.document_id == document_id).delete()

        conflicts: list[models.Conflict] = []
        for var, eqs in groups.items():
            if len(eqs) < 2:
                continue
            # Multiple definitions of the same variable
            equation_ids = [e.equation_id for e in eqs]
            conflicts.append(
                models.Conflict(
                    document_id=document_id,
                    variable=var,
                    conflict_type="MULTIPLE_DEFINITION",
                    equation_ids=equation_ids,
                    explanation=f"Variable {var} is defined in {len(eqs)} equations.",
                )
            )

            # Try symbolic equivalence pairwise
            parsed = [(e, self._parse_rhs(e.raw_text or "")) for e in eqs]
            for i in range(len(parsed)):
                for j in range(i + 1, len(parsed)):
                    e1, expr1 = parsed[i]
                    e2, expr2 = parsed[j]
                    if expr1 is None or expr2 is None:
                        continue
                    try:
                        diff = simplify(expr1 - expr2)
                        if diff != 0:
                            conflicts.append(
                                models.Conflict(
                                    document_id=document_id,
                                    variable=var,
                                    conflict_type="SYMBOLIC_CONFLICT",
                                    equation_ids=[e1.equation_id, e2.equation_id],
                                    explanation=(
                                        f"Equations {e1.equation_id} and {e2.equation_id} "
                                        f"define {var} with incompatible expressions."
                                    ),
                                )
                            )
                    except Exception:
                        continue

        for c in conflicts:
            self.db.add(c)
        self.db.commit()
        return conflicts

