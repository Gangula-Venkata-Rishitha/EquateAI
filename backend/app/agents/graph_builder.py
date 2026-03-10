"""Dependency Graph Agent - builds NetworkX graph for visualization."""
from typing import Any
import networkx as nx

from app.agents.base import SemanticEquation


class GraphBuilderAgent:
    """Build NetworkX graph from dependency analysis. Nodes: variables + equations; edges: depends_on, defines."""

    def build(
        self,
        equations: list[SemanticEquation],
        dependency_edges: list[tuple[str, str, int]],
    ) -> nx.DiGraph:
        """Build directed graph. Node ids: var names and eq_0, eq_1, ..."""
        G = nx.DiGraph()
        for idx, eq in enumerate(equations):
            node_id = f"eq_{idx}"
            G.add_node(node_id, label=eq.parsed.raw_text[:50], type="equation")
            if eq.defined_vars:
                for v in eq.defined_vars:
                    if not G.has_node(v):
                        G.add_node(v, label=v, type="variable")
                    G.add_edge(node_id, v, type="defines")
            for source, target, eq_idx in dependency_edges:
                if eq_idx == idx:
                    if not G.has_node(target):
                        G.add_node(target, label=target, type="variable")
                    G.add_edge(source, target, type="depends_on")
        return G

    def to_frontend_format(self, G: nx.DiGraph) -> dict[str, Any]:
        """Convert to nodes/edges lists for React Flow / Cytoscape."""
        nodes = []
        for nid, attrs in G.nodes(data=True):
            nodes.append({
                "id": nid,
                "label": attrs.get("label", nid),
                "type": attrs.get("type", "variable"),
            })
        edges = []
        for u, v, attrs in G.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "type": attrs.get("type", "depends_on"),
            })
        return {"nodes": nodes, "edges": edges}
