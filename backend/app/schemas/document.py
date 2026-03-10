"""Document-related Pydantic schemas."""
from datetime import datetime
from pydantic import BaseModel


class DocumentCreate(BaseModel):
    filename: str


class DocumentResponse(BaseModel):
    document_id: int
    filename: str
    path: str
    uploaded_at: datetime
    status: str
    page_count: int | None = None

    class Config:
        from_attributes = True


class DocumentSummary(BaseModel):
    document_id: int
    filename: str
    page_count: int | None
    equation_count: int
    undefined_variables_count: int
    status: str
