"""Conflict Detection Agent - detects multiple definitions of same variable."""
from app.agents.base import SemanticEquation


class ConflictDetectorAgent:
    """Detect when the same variable is defined by multiple equations."""

    def detect(self, equations: list[SemanticEquation]) -> list[tuple[str, list[int]]]:
        """
        Return list of (variable_name, [equation_indices]) for variables
        that are defined in more than one equation.
        """
        defined_in: dict[str, list[int]] = {}
        for idx, eq in enumerate(equations):
            for v in eq.defined_vars:
                defined_in.setdefault(v, []).append(idx)
        conflicts: list[tuple[str, list[int]]] = []
        for var, indices in defined_in.items():
            if len(indices) > 1:
                conflicts.append((var, indices))
        return conflicts
