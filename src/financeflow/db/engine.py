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
from decimal import Decimal

from sqlalchemy import MetaData, Table, create_engine, inspect, select, Engine
from sqlalchemy.orm import sessionmaker, Session
from financeflow.db.models import Base
from financeflow.money import decimal_amount


_MONEY_COLUMNS = {
    'expenses': ('amount',),
    'category_limits': ('limit',),
}


def _migrate_legacy_money_columns(engine: Engine) -> None:
    """Rebuild legacy REAL money columns as exact integer minor-unit columns."""
    inspector = inspect(engine)
    for table_name, money_columns in _MONEY_COLUMNS.items():
        columns = {column['name']: column['type'] for column in inspector.get_columns(table_name)}
        if all('INT' in str(columns[column]).upper() for column in money_columns):
            continue

        legacy_name = f'{table_name}_legacy_money'
        table = Base.metadata.tables[table_name]
        with engine.begin() as connection:
            connection.exec_driver_sql(
                f'ALTER TABLE "{table_name}" RENAME TO "{legacy_name}"'
            )
            table.create(connection)
            legacy_table = Table(
                legacy_name,
                MetaData(),
                autoload_with=connection,
            )
            migrated_rows: list[dict[str, object]] = []
            for row in connection.execute(select(legacy_table)).mappings():
                values = dict(row)
                for column in money_columns:
                    values[column] = decimal_amount(Decimal(str(values[column])))
                migrated_rows.append(values)
            if migrated_rows:
                connection.execute(table.insert(), migrated_rows)
            legacy_table.drop(connection)


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
    _migrate_legacy_money_columns(engine)
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