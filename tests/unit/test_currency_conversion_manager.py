from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from financeflow.db.models import CategoryLimitRow, ExpenseRow, SettingRow
from financeflow.managers.currency_conversion_manager import CurrencyConversionManager
from financeflow.models import Category, Currency


class TestCurrencyConversionManager:
    @pytest.fixture(autouse=True)
    def clear_financial_data(self, test_session):
        test_session.query(ExpenseRow).delete()
        test_session.query(CategoryLimitRow).delete()
        test_session.query(SettingRow).filter(
            SettingRow.key.in_(['currency', 'limit'])
        ).delete(synchronize_session=False)
        test_session.commit()
        yield
        test_session.query(ExpenseRow).delete()
        test_session.query(CategoryLimitRow).delete()
        test_session.query(SettingRow).filter(
            SettingRow.key.in_(['currency', 'limit'])
        ).delete(synchronize_session=False)
        test_session.commit()

    def test_convert_amounts_updates_expenses_and_budgets(self, test_session) -> None:
        test_session.add(
            ExpenseRow(
                id=1,
                name='Lunch',
                amount=Decimal('10.25'),
                category=Category.FOOD.value,
                date=date(2026, 1, 1),
                description='',
            )
        )
        test_session.add(
            CategoryLimitRow(category=Category.FOOD.value, limit=Decimal('100.00'))
        )
        test_session.add(SettingRow(key='limit', value='500.00'))
        test_session.commit()
        rate_provider = MagicMock(return_value=Decimal('1.234'))

        manager = CurrencyConversionManager(test_session, rate_provider)
        manager.convert_amounts(Currency.EURO, Currency.DOLLARS)
        test_session.commit()

        rate_provider.assert_called_once_with(Currency.EURO, Currency.DOLLARS)
        assert test_session.get(ExpenseRow, 1).amount == Decimal('12.65')
        assert (
            test_session.get(CategoryLimitRow, Category.FOOD.value).limit
            == Decimal('123.40')
        )
        assert test_session.get(SettingRow, 'limit').value == '617.00'

    def test_convert_amounts_rounds_to_target_currency_precision(
        self,
        test_session,
    ) -> None:
        test_session.add(
            ExpenseRow(
                id=1,
                name='Lunch',
                amount=Decimal('10.25'),
                category=Category.FOOD.value,
                date=date(2026, 1, 1),
                description='',
            )
        )
        test_session.commit()
        rate_provider = MagicMock(return_value=Decimal('150.25'))

        manager = CurrencyConversionManager(test_session, rate_provider)
        manager.convert_amounts(Currency.EURO, Currency.YEN)
        test_session.commit()

        assert test_session.get(ExpenseRow, 1).amount == Decimal('1540.00')

    def test_convert_amounts_leaves_transaction_control_to_caller(
        self,
        test_session,
    ) -> None:
        rate_provider = MagicMock(return_value=Decimal('1.1'))
        manager = CurrencyConversionManager(test_session, rate_provider)

        with patch.object(test_session, 'commit') as commit:
            manager.convert_amounts(Currency.EURO, Currency.DOLLARS)

        commit.assert_not_called()
