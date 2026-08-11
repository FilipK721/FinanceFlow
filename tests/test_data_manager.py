import json
from unittest.mock import mock_open, patch

from financeflow.managers.data_manager import DataManager
from financeflow.models import Category, Currency, Expense


class TestDataManager:
    def test_init(self) -> None:
        with (
            patch("financeflow.managers.data_manager.os.path.exists", return_value=False),
            patch("financeflow.managers.data_manager.os.makedirs") as mock_makedirs,
            patch("financeflow.managers.data_manager.open", mock_open()) as mock_file,
        ):
            manager = DataManager()

        assert manager.path.endswith("data/expenses.json")
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once_with(manager.path, "w", encoding="utf-8")

    def test_load_all_expenses(self, sample_manager: DataManager) -> None:
        expenses = [Expense("A", 100, Category.FOOD, 1, "01-01-2026").to_dict()]
        with open(sample_manager.path, "w", encoding="utf-8") as file:
            json.dump({"expenses": expenses}, file)

        assert sample_manager.load_all_expenses() == expenses

    def test_load_file(self, sample_manager: DataManager) -> None:
        expenses = [Expense("A", 100, Category.FOOD, 1, "01-01-2026").to_dict()]
        with open(sample_manager.path, "w", encoding="utf-8") as file:
            json.dump({"expenses": expenses}, file)

        assert sample_manager.load_file()["expenses"] == expenses

    def test_set_currency(self, sample_manager: DataManager) -> None:
        sample_manager.set_currency(Currency.PLN)

        assert sample_manager.load_file()["currency"] == Currency.PLN

    def test_get_currency(self, sample_manager: DataManager) -> None:
        sample_manager.set_currency(Currency.EURO)

        assert sample_manager.get_currency() == Currency.EURO

    def test_get_currency_returns_none_when_not_saved(self, sample_manager: DataManager) -> None:
        assert sample_manager.get_currency() is None
