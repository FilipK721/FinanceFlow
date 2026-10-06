import pytest
from financeflow.managers.analytics_manager import AnalyticsManager
from financeflow.models import Category, Currency


class TestAnalyticsManager:
    def test_all_expenses_from_a_given_month(self, sample_analytics_manager: AnalyticsManager) -> None:
        expenses = sample_analytics_manager.all_expenses_from_a_given_month(2)
        assert len(expenses) == 2
        assert expenses[0]['name'] == 'Cinema'
        assert expenses[1]['category'] == Category.HEALTH

    def test_the_most_common_expense_category(self, sample_analytics_manager: AnalyticsManager) -> None:
        assert sample_analytics_manager.the_most_common_expense_category() == Category.FOOD

    def test_most_common_category_rejects_empty_data(
        self,
        sample_analytics_manager: AnalyticsManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sample_analytics_manager, 'load_all_expenses', lambda: [])
        with pytest.raises(ValueError, match="No expenses found"):
            sample_analytics_manager.the_most_common_expense_category()

    def test_month_with_the_highest_expenses(
        self,
        sample_analytics_manager: AnalyticsManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        expenses = [
            {'amount': 100.0, 'date': '22-07-2026'},
            {'amount': 200.0, 'date': '01-07-2026'},
            {'amount': 150.0, 'date': '01-06-2026'},
        ]
        monkeypatch.setattr(sample_analytics_manager, 'load_all_expenses', lambda: expenses)

        assert sample_analytics_manager.month_with_the_highest_expenses(Currency.EURO) == (
            "💰 month with the highest expenses: 07-2026 (300.0 Euro)"
        )

    def test_highest_expenses_rejects_empty_data(
        self,
        sample_analytics_manager: AnalyticsManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sample_analytics_manager, 'load_all_expenses', lambda: [])
        with pytest.raises(ValueError, match="No expenses found"):
            sample_analytics_manager.month_with_the_highest_expenses(Currency.EURO)

    def test_spending_by_category_raises_value_error_when_no_expenses(
        self,
        sample_analytics_manager: AnalyticsManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sample_analytics_manager, 'load_all_expenses', lambda: [])
        with pytest.raises(ValueError, match="No expenses found"):
            sample_analytics_manager.spending_by_category()
    
    def test_spending_by_category(
        self,
        sample_analytics_manager: AnalyticsManager,
        sample_dict_expenses: list[dict],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sample_analytics_manager, 'load_all_expenses', lambda: sample_dict_expenses)
        categories_and_expenses = sample_analytics_manager.spending_by_category()
        assert categories_and_expenses == {'Health': 200.0, 'Other': 400.0}
    
    def test_spending_by_month_raises_value_error_when_no_expenses(
        self,
        sample_analytics_manager: AnalyticsManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(sample_analytics_manager, 'load_all_expenses', lambda: [])
        with pytest.raises(ValueError, match='No expenses found'):
            sample_analytics_manager.spending_by_month()
    
    def test_spending_by_month(
        self,
        sample_analytics_manager: AnalyticsManager,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        expenses = [
            {'amount': 100.0, 'date': '15-07-2026'},
            {'amount': 50.0, 'date': '01-02-2026'},
            {'amount': 25.0, 'date': '01-02-2025'},
            {'amount': 10.0, 'date': '20-07-2026'},
        ]
        monkeypatch.setattr(sample_analytics_manager, 'load_all_expenses', lambda: expenses)

        monthly_totals = sample_analytics_manager.spending_by_month()

        assert list(monthly_totals.items()) == [
            ('02-2025', 25.0),
            ('02-2026', 50.0),
            ('07-2026', 110.0),
        ]