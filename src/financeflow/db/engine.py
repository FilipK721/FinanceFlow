"""Database engine and connection factory configuration for FinanceFlow."""

import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from financeflow.db.models import Base


def get_db_path() -> str:
    """Return the absolute path to the SQLite database file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, '..', '..', '..', 'data', 'financeflow.db')
    return os.path.abspath(path)


def get_engine() -> Engine:
    """Create the SQLite engine and initialize the schema if needed."""
    db_path = get_db_path()
    directory = os.path.dirname(db_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine

_engine = get_engine()
SessionLocal = sessionmaker(bind=_engine)