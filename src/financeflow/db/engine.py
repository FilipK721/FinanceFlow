"""
Database engine setup for FinanceFlow.

Resolves the SQLite file path the same way the old DataManager resolved
expenses.json (project_root/data/financeflow.db), creates the directory
if missing, and exposes a lazily-initialized session factory.

The engine is created on first use (not at import time) so that importing
this module — or anything that imports it, like test conftest files —
never touches the real database file as a side effect.
"""

import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from financeflow.db.models import Base


def get_db_path() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, '..', '..', '..', 'data', 'financeflow.db')
    return os.path.abspath(path)


def get_engine() -> Engine:
    db_path = get_db_path()
    directory = os.path.dirname(db_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine


_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_session_local() -> sessionmaker[Session]:
    """
    Returns the shared sessionmaker, creating the engine and tables
    on first call only. Safe to call repeatedly — the engine is built once.
    """
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = get_engine()
        _SessionLocal = sessionmaker(bind=_engine)
    return _SessionLocal