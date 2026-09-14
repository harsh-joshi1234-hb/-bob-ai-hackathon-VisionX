"""
database.py
-----------
SQLAlchemy engine, session factory, and declarative base for the
S1 Semiconductor AI backend.

Usage
-----
Import `SessionLocal` for a synchronous DB session in route handlers:

    from app.database import SessionLocal

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

Import `Base` in every ORM model module so that `Base.metadata.create_all`
and Alembic can discover all tables automatically.
"""

import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------------------------------------------------------------------
# Read DATABASE_URL from environment – no hard-coded credentials.
# The .env file (copied from .env.example) is loaded by the application
# entry-point (main.py) via python-dotenv before this module is imported.
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:changeme@localhost:5432/s1_wafer_db",
)

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# pool_pre_ping=True: issues a lightweight SELECT 1 before each connection
# checkout to detect and recycle stale connections transparently.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # Keep a small pool for a single-process FastAPI app; tune for production.
    pool_size=10,
    max_overflow=20,
    echo=os.environ.get("APP_ENV", "production") == "development",
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ---------------------------------------------------------------------------
# Declarative base
# All ORM models inherit from this.
# ---------------------------------------------------------------------------
Base = declarative_base()


# ---------------------------------------------------------------------------
# Dependency helper (for FastAPI route injection)
# ---------------------------------------------------------------------------
def get_db():
    """
    FastAPI dependency that yields a database session and guarantees it is
    closed even if an exception is raised inside the route handler.

    Example usage in a router::

        from fastapi import Depends
        from sqlalchemy.orm import Session
        from app.database import get_db

        @router.get("/lots")
        def list_lots(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Health-check helper
# ---------------------------------------------------------------------------
def check_db_connection() -> bool:
    """
    Execute a lightweight query to verify the database is reachable.
    Returns True on success, raises on failure.
    """
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
