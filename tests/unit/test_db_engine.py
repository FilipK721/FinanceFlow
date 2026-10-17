from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from financeflow.db import engine as db_engine


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
