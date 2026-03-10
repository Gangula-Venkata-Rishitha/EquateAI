"""SQLAlchemy models for EquateAI."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship

from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(512), nullable=False)
    path = Column(String(1024), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(64), default="uploaded")  # uploaded, processing, processed, error
    page_count = Column(Integer, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)


class Equation(Base):
    __tablename__ = "equations"

    equation_id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=False)
    page = Column(Integer, nullable=True)
    line_no = Column(Integer, nullable=True)
    raw_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    ast_json = Column(JSON, nullable=True)
    variables_json = Column(JSON, nullable=True)  # list of variable names
    equation_type = Column(String(64), nullable=True)  # ALGEBRAIC, DIFFERENTIAL, LOGIC, etc.
    natural_language = Column(Text, nullable=True)

    document = relationship("Document", backref="equations")


class Variable(Base):
    __tablename__ = "variables"

    variable_id = Column(Integer, primary_key=True, index=True)
    equation_id = Column(Integer, ForeignKey("equations.equation_id"), nullable=False)
    name = Column(String(256), nullable=False)
    type_ = Column("type", String(64), nullable=True)  # defined, used, undefined

    equation = relationship("Equation", backref="variables")


class Dependency(Base):
    __tablename__ = "dependencies"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=False)
    source_variable = Column(String(256), nullable=False)
    target_variable = Column(String(256), nullable=False)
    equation_id = Column(Integer, ForeignKey("equations.equation_id"), nullable=True)

    document = relationship("Document", backref="dependencies")


class Conflict(Base):
    __tablename__ = "conflicts"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=False)
    variable = Column(String(256), nullable=False)
    conflict_type = Column(String(64), nullable=False)  # MULTIPLE_DEFINITION, SYMBOLIC_CONFLICT, etc.
    equation_ids = Column(JSON, nullable=False)  # list of equation IDs involved in the conflict
    explanation = Column(Text, nullable=True)

    document = relationship("Document", backref="conflicts")


class MissingVariable(Base):
    __tablename__ = "missing_variables"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=False)
    name = Column(String(256), nullable=False)

    document = relationship("Document", backref="missing_variables")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(256), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=True)
    role = Column(String(32), nullable=False)  # user, assistant
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", backref="chat_history")
