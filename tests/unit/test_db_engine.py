from pathlib import Path
import sqlite3

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from financeflow.db import engine as db_engine
from financeflow.db.models import CategoryLimitRow, ExpenseRow
from decimal import Decimal


def test_get_db_path_resolves_data_directory(
    tmp_path: Path,
    monkeypatch,
) -> None:
    module_path = tmp_path / 'src' / 'financeflow' / 'db' / 'engine.py'
    monkeypatch.setattr(db_engine, '__file__', str(module_path))

    assert db_engine.get_db_path() == str(tmp_path / 'data' / 'financeflow.db')


def test_get_engine_creates_directory_and_tables(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database_path = tmp_path / 'new' / 'directory' / 'financeflow.db'
    monkeypatch.setattr(db_engine, 'get_db_path', lambda: str(database_path))

    engine = db_engine.get_engine()

    try:
        assert database_path.parent.is_dir()
        assert set(inspect(engine).get_table_names()) == {
            'expenses',
            'category_limits',
            'settings',
        }
    finally:
        engine.dispose()


def test_get_session_local_initializes_once_and_reuses_factory(
    monkeypatch,
) -> None:
    test_engine = create_engine('sqlite:///:memory:')
    calls = 0

    def make_engine():
        nonlocal calls
        calls += 1
        return test_engine

    monkeypatch.setattr(db_engine, '_engine', None)
    monkeypatch.setattr(db_engine, '_SessionLocal', None)
    monkeypatch.setattr(db_engine, 'get_engine', make_engine)

    try:
        session_factory = db_engine.get_session_local()
        repeated_factory = db_engine.get_session_local()

        assert calls == 1
        assert session_factory is repeated_factory
        assert isinstance(session_factory, sessionmaker)
        assert session_factory.kw['bind'] is test_engine

        with session_factory() as session:
            assert session.is_active
    finally:
        test_engine.dispose()


def test_get_engine_migrates_legacy_real_money_columns(
    tmp_path: Path,
    monkeypatch,
) -> None:
    database_path = tmp_path / 'legacy.db'
    connection = sqlite3.connect(database_path)
    connection.executescript(
        """
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY,
            name VARCHAR NOT NULL,
            amount DOUBLE NOT NULL,
            category VARCHAR NOT NULL,
            date DATE NOT NULL,
            description VARCHAR NOT NULL
        );
        INSERT INTO expenses VALUES (1, 'Coffee', 0.1, 'Food', '2026-01-01', '');
        CREATE TABLE category_limits (
            category VARCHAR PRIMARY KEY,
            "limit" DOUBLE NOT NULL
        );
        INSERT INTO category_limits VALUES ('Food', 1.235);
        """
    )
    connection.commit()
    connection.close()
    monkeypatch.setattr(db_engine, 'get_db_path', lambda: str(database_path))

    engine = db_engine.get_engine()
    try:
        SessionLocal = sessionmaker(bind=engine)
        with SessionLocal() as session:
            assert session.get(ExpenseRow, 1).amount == Decimal('0.10')
            assert (
                session.get(CategoryLimitRow, 'Food').limit
                == Decimal('1.24')
            )

        assert str(inspect(engine).get_columns('expenses')[2]['type']).upper() == 'INTEGER'
        assert str(inspect(engine).get_columns('category_limits')[1]['type']).upper() == 'INTEGER'
    finally:
        engine.dispose()
