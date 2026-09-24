from unittest.mock import patch
from financeflow.views import Views
from financeflow.models import Currency
from financeflow.managers.expense_manager import ExpenseManager
from unittest.mock import MagicMock
import pytest

class TestViews:
    class TestGetDate:
        def test_returns_formatted_date(self, sample_views: Views) -> None:
            with patch.object(sample_views, 'get_int', side_effect=[2026, 15, 6]):
                result = sample_views.get_date()
            assert result == '15-06-2026'
            
        def test_retries_when_year_out_of_range(self, sample_views: Views) -> None:
            with patch.object(sample_views, 'get_int', side_effect=[3000, 2026, 15, 6]):
                result = sample_views.get_date()
            assert result == '15-06-2026'
        def test_retries_when_day_month_combination_invalid(self, sample_views: Views) -> None:
            with patch.object(sample_views, 'get_int', side_effect=[2026, 31, 2, 22, 2]):
                result = sample_views.get_date()
            assert result == '22-02-2026'
    
    def test_show_all_expenses_raises_valueerror(self, sample_views: Views) -> None:
        sample_views.expense_manager.load_all_expenses = MagicMock(return_value=[])
        with pytest.raises(ValueError, match='No expenses found!'):
            sample_views.show_all_expenses(Currency.EURO)
    
    class TestBuildLimitsText:
        def test_shows_no_limits_message_when_none_set(self, sample_views: Views) -> None:
            sample_views.budget_manager.get_category_limit = MagicMock(return_value=None)
            sample_views.budget_manager.get_limit = MagicMock(return_value=None)

            result = sample_views._build_limits_text()

            assert 'No limits set' in result

        def test_shows_red_when_category_limit_exceeded(self, sample_views: Views) -> None:
            sample_views.budget_manager.get_category_limit = MagicMock(return_value=100.0)
            sample_views.budget_manager.percentage_of_category_limit = MagicMock(return_value=120)
            sample_views.budget_manager.get_limit = MagicMock(return_value=None)

            result = sample_views._build_limits_text()

            assert 'bold red' in result

        def test_shows_yellow_when_category_limit_near(self, sample_views: Views) -> None:
            sample_views.budget_manager.get_category_limit = MagicMock(return_value=100.0)
            sample_views.budget_manager.percentage_of_category_limit = MagicMock(return_value=85)
            sample_views.budget_manager.get_limit = MagicMock(return_value=None)

            result = sample_views._build_limits_text()

            assert 'bold yellow' in result

        def test_shows_green_when_monthly_limit_healthy(self, sample_views: Views) -> None:
            sample_views.budget_manager.get_category_limit = MagicMock(return_value=None)
            sample_views.budget_manager.get_limit = MagicMock(return_value=500.0)
            sample_views.budget_manager.percentage_of_the_limit = MagicMock(return_value=30)

            result = sample_views._build_limits_text()

            assert 'Monthly: 30%' in result
            assert '[green]' in result
