"""Dependency Analysis Agent - builds variable dependency relationships."""
from app.agents.base import SemanticEquation


class DependencyAgent:
    """Build dependency graph: for each equation, LHS depends on RHS variables."""

    def analyze(self, equations: list[SemanticEquation]) -> list[tuple[str, str, int]]:
        """
        Return list of (source_variable, target_variable, equation_index).
        source_variable is defined by the equation and depends on target_variable.
        """
        edges: list[tuple[str, str, int]] = []
        for idx, eq in enumerate(equations):
            for defined in eq.defined_vars:
                for used in eq.used_vars:
                    edges.append((defined, used, idx))
        return edges
