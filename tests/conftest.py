from typing import Generator
import os, pytest
from financeflow.models import Expense, Category
from financeflow.data_manager import DataManager

@pytest.fixture
def sample_manager() -> Generator[DataManager]:
    manager = DataManager()
    yield manager

    path = manager.path
    if os.path.exists(path):
        os.unlink(path)

@pytest.fixture
def sample_expenses() -> list[Expense]:
    return [Expense('Pizza', 40, Category.FOOD, 1, '07-08-2026', ''),
            Expense('Fuel', 100, Category.FUEL, 2, '07-07-2026', ''),
            Expense('Cinema', 10, Category.ENTERTAINMENT, 3, '07-02-2026', '')]