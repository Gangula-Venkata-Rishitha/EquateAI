"""Database connection and session management."""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.core.config import settings

_db_url = settings.database_url
if _db_url.startswith("sqlite:///"):
    db_path = Path(_db_url.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)

connect_args = {}
if "sqlite" in _db_url:
    # Use autocommit mode for SQLite to avoid rollback errors when no transaction is active.
    connect_args["check_same_thread"] = False
    connect_args["isolation_level"] = None

engine = create_engine(
    _db_url,
    connect_args=connect_args,
    poolclass=StaticPool if "sqlite" in _db_url else None,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
