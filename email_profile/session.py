"""SQLAlchemy session factory."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def make_session(url: str) -> tuple[Engine, sessionmaker]:
    """Create a SQLAlchemy engine and session factory bound to ``url``."""
    engine = create_engine(url=url, future=True)
    factory = sessionmaker(
        bind=engine, autocommit=False, autoflush=False, future=True
    )
    return engine, factory
