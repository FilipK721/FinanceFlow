import pytest
from sqlalchemy.orm import Session

from financeflow.db.models import ExpenseRow, SettingRow
from financeflow.managers.data_manager import DataManager
from financeflow.models import Category, Currency


class TestDataManager:
    @pytest.fixture(autouse=True)
    def clear_manager_data(self, sample_manager: DataManager) -> None:
        """Isolate tests from data persisted by the shared database fixture."""
        session = sample_manager.session
        session.query(ExpenseRow).delete()
        session.query(SettingRow).delete()
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
                date="01-01-2026",
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
                "date": "01-01-2026",
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
