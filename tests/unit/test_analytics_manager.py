import json

import pytest

from financeflow.managers.analytics_manager import AnalyticsManager
from financeflow.models import Category, Currency, Expense


class TestAnalyticsManager:
    def test_all_expenses_from_a_given_month(self, sample_analytics_manager: AnalyticsManager) -> None:
        july_expense = Expense("A", 100, Category.FOOD, 1, "28-07-2026").to_dict()
        february_expense = Expense("B", 200, Category.FUEL, 2, "01-02-2026").to_dict()
        with open(sample_analytics_manager.path, "w", encoding="utf-8") as file:
            json.dump({"expenses": [july_expense, february_expense]}, file)

        assert sample_analytics_manager.all_expenses_from_a_given_month(7) == [july_expense]

    def test_the_most_common_expense_category(self, sample_analytics_manager: AnalyticsManager) -> None:
        expenses = [
            Expense("A", 100, Category.FOOD, 1, "01-01-2026").to_dict(),
            Expense("B", 200, Category.FUEL, 2, "01-01-2026").to_dict(),
            Expense("C", 150, Category.FOOD, 3, "01-01-2026").to_dict(),
        ]
        with open(sample_analytics_manager.path, "w", encoding="utf-8") as file:
            json.dump({"expenses": expenses}, file)

        assert sample_analytics_manager.the_most_common_expense_category() == Category.FOOD

    def test_most_common_category_rejects_empty_data(self, sample_analytics_manager: AnalyticsManager) -> None:
        with pytest.raises(ValueError, match="No expenses found"):
            sample_analytics_manager.the_most_common_expense_category()

    def test_month_with_the_highest_expenses(self, sample_analytics_manager: AnalyticsManager) -> None:
        expenses = [
            Expense("A", 100, Category.FOOD, 1, "22-07-2026").to_dict(),
            Expense("B", 200, Category.FUEL, 2, "01-07-2026").to_dict(),
            Expense("C", 150, Category.FOOD, 3, "01-06-2026").to_dict(),
        ]
        with open(sample_analytics_manager.path, "w", encoding="utf-8") as file:
            json.dump({"expenses": expenses}, file)

        assert sample_analytics_manager.month_with_the_highest_expenses(Currency.EURO) == (
            "💰 month with the highest expenses: 07-2026 (300.0 Euro)"
        )

    def test_highest_expenses_rejects_empty_data(self, sample_analytics_manager: AnalyticsManager) -> None:
        with pytest.raises(ValueError, match="No expenses found"):
            sample_analytics_manager.month_with_the_highest_expenses(Currency.EURO)
