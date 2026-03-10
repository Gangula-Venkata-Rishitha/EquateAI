"""Graph-related Pydantic schemas."""
from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # variable, equation


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str  # depends_on, defines


class DependencyGraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class KnowledgeTriple(BaseModel):
    subject: str
    predicate: str
    object: str


class KnowledgeGraphResponse(BaseModel):
    triples: list[KnowledgeTriple]
    nodes: list[GraphNode]
    edges: list[GraphEdge]
