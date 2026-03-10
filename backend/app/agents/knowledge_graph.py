"""Knowledge Graph Builder - creates semantic triples (subject, predicate, object)."""
from app.agents.base import SemanticEquation


class KnowledgeGraphBuilder:
    """Build scientific knowledge graph triples from equations."""

    def build(self, equations: list[SemanticEquation]) -> list[tuple[str, str, str]]:
        """Return list of (subject, predicate, object) triples."""
        triples: list[tuple[str, str, str]] = []
        for idx, eq in enumerate(equations):
            eq_id = f"Equation_{idx + 1}"
            for defined in eq.defined_vars:
                triples.append((eq_id, "defines", defined))
            for used in eq.used_vars:
                for defined in eq.defined_vars:
                    triples.append((defined, "depends_on", used))
        return triples

    def to_frontend_format(self, triples: list[tuple[str, str, str]]) -> dict:
        """Convert to nodes and edges for visualization."""
        nodes_set = set()
        edges = []
        for s, p, o in triples:
            nodes_set.add((s, "equation" if s.startswith("Equation_") else "variable"))
            nodes_set.add((o, "variable"))
            edges.append({"source": s, "target": o, "type": p})
        nodes = [{"id": n, "label": n, "type": t} for n, t in nodes_set]
        return {"nodes": nodes, "edges": edges, "triples": [{"subject": s, "predicate": p, "object": o} for s, p, o in triples]}
