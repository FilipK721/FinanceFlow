from collections.abc import Callable
from pathlib import Path

import pytest
from financeflow.models import Expense, Category
from financeflow.managers.data_manager import DataManager
import financeflow.managers.data_manager as data_manager_module
from financeflow.managers.analytics_manager import AnalyticsManager
from financeflow.managers.budget_manager import BudgetManager
from financeflow.managers.expense_manager import ExpenseManager

@pytest.fixture
def manager_factory(tmp_path: Path) -> Callable[[type[DataManager]], DataManager]:
    # Mirror the production ``src/financeflow/managers`` layout so DataManager's
    # relative storage path resolves inside this test's temporary directory.
    fake_file = tmp_path / "src" / "financeflow" / "managers" / "data_manager.py"
    fake_file.parent.mkdir(parents=True)
    fake_file.touch()

    def create(manager_class: type[DataManager]) -> DataManager:
        original_file = data_manager_module.__file__
        data_manager_module.__file__ = str(fake_file)
        try:
            return manager_class()
        finally:
            data_manager_module.__file__ = original_file

    return create


@pytest.fixture
def sample_manager(manager_factory: Callable[[type[DataManager]], DataManager]) -> DataManager:
    return manager_factory(DataManager)


@pytest.fixture
def sample_expense_manager(manager_factory: Callable[[type[DataManager]], DataManager]) -> ExpenseManager:
    return manager_factory(ExpenseManager)  # type: ignore[return-value]


@pytest.fixture
def sample_analytics_manager(manager_factory: Callable[[type[DataManager]], DataManager]) -> AnalyticsManager:
    return manager_factory(AnalyticsManager)  # type: ignore[return-value]


@pytest.fixture
def sample_budget_manager(manager_factory: Callable[[type[DataManager]], DataManager]) -> BudgetManager:
    return manager_factory(BudgetManager)  # type: ignore[return-value]

@pytest.fixture
def sample_expenses() -> list[Expense]:
    return [Expense('Pizza', 40, Category.FOOD, 1, '07-08-2026', ''),
            Expense('Fuel', 100, Category.FUEL, 2, '07-07-2026', ''),
            Expense('Cinema', 10, Category.ENTERTAINMENT, 3, '07-02-2026', '')]
