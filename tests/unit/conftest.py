from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from financeflow.models import Expense, Category
from financeflow.managers.data_manager import DataManager
import financeflow.managers.data_manager as data_manager_module
from financeflow.managers.analytics_manager import AnalyticsManager
from financeflow.managers.budget_manager import BudgetManager
from financeflow.managers.expense_manager import ExpenseManager
from financeflow.managers.export_manager import ExportManager
from sqlalchemy.orm import Session, sessionmaker
from financeflow.db.models import ExpenseRow
from sqlalchemy import create_engine
from financeflow.db.models import Base
from financeflow.views import Views
from typing import Generator

@pytest.fixture(scope="session", autouse=True)
def global_setup(sample_expenses: list[Expense], sample_manager: DataManager) -> Generator[None, None, None]:
    for expense in sample_expenses:
        new_row = ExpenseRow(
            id=expense.id,
            name=expense.name,
            amount=expense.amount,
            category=expense.category.value,
            date=expense.date,
            description=expense.description
        )
        sample_manager.session.add(new_row)
    sample_manager.session.commit()
    
    yield

@pytest.fixture(scope="session")
def test_session() -> Session:
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    return TestSessionLocal()

@pytest.fixture(scope="session")
def sample_manager(test_session: Session) -> DataManager:
    return DataManager(session=test_session)

@pytest.fixture(scope="session")
def sample_expense_manager(test_session: Session) -> ExpenseManager:
    return ExpenseManager(session=test_session)

@pytest.fixture(scope="session")
def sample_analytics_manager(test_session: Session) -> AnalyticsManager:
    return AnalyticsManager(session=test_session)

@pytest.fixture(scope="session")
def sample_budget_manager(test_session: Session) -> BudgetManager:
    return BudgetManager(session=test_session)

@pytest.fixture(scope="session")
def sample_export_manager(test_session: Session) -> ExportManager:
    return ExportManager(session=test_session)

@pytest.fixture(scope="session")
def sample_views(test_session: Session) -> Views:
    return Views(session=test_session)

@pytest.fixture(scope="session")
def sample_expenses() -> list[Expense]:
    return [Expense('Pizza', 40, Category.FOOD, 1, '07-08-2026', ''),
            Expense('Burger', 50, Category.FOOD, 5, '07-03-2026', ''),
            Expense('Fuel', 100, Category.FUEL, 2, '07-07-2026', ''),
            Expense('Cinema', 10, Category.ENTERTAINMENT, 3, '07-02-2026', ''),
            Expense('Doctor', 200, Category.HEALTH, 4, '02-02-2026')]

@pytest.fixture(scope="session")
def sample_views(manager_factory: Callable[[type], Views]) -> Views:
    return manager_factory(Views)

@pytest.fixture(scope="session")
def sample_dict_expenses() -> list[dict]:
    return [
        {
            "name": "Dentist",
            "amount": 100.0,
            "category": "Health",
            "description": "",
            "id": 3,
            "date": "19-09-2026"
        },
        {
            "name": "Doctor",
            "amount": 100.0,
            "category": "Health",
            "description": "",
            "id": 4,
            "date": "19-09-2026"
        },
        {
            "name": "Furniture",
            "amount": 400.0,
            "category": "Other",
            "description": "",
            "id": 5,
            "date": "24-09-2026"
        }
    ]