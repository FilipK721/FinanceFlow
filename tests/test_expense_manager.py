import json
from unittest.mock import MagicMock, patch

import pytest

from financeflow.managers.expense_manager import ExpenseManager
from financeflow.models import Category, Expense


class TestExpenseManager:
    def test_save_expense(self, sample_expense_manager: ExpenseManager, sample_expenses: list[Expense]) -> None:
        expense = sample_expenses[0]
        sample_expense_manager.save_expense(expense)

        assert sample_expense_manager.load_all_expenses() == [expense.to_dict()]

    def test_save_all_expenses_propagates_os_error(self, sample_expense_manager: ExpenseManager) -> None:
        expenses = [Expense("A", 100, Category.FOOD, 1, "01-01-2026").to_dict()]

        with patch("builtins.open", side_effect=OSError("No permission")), pytest.raises(OSError, match="No permission"):
            sample_expense_manager.save_all_expenses(expenses)

    def test_delete_expense(self, sample_expense_manager: ExpenseManager) -> None:
        first = Expense("A", 100, Category.FOOD, 1, "01-01-2026").to_dict()
        second = Expense("B", 200, Category.FUEL, 2, "02-01-2026").to_dict()
        sample_expense_manager.save_all_expenses([first, second])

        sample_expense_manager.delete_expense(1)

        assert sample_expense_manager.load_all_expenses() == [second]

    def test_delete_expense_rejects_unknown_id(self, sample_expense_manager: ExpenseManager) -> None:
        with pytest.raises(ValueError, match="No expenses found"):
            sample_expense_manager.delete_expense(1)

    def test_load_expense_by_id(self, sample_expense_manager: ExpenseManager) -> None:
        expense = Expense("A", 100, Category.FOOD, 1, "01-01-2026").to_dict()
        sample_expense_manager.save_all_expenses([expense])

        assert sample_expense_manager.load_expense_by_id(1) == expense

    def test_get_all_ids(self, sample_expense_manager: ExpenseManager) -> None:
        sample_expense_manager.save_all_expenses([
            Expense("A", 100, Category.FOOD, 1, "01-01-2026").to_dict(),
            Expense("B", 100, Category.FUEL, 3, "01-01-2026").to_dict(),
        ])

        assert sample_expense_manager.get_all_ids() == [1, 3]

    @patch("financeflow.managers.expense_manager.ExpenseManager.load_all_expenses")
    def test_assign_id(self, mock_load: MagicMock, sample_expense_manager: ExpenseManager) -> None:
        mock_load.return_value = [{"id": 5}, {"id": 12}, {"id": 3}]

        assert sample_expense_manager.assign_id() == 13

    def test_edit_expense_name(self, sample_expense_manager: ExpenseManager, sample_expenses: list[Expense]) -> None:
        sample_expense_manager.load_expense_by_id = MagicMock(return_value=sample_expenses[0].to_dict())
        sample_expense_manager.save_expense = MagicMock()
        sample_expense_manager.console = MagicMock()

        with patch("financeflow.views.Views") as mock_views:
            mock_views.return_value.get_str.side_effect = ["1", "New name"]
            sample_expense_manager.edit_expense(1)

        saved_expense = sample_expense_manager.save_expense.call_args.args[0]
        assert saved_expense.name == "New name"

    def test_edit_expense_amount(self, sample_expense_manager: ExpenseManager, sample_expenses: list[Expense]) -> None:
        sample_expense_manager.load_expense_by_id = MagicMock(return_value=sample_expenses[0].to_dict())
        sample_expense_manager.save_expense = MagicMock()
        sample_expense_manager.get_currency = MagicMock(return_value="Euro")
        sample_expense_manager.console = MagicMock()

        with patch("financeflow.views.Views") as mock_views:
            mock_views.return_value.get_str.return_value = "2"
            mock_views.return_value.get_amount.return_value = 150.0
            sample_expense_manager.edit_expense(1)

        saved_expense = sample_expense_manager.save_expense.call_args.args[0]
        assert saved_expense.amount == 150.0

    def test_edit_expense_category(self, sample_expense_manager: ExpenseManager, sample_expenses: list[Expense]) -> None:
        sample_expense_manager.load_expense_by_id = MagicMock(return_value=sample_expenses[0].to_dict())
        sample_expense_manager.save_expense = MagicMock()
        sample_expense_manager.console = MagicMock()

        with patch("financeflow.views.Views") as mock_views:
            mock_views.return_value.get_str.return_value = "3"
            mock_views.return_value.get_category.return_value = Category.FUEL
            sample_expense_manager.edit_expense(1)

        saved_expense = sample_expense_manager.save_expense.call_args.args[0]
        assert saved_expense.category == Category.FUEL

    def test_edit_expense_description(self, sample_expense_manager: ExpenseManager, sample_expenses: list[Expense]) -> None:
        sample_expense_manager.load_expense_by_id = MagicMock(return_value=sample_expenses[0].to_dict())
        sample_expense_manager.save_expense = MagicMock()
        sample_expense_manager.console = MagicMock()

        with patch("financeflow.views.Views") as mock_views:
            mock_views.return_value.get_str.side_effect = ["4", "New description"]
            sample_expense_manager.edit_expense(1)

        saved_expense = sample_expense_manager.save_expense.call_args.args[0]
        assert saved_expense.description == "New description"

    def test_edit_expense_exit_does_not_save(self, sample_expense_manager: ExpenseManager, sample_expenses: list[Expense]) -> None:
        sample_expense_manager.load_expense_by_id = MagicMock(return_value=sample_expenses[0].to_dict())
        sample_expense_manager.save_expense = MagicMock()
        sample_expense_manager.console = MagicMock()

        with patch("financeflow.views.Views") as mock_views:
            mock_views.return_value.get_str.return_value = "5"
            sample_expense_manager.edit_expense(1)

        sample_expense_manager.save_expense.assert_not_called()

    def test_edit_expense_handles_invalid_option(self, sample_expense_manager: ExpenseManager, sample_expenses: list[Expense]) -> None:
        sample_expense_manager.load_expense_by_id = MagicMock(return_value=sample_expenses[0].to_dict())
        sample_expense_manager.save_expense = MagicMock()
        sample_expense_manager.console = MagicMock()

        with patch("financeflow.views.Views") as mock_views:
            mock_views.return_value.get_str.side_effect = ["9", "5"]
            sample_expense_manager.edit_expense(1)

        sample_expense_manager.save_expense.assert_not_called()
        sample_expense_manager.console.print.assert_called()

    def test_edit_expense_handles_load_error(self, sample_expense_manager: ExpenseManager, sample_expenses: list[Expense]) -> None:
        sample_expense_manager.load_expense_by_id = MagicMock(
            side_effect=[Exception("Database error"), sample_expenses[0].to_dict()]
        )
        sample_expense_manager.save_expense = MagicMock()
        sample_expense_manager.console = MagicMock()

        with patch("financeflow.views.Views") as mock_views:
            mock_views.return_value.get_str.return_value = "5"
            sample_expense_manager.edit_expense(1)

        sample_expense_manager.save_expense.assert_not_called()
        sample_expense_manager.console.print.assert_called()
