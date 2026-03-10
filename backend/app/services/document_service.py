"""Document processing service - orchestrates pipeline and persistence."""
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.db import models
from app.agents.coordinator import ProcessingCoordinator
from app.agents.base import SemanticEquation, ParsedEquation
from app.utils.ast_serialize import ast_to_dict
from app.services.conflict_detection import ConflictDetectionService
from app.services.equation_classifier import EquationClassifier
from app.services.semantic_analysis import SemanticAnalysisService


class DocumentService:
    """Process documents and persist equations, variables, dependencies."""

    def __init__(self, db: Session):
        self.db = db
        self.coordinator = ProcessingCoordinator()

    def process_document(self, document_id: int, file_path: Path) -> dict[str, Any]:
        """Run full pipeline and save results to DB."""
        doc = self.db.query(models.Document).filter(models.Document.document_id == document_id).first()
        if not doc:
            raise ValueError("Document not found")
        doc.status = "processing"
        self.db.commit()

        try:
            result = self.coordinator.process_document(file_path)
        except Exception as e:
            doc.status = "error"
            self.db.commit()
            raise

        semantic_eqs: list[SemanticEquation] = result["semantic_equations"]
        parsed_list: list[ParsedEquation] = result["parsed_equations"]

        classifier = EquationClassifier()

        for idx, (sem, parsed) in enumerate(zip(semantic_eqs, parsed_list)):
            eq_row = models.Equation(
                document_id=document_id,
                page=parsed.page,
                line_no=parsed.line_no,
                raw_text=parsed.raw_text,
                confidence_score=parsed.confidence,
                ast_json=ast_to_dict(parsed.ast),
                variables_json=[v.name for v in sem.variables],
            )
            # classify equation type
            classifier.apply_to_equation(eq_row)
            self.db.add(eq_row)
            self.db.flush()
            for v in sem.variables:
                self.db.add(models.Variable(equation_id=eq_row.equation_id, name=v.name, type_=v.role))
            for dep in result["dependency_edges"]:
                if dep["equation_index"] == idx:
                    self.db.add(
                        models.Dependency(
                            document_id=document_id,
                            source_variable=dep["source"],
                            target_variable=dep["target"],
                            equation_id=eq_row.equation_id,
                        )
                    )

        # After equations and dependencies are stored, run higher-level analyses
        ConflictDetectionService(self.db).detect_for_document(document_id)
        SemanticAnalysisService(self.db).compute_missing_variables(document_id)

        doc.status = "processed"
        doc.page_count = len(set(l[1] for l in result["text_lines"])) if result["text_lines"] else None
        self.db.commit()

        result["document_id"] = document_id
        return result

    def get_dependency_graph_json(self, document_id: int) -> dict | None:
        """Get dependency graph from DB as frontend-ready JSON. Rebuilds from stored equations."""
        eqs = (
            self.db.query(models.Equation)
            .filter(models.Equation.document_id == document_id)
            .order_by(models.Equation.equation_id)
            .all()
        )
        if not eqs:
            return None
        deps = (
            self.db.query(models.Dependency)
            .filter(models.Dependency.document_id == document_id)
            .all()
        )
        vars_rows = (
            self.db.query(models.Variable)
            .join(models.Equation, models.Variable.equation_id == models.Equation.equation_id)
            .filter(models.Equation.document_id == document_id)
            .all()
        )
        defined_by_eq: dict[int, list[str]] = {}
        for v in vars_rows:
            if v.type_ == "defined":
                defined_by_eq.setdefault(v.equation_id, []).append(v.name)

        nodes: list[dict] = []
        seen: set[str] = set()
        for eq in eqs:
            eq_node_id = f"eq_{eq.equation_id}"
            if eq_node_id not in seen:
                nodes.append(
                    {
                        "id": eq_node_id,
                        "label": eq.raw_text[:80],
                        "type": "equation",
                    }
                )
                seen.add(eq_node_id)
            for v_name in eq.variables_json or []:
                if v_name not in seen:
                    nodes.append({"id": v_name, "label": v_name, "type": "variable"})
                    seen.add(v_name)

        edges: list[dict] = []
        # Variable-to-variable dependencies
        for d in deps:
            edges.append(
                {
                    "source": d.source_variable,
                    "target": d.target_variable,
                    "type": "depends_on",
                }
            )
        # Equation defines variable edges and equation depends_on variable edges
        for eq in eqs:
            eq_node_id = f"eq_{eq.equation_id}"
            defined_vars = set(defined_by_eq.get(eq.equation_id, []))
            # edges for defined variables
            for v_name in defined_vars:
                edges.append(
                    {
                        "source": eq_node_id,
                        "target": v_name,
                        "type": "defines",
                    }
                )
            # edges for variables this equation uses (inputs) – all variables minus those it defines
            for v_name in (eq.variables_json or []):
                if v_name in defined_vars:
                    continue
                edges.append(
                    {
                        "source": eq_node_id,
                        "target": v_name,
                        "type": "depends_on",
                    }
                )
        return {"nodes": nodes, "edges": edges}

    def get_knowledge_graph_json(self, document_id: int) -> dict:
        """Build knowledge graph triples from stored equations and dependencies."""
        eqs = self.db.query(models.Equation).filter(models.Equation.document_id == document_id).all()
        deps = self.db.query(models.Dependency).filter(models.Dependency.document_id == document_id).all()
        triples = []
        for eq in eqs:
            eq_id = f"Equation_{eq.equation_id}"
            for v in eq.variables_json or []:
                triples.append({"subject": eq_id, "predicate": "defines", "object": v})
        for d in deps:
            triples.append({"subject": d.source_variable, "predicate": "depends_on", "object": d.target_variable})
        nodes_set = set()
        for t in triples:
            nodes_set.add((t["subject"], "equation" if t["subject"].startswith("Equation_") else "variable"))
            nodes_set.add((t["object"], "variable"))
        nodes = [{"id": n, "label": n, "type": t} for n, t in nodes_set]
        edges = [{"source": t["subject"], "target": t["object"], "type": t["predicate"]} for t in triples]
        return {"nodes": nodes, "edges": edges, "triples": triples}
