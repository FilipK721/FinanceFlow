from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch
from financeflow.views import Views
from financeflow.models import Category, Currency
from financeflow.managers.expense_manager import ExpenseManager
import pytest


class TestViews:
    def test_get_amount_returns_decimal_and_rounds_to_cents(
        self,
        sample_views: Views,
    ) -> None:
        with patch('financeflow.views.Prompt.ask', return_value='1.005'):
            amount = sample_views.get_amount(Currency.EURO)

        assert amount == Decimal('1.01')

    class TestGetDate:
        def test_returns_formatted_date(self, sample_views: Views) -> None:
            with patch.object(sample_views, 'get_int', side_effect=[2026, 15, 6]):
                result = sample_views.get_date()
            assert result == date(2026, 6, 15)
            
        def test_retries_when_year_out_of_range(self, sample_views: Views) -> None:
            with patch.object(sample_views, 'get_int', side_effect=[3000, 2026, 15, 6]):
                result = sample_views.get_date()
            assert result == date(2026, 6, 15)
        def test_retries_when_day_month_combination_invalid(self, sample_views: Views) -> None:
            with patch.object(sample_views, 'get_int', side_effect=[2026, 31, 2, 22, 2]):
                result = sample_views.get_date()
            assert result == date(2026, 2, 22)
    
    def test_show_all_expenses_raises_valueerror(self, sample_views: Views) -> None:
        sample_views.expense_manager.load_all_expenses = MagicMock(return_value=[])
        with pytest.raises(ValueError, match='No expenses found!'):
            sample_views.show_all_expenses(Currency.EURO)

    def test_show_expenses_table_preserves_order_and_formats_values(self, sample_views: Views) -> None:
        sample_views.console = MagicMock()
        table = MagicMock()
        expenses = [
            {
                'name': 'Coffee',
                'amount': 4.5,
                'description': 'Morning',
                'category': 'Food',
                'id': 8,
                'date': date(2026, 10, 15),
            },
            {
                'name': 'Tea',
                'amount': 2.0,
                'description': '',
                'category': 'Other',
                'id': 3,
                'date': date(2026, 10, 16),
            },
        ]

        with patch('financeflow.views.Table', return_value=table) as table_factory:
            sample_views.show_expenses_table(expenses, Currency.EURO)

        table_factory.assert_called_once_with(title=f'📊 Expenses ({Currency.EURO})')
        assert table.add_row.call_args_list == [
            (('Coffee', '4.50', 'Morning', 'Food', '8', '15-10-2026'),),
            (('Tea', '2.00', '', 'Other', '3', '16-10-2026'),),
        ]
        sample_views.console.print.assert_called_once_with(table)

    def test_get_search_criteria_returns_selected_filters_and_sorting(
        self,
        sample_views: Views,
    ) -> None:
        start = date(2026, 1, 1)
        end = date(2026, 1, 31)
        sample_views.confirm = MagicMock(side_effect=[True, True, True])
        sample_views.get_category = MagicMock(return_value=Category.FOOD)
        sample_views.get_date = MagicMock(side_effect=[start, end])

        with patch(
            'financeflow.views.Prompt.ask',
            side_effect=['  coffee  ', 'amount', 'asc'],
        ):
            result = sample_views.get_search_criteria()

        assert result == {
            'text': 'coffee',
            'category': Category.FOOD,
            'date_from': start,
            'date_to': end,
            'sort_by': 'amount',
            'descending': False,
        }

    def test_get_search_criteria_uses_none_for_skipped_filters(
        self,
        sample_views: Views,
    ) -> None:
        sample_views.confirm = MagicMock(return_value=False)

        with patch(
            'financeflow.views.Prompt.ask',
            side_effect=['', 'date', 'desc'],
        ):
            result = sample_views.get_search_criteria()

        assert result == {
            'text': None,
            'category': None,
            'date_from': None,
            'date_to': None,
            'sort_by': 'date',
            'descending': True,
        }

    def test_get_search_criteria_rejects_reversed_date_range(
        self,
        sample_views: Views,
    ) -> None:
        sample_views.confirm = MagicMock(side_effect=[False, True, True])
        sample_views.get_date = MagicMock(
            side_effect=[date(2026, 2, 1), date(2026, 1, 1)]
        )

        with patch('financeflow.views.Prompt.ask', return_value=''):
            with pytest.raises(ValueError, match='Start date cannot be after end date'):
                sample_views.get_search_criteria()
    
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
