from unittest.mock import MagicMock
from financeflow.models import Category
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

        assert sample_budget_manager.percentage_of_the_limit() == 75

    def test_percentage_of_the_limit_returns_0(self, sample_budget_manager: BudgetManager) -> None:
        sample_budget_manager.get_limit = MagicMock(return_value=None)
        assert sample_budget_manager.percentage_of_the_limit() == 0
    
    def test_set_and_get_category_limit(self, sample_budget_manager: BudgetManager) -> None:
        sample_budget_manager.set_limit_for_category(Category.FOOD, 300.0)
        assert sample_budget_manager.get_category_limit(Category.FOOD) == 300.0

    def test_delete_category_limit(self, sample_budget_manager: BudgetManager) -> None:
        sample_budget_manager.set_limit_for_category(Category.FOOD, 300.0)
        sample_budget_manager.delete_category_limit(Category.FOOD)
        assert sample_budget_manager.get_category_limit(Category.FOOD) is None

    def test_percentage_of_category_limit(self, sample_budget_manager: BudgetManager) -> None:
        sample_budget_manager.set_limit_for_category(Category.FOOD, 200.0)
        sample_budget_manager.all_expenses_from_a_given_month = MagicMock(
            return_value=[{"amount": 100.0, "category": Category.FOOD}]
        )
        assert sample_budget_manager.percentage_of_category_limit(Category.FOOD) == 50

    def test_returns_true_when_all_limits_below_100(self, sample_budget_manager: BudgetManager) -> None:
        sample_budget_manager.set_limit(500.0)
        sample_budget_manager.percentage_of_the_limit = MagicMock(return_value=50)
        assert sample_budget_manager.make_limits_check() is True

    def test_checks_all_categories_not_just_first(self, sample_budget_manager: BudgetManager) -> None:
        sample_budget_manager.set_limit_for_category(Category.FOOD, 100.0)
        sample_budget_manager.set_limit_for_category(Category.ENTERTAINMENT, 100.0)

        def fake_percentage(category: Category) -> int:
            return 100 if category == Category.ENTERTAINMENT else 10

        sample_budget_manager.percentage_of_category_limit = MagicMock(side_effect=fake_percentage)
        assert sample_budget_manager.make_limits_check() is False