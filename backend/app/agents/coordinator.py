"""Processing Coordinator - orchestrates the full document-to-graph pipeline."""
from pathlib import Path
from typing import Any

from app.agents.base import TextLine, EquationCandidate, ParsedEquation, SemanticEquation
from app.agents.document_reader import DocumentReaderAgent
from app.agents.preprocessing import PreprocessingAgent
from app.agents.equation_detection import EquationDetectionAgent
from app.agents.lexer import LexerAgent
from app.agents.parser import ParserAgent
from app.agents.semantic import SemanticAnalyzerAgent
from app.agents.conflict import ConflictDetectorAgent
from app.agents.dependency import DependencyAgent
from app.agents.graph_builder import GraphBuilderAgent
from app.agents.knowledge_graph import KnowledgeGraphBuilder
from app.agents.reasoning import ReasoningAgent


class ProcessingCoordinator:
    """Runs the full pipeline: read → preprocess → detect → parse → semantic → dependency → graphs."""

    def __init__(self):
        self.reader = DocumentReaderAgent()
        self.preprocessor = PreprocessingAgent()
        self.detector = EquationDetectionAgent()
        self.lexer = LexerAgent()
        self.parser = ParserAgent()
        self.semantic = SemanticAnalyzerAgent()
        self.conflict = ConflictDetectorAgent()
        self.dependency = DependencyAgent()
        self.graph_builder = GraphBuilderAgent()
        self.knowledge_builder = KnowledgeGraphBuilder()

    def process_document(self, file_path: Path) -> dict[str, Any]:
        """
        Run full pipeline. Returns dict with:
        - text_lines, equation_candidates, parsed_equations, semantic_equations,
        - conflicts, dependency_edges, dependency_graph (NetworkX), dependency_graph_json,
        - knowledge_triples, knowledge_graph_json
        """
        # 1. Read
        lines: list[TextLine] = self.reader.read(file_path)
        # 2. Preprocess
        lines = self.preprocessor.process(lines)
        # 3. Detect equations
        candidates: list[EquationCandidate] = self.detector.detect(lines)
        # 4. Parse each candidate
        parsed: list[ParsedEquation] = []
        for c in candidates:
            p = self.parser.parse(c)
            parsed.append(p)
        # 5. Semantic analysis (with cumulative defined set)
        defined_so_far: set[str] = set()
        semantic_eqs: list[SemanticEquation] = []
        for p in parsed:
            sem = self.semantic.analyze(p, defined_so_far)
            semantic_eqs.append(sem)
            defined_so_far |= set(sem.defined_vars)
        # 6. Conflicts
        conflicts = self.conflict.detect(semantic_eqs)
        # 7. Dependencies
        dep_edges = self.dependency.analyze(semantic_eqs)
        # 8. Dependency graph
        G = self.graph_builder.build(semantic_eqs, dep_edges)
        dep_json = self.graph_builder.to_frontend_format(G)
        # 9. Knowledge graph
        triples = self.knowledge_builder.build(semantic_eqs)
        kg_json = self.knowledge_builder.to_frontend_format(triples)

        return {
            "text_lines": [(l.content, l.page, l.line_no) for l in lines],
            "equation_candidates": [
                {"raw_text": c.raw_text, "page": c.page, "line_no": c.line_no, "confidence": c.confidence}
                for c in candidates
            ],
            "parsed_equations": parsed,
            "semantic_equations": semantic_eqs,
            "conflicts": [{"variable": v, "equation_indices": ids} for v, ids in conflicts],
            "dependency_edges": [{"source": s, "target": t, "equation_index": i} for s, t, i in dep_edges],
            "dependency_graph": G,
            "dependency_graph_json": dep_json,
            "knowledge_triples": triples,
            "knowledge_graph_json": kg_json,
        }
