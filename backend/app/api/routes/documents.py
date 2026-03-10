"""Document upload and processing API."""
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db import get_db, models
from app.schemas import DocumentResponse, DocumentSummary
from app.services import DocumentService, ConflictDetectionService, SemanticAnalysisService
from app.core.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a PDF or DOCX document. Returns document_id."""
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".pdf", ".docx"):
        raise HTTPException(400, "Only PDF and DOCX are supported")
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / file.filename
    content = file.file.read()
    with open(path, "wb") as f:
        f.write(content)
    doc = models.Document(filename=file.filename, path=str(path), status="uploaded")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.post("/{document_id}/process")
def process_document(
    document_id: int,
  db: Session = Depends(get_db),
):
    """Run full pipeline: extract, preprocess, detect equations, parse, build graphs."""
    doc = db.query(models.Document).filter(models.Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    path = Path(doc.path)
    if not path.exists():
        raise HTTPException(404, "File not found on disk")
    service = DocumentService(db)
    try:
        result = service.process_document(document_id, path)
    except Exception as e:
        raise HTTPException(500, str(e))
    return {
        "document_id": document_id,
        "status": "processed",
        "equation_count": len(result.get("semantic_equations", [])),
        "conflicts": result.get("conflicts", []),
    }


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents."""
    docs = db.query(models.Document).order_by(models.Document.uploaded_at.desc()).all()
    return docs


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.get("/{document_id}/summary", response_model=DocumentSummary)
def get_document_summary(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    eq_count = db.query(models.Equation).filter(models.Equation.document_id == document_id).count()
    undefined = 0
    for eq in db.query(models.Equation).filter(models.Equation.document_id == document_id):
        for v in db.query(models.Variable).filter(models.Variable.equation_id == eq.equation_id, models.Variable.type_ == "undefined"):
            undefined += 1
    return DocumentSummary(
        document_id=doc.document_id,
        filename=doc.filename,
        page_count=doc.page_count,
        equation_count=eq_count,
        undefined_variables_count=undefined,
        status=doc.status,
    )


@router.get("/{document_id}/equations")
def get_equations(document_id: int, db: Session = Depends(get_db)):
    eqs = db.query(models.Equation).filter(models.Equation.document_id == document_id).order_by(models.Equation.equation_id).all()
    return [
        {
            "equation_id": e.equation_id,
            "document_id": e.document_id,
            "page": e.page,
            "line_no": e.line_no,
            "raw_text": e.raw_text,
            "confidence_score": e.confidence_score,
            "variables": e.variables_json,
            "ast_json": e.ast_json,
        }
        for e in eqs
    ]


@router.get("/{document_id}/dependency-graph")
def get_dependency_graph(document_id: int, db: Session = Depends(get_db)):
    service = DocumentService(db)
    data = service.get_dependency_graph_json(document_id)
    if data is None:
        return {"nodes": [], "edges": []}
    return data


@router.get("/{document_id}/knowledge-graph")
def get_knowledge_graph(document_id: int, db: Session = Depends(get_db)):
    service = DocumentService(db)
    return service.get_knowledge_graph_json(document_id)


@router.get("/{document_id}/conflicts")
def get_conflicts(document_id: int, db: Session = Depends(get_db)):
    """Return detected equation conflicts for the document."""
    doc = db.query(models.Document).filter(models.Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    # Conflicts are computed when the document is processed; just read them.
    conflicts = (
        db.query(models.Conflict)
        .filter(models.Conflict.document_id == document_id)
        .order_by(models.Conflict.id)
        .all()
    )
    return [
        {
            "id": c.id,
            "variable": c.variable,
            "conflict_type": c.conflict_type,
            "equation_ids": c.equation_ids,
            "explanation": c.explanation,
        }
        for c in conflicts
    ]


@router.get("/{document_id}/missing-variables")
def get_missing_variables(document_id: int, db: Session = Depends(get_db)):
    """Return variables that are used but never defined."""
    doc = db.query(models.Document).filter(models.Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    svc = SemanticAnalysisService(db)
    mvs = svc.compute_missing_variables(document_id)
    return [{"name": m.name} for m in mvs]


@router.get("/{document_id}/dependency-issues")
def get_dependency_issues(document_id: int, db: Session = Depends(get_db)):
    """Return dependency issues such as circular dependencies."""
    doc = db.query(models.Document).filter(models.Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    svc = SemanticAnalysisService(db)
    cycles = svc.dependency_cycles(document_id)
    return {"cycles": cycles}


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and all associated derived data."""
    doc = db.query(models.Document).filter(models.Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    # Delete rows that depend on this document
    # Equations first to cascade to variables/dependencies by explicit deletes
    eq_ids = [
        e.equation_id
        for e in db.query(models.Equation).filter(models.Equation.document_id == document_id).all()
    ]
    if eq_ids:
        db.query(models.Variable).filter(models.Variable.equation_id.in_(eq_ids)).delete(
            synchronize_session=False
        )
        db.query(models.Dependency).filter(models.Dependency.document_id == document_id).delete(
            synchronize_session=False
        )
        db.query(models.Equation).filter(models.Equation.document_id == document_id).delete(
            synchronize_session=False
        )

    db.query(models.Conflict).filter(models.Conflict.document_id == document_id).delete(
        synchronize_session=False
    )
    db.query(models.MissingVariable).filter(
        models.MissingVariable.document_id == document_id
    ).delete(synchronize_session=False)
    db.query(models.ChatHistory).filter(
        models.ChatHistory.document_id == document_id
    ).delete(synchronize_session=False)

    db.delete(doc)
    db.commit()
    return {"status": "deleted"}
