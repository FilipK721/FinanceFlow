from unittest.mock import MagicMock

from financeflow.managers.budget_manager import BudgetManager


class TestBudgetManager:
    def test_set_and_get_limit(self, sample_budget_manager: BudgetManager) -> None:
        sample_budget_manager.set_limit(1000.0)

        assert sample_budget_manager.get_limit() == 1000.0

    def test_get_limit_returns_none_when_not_set(self, sample_budget_manager: BudgetManager) -> None:
        assert sample_budget_manager.get_limit() is None

    def test_delete_limit(self, sample_budget_manager: BudgetManager) -> None:
        sample_budget_manager.set_limit(1000.0)

        sample_budget_manager.delete_limit()

        assert sample_budget_manager.get_limit() is None

    def test_delete_limit_when_not_set_is_a_none(self, sample_budget_manager: BudgetManager) -> None:
        sample_budget_manager.delete_limit()

        assert sample_budget_manager.get_limit() is None

    def test_percentage_of_limit(self, sample_budget_manager: BudgetManager) -> None:
        sample_budget_manager.set_limit(500.0)
        sample_budget_manager.all_expenses_from_a_given_month = MagicMock(
            return_value=[{"amount": 125.0}, {"amount": 250.0}]
        )

        assert sample_budget_manager.percantage_of_the_limit() == 75
