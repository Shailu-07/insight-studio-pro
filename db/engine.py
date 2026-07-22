"""Database engine and session management.

Uses SQLAlchemy against MySQL. Both the target database and all tables are
created automatically on first run via `init_db()` — no manual migration
step required.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from config import settings
from core.exceptions import DatabaseConnectionError

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.mysql_url,
            pool_pre_ping=True,
            pool_recycle=1800,
            echo=False,
        )
    return _engine


def get_session_factory() -> sessionmaker:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, expire_on_commit=False)
    return _SessionLocal


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _ensure_database_exists() -> None:
    """Create the target MySQL schema if it doesn't already exist."""
    server_engine = create_engine(settings.mysql_server_url, pool_pre_ping=True)
    try:
        with server_engine.connect() as conn:
            conn.exec_driver_sql(
                f"CREATE DATABASE IF NOT EXISTS `{settings.mysql_database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        server_engine.dispose()


def init_db() -> None:
    """Create the database (if needed) and all tables. Safe to call every run."""
    from db import models  # local import avoids circular imports

    try:
        _ensure_database_exists()
        models.Base.metadata.create_all(bind=get_engine())
    except OperationalError as exc:
        raise DatabaseConnectionError(
            "Could not connect to MySQL. Check MYSQL_HOST, MYSQL_PORT, "
            f"MYSQL_USER, MYSQL_PASSWORD and MYSQL_DATABASE in your .env file. "
            f"Original error: {exc}"
        ) from exc


def check_connection() -> bool:
    try:
        with get_engine().connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return True
    except Exception:
        return False
