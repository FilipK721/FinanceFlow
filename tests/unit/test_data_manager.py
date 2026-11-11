from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session

from financeflow.db.models import CategoryLimitRow, ExpenseRow, SettingRow
from financeflow.managers.data_manager import DataManager
from financeflow.models import Category, Currency


class TestDataManager:
    @pytest.fixture(autouse=True)
    def clear_manager_data(self, sample_manager: DataManager) -> None:
        """Isolate tests from data persisted by the shared database fixture."""
        session = sample_manager.session
        session.query(ExpenseRow).delete()
        session.query(SettingRow).delete()
        session.query(CategoryLimitRow).delete()
        session.commit()

    def test_init(self, test_session: Session) -> None:
        manager = DataManager(session=test_session)

        assert manager.session is test_session
        assert manager.path.endswith("financeflow.db")
        assert manager.console is not None

    def test_load_all_expenses(self, sample_manager: DataManager) -> None:
        sample_manager.session.add(
            ExpenseRow(
                id=1,
                name="A",
                amount=100,
                category=Category.FOOD.value,
                date=date(2026, 1, 1),
                description="",
            )
        )
        sample_manager.session.commit()

        assert sample_manager.load_all_expenses() == [
            {
                "name": "A",
                "amount": 100.0,
                "category": Category.FOOD.value,
                "description": "",
                "id": 1,
                "date": date(2026, 1, 1),
            }
        ]

    def test_load_all_expenses_returns_empty_list_when_no_expenses(
        self,
        sample_manager: DataManager,
    ) -> None:
        assert sample_manager.load_all_expenses() == []

    def test_set_currency(self, sample_manager: DataManager) -> None:
        sample_manager.set_currency(Currency.PLN)

        assert sample_manager.get_currency() is Currency.PLN

    def test_get_currency_returns_none_when_not_saved(self, sample_manager: DataManager) -> None:
        assert sample_manager.get_currency() is None

    def test_set_currency_none_removes_saved_currency(self, sample_manager: DataManager) -> None:
        sample_manager.set_currency(Currency.EURO)

        sample_manager.set_currency(None)

        assert sample_manager.get_currency() is None

    def test_set_currency_converts_expenses_and_budget_limits(
        self,
        sample_manager: DataManager,
    ) -> None:
        sample_manager.set_currency(Currency.EURO)
        sample_manager.session.add(
            ExpenseRow(
                id=1,
                name='Coffee',
                amount=Decimal('10.25'),
                category=Category.FOOD.value,
                date=date(2026, 1, 1),
                description='',
            )
        )
        sample_manager.session.add(
            CategoryLimitRow(category=Category.FOOD.value, limit=Decimal('100.00'))
        )
        sample_manager.session.add(SettingRow(key='limit', value='500.00'))
        sample_manager.session.commit()

        with patch(
            'financeflow.managers.data_manager.get_exchange_rate',
            return_value=Decimal('1.234'),
        ) as get_rate:
            sample_manager.set_currency(Currency.DOLLARS)

        get_rate.assert_called_once_with(Currency.EURO, Currency.DOLLARS)
        assert sample_manager.get_currency() is Currency.DOLLARS
        assert sample_manager.session.get(ExpenseRow, 1).amount == Decimal('12.65')
        assert (
            sample_manager.session.get(CategoryLimitRow, Category.FOOD.value).limit
            == Decimal('123.40')
        )
        assert sample_manager.session.get(SettingRow, 'limit').value == '617.00'

    def test_failed_exchange_rate_leaves_currency_and_amounts_unchanged(
        self,
        sample_manager: DataManager,
    ) -> None:
        sample_manager.set_currency(Currency.EURO)
        sample_manager.session.add(
            ExpenseRow(
                id=1,
                name='Coffee',
                amount=Decimal('10.25'),
                category=Category.FOOD.value,
                date=date(2026, 1, 1),
                description='',
            )
        )
        sample_manager.session.commit()

        with patch(
            'financeflow.managers.data_manager.get_exchange_rate',
            side_effect=RuntimeError('Rate service unavailable'),
        ):
            with pytest.raises(RuntimeError, match='Rate service unavailable'):
                sample_manager.set_currency(Currency.DOLLARS)

        assert sample_manager.get_currency() is Currency.EURO
        assert sample_manager.session.get(ExpenseRow, 1).amount == Decimal('10.25')

    def test_setting_currency_without_source_rejects_existing_amounts(
        self,
        sample_manager: DataManager,
    ) -> None:
        sample_manager.session.add(
            ExpenseRow(
                id=1,
                name='Coffee',
                amount=Decimal('10.25'),
                category=Category.FOOD.value,
                date=date(2026, 1, 1),
                description='',
            )
        )
        sample_manager.session.commit()

        with pytest.raises(ValueError, match='currency is unknown'):
            sample_manager.set_currency(Currency.DOLLARS)

        assert sample_manager.get_currency() is None
        assert sample_manager.session.get(ExpenseRow, 1).amount == Decimal('10.25')

    def test_cannot_remove_currency_while_expenses_exist(
        self,
        sample_manager: DataManager,
    ) -> None:
        sample_manager.set_currency(Currency.EURO)
        sample_manager.session.add(
            ExpenseRow(
                id=1,
                name='Coffee',
                amount=Decimal('10.25'),
                category=Category.FOOD.value,
                date=date(2026, 1, 1),
                description='',
            )
        )
        sample_manager.session.commit()

        with pytest.raises(ValueError, match='Cannot remove the currency'):
            sample_manager.set_currency(None)

        assert sample_manager.get_currency() is Currency.EURO
