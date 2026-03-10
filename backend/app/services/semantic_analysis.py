"""Semantic reasoning helpers: missing variables, circular dependencies."""
from __future__ import annotations

from typing import Any

import networkx as nx
from sqlalchemy.orm import Session

from app.db import models


class SemanticAnalysisService:
    """Higher-level semantic checks: missing vars, circular dependencies."""

    def __init__(self, db: Session):
        self.db = db

    def compute_missing_variables(self, document_id: int) -> list[models.MissingVariable]:
        """Find variables that are used but never defined in any equation of this document."""
        # Clear existing rows
        self.db.query(models.MissingVariable).filter(
            models.MissingVariable.document_id == document_id
        ).delete()

        vars_rows = (
            self.db.query(models.Variable)
            .join(models.Equation, models.Variable.equation_id == models.Equation.equation_id)
            .filter(models.Equation.document_id == document_id)
            .all()
        )
        defined = {v.name for v in vars_rows if v.type_ == "defined"}
        used = {v.name for v in vars_rows if v.type_ in {"used", "undefined"}}
        missing = sorted(used - defined)

        result: list[models.MissingVariable] = []
        for name in missing:
            mv = models.MissingVariable(document_id=document_id, name=name)
            self.db.add(mv)
            result.append(mv)
        self.db.commit()
        return result

    def dependency_cycles(self, document_id: int) -> list[list[str]]:
        """Return cycles in dependency graph as lists of variable names."""
        deps = (
            self.db.query(models.Dependency)
            .filter(models.Dependency.document_id == document_id)
            .all()
        )
        G = nx.DiGraph()
        for d in deps:
            G.add_edge(d.source_variable, d.target_variable)
        cycles = list(nx.simple_cycles(G))
        # Represent each cycle as list of node names
        return [list(c) for c in cycles]

