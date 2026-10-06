from unittest.mock import MagicMock, patch

import pytest

from financeflow.db.models import ExpenseRow
from financeflow.managers.expense_manager import ExpenseManager
from financeflow.models import Category, Currency, Expense


class TestExpenseManager:
    @pytest.fixture(autouse=True)
    def clear_expenses(self, sample_expense_manager: ExpenseManager) -> None:
        """Keep tests isolated despite the shared SQLAlchemy test session."""
        sample_expense_manager.session.query(ExpenseRow).delete()
        sample_expense_manager.session.commit()

    @staticmethod
    def make_expense_dict(expense: Expense) -> dict[str, float | int | str]:
        """Represent an expense as the database-backed manager returns it."""
        return {
            "name": expense.name,
            "amount": expense.amount,
            "category": expense.category.value,
            "description": expense.description,
            "id": expense.id,
            "date": expense.date,
        }

    @staticmethod
    def add_expenses(manager: ExpenseManager, expenses: list[Expense]) -> None:
        """Persist sample expenses for tests that need database contents."""
        for expense in expenses:
            manager.session.add(
                ExpenseRow(
                    id=expense.id,
                    name=expense.name,
                    amount=expense.amount,
                    category=expense.category.value,
                    date=expense.date,
                    description=expense.description,
                )
            )
        manager.session.commit()

    def test_save_expense_inserts_record(self, sample_expense_manager: ExpenseManager) -> None:
        expense = Expense("A", 100, Category.FOOD, 1, "01-01-2026")

        sample_expense_manager.save_expense(expense)

        assert sample_expense_manager.load_all_expenses() == [self.make_expense_dict(expense)]

    def test_save_expense_updates_existing_record(self, sample_expense_manager: ExpenseManager) -> None:
        original = Expense("A", 100, Category.FOOD, 1, "01-01-2026")
        sample_expense_manager.save_expense(original)
        updated = Expense("Updated", 150, Category.FUEL, 1, "02-01-2026", "note")

        sample_expense_manager.save_expense(updated)

        assert sample_expense_manager.load_all_expenses() == [self.make_expense_dict(updated)]

    def test_delete_expense(self, sample_expense_manager: ExpenseManager) -> None:
        first = Expense("A", 100, Category.FOOD, 1, "01-01-2026")
        second = Expense("B", 200, Category.FUEL, 2, "02-01-2026")
        self.add_expenses(sample_expense_manager, [first, second])

        sample_expense_manager.delete_expense(1)

        assert sample_expense_manager.load_all_expenses() == [self.make_expense_dict(second)]

    def test_delete_expense_rejects_empty_database(self, sample_expense_manager: ExpenseManager) -> None:
        with pytest.raises(ValueError, match="No expenses found"):
            sample_expense_manager.delete_expense(1)

    def test_delete_expense_rejects_unknown_id(self, sample_expense_manager: ExpenseManager) -> None:
        self.add_expenses(
            sample_expense_manager,
            [Expense("A", 100, Category.FOOD, 1, "01-01-2026")],
        )

        with pytest.raises(KeyError, match="Expense with id: 2 not found"):
            sample_expense_manager.delete_expense(2)

    def test_load_expense_by_id(self, sample_expense_manager: ExpenseManager) -> None:
        expense = Expense("A", 100, Category.FOOD, 1, "01-01-2026")
        self.add_expenses(sample_expense_manager, [expense])

        assert sample_expense_manager.load_expense_by_id(1) == self.make_expense_dict(expense)

    def test_load_expense_by_id_rejects_unknown_id(self, sample_expense_manager: ExpenseManager) -> None:
        with pytest.raises(ValueError, match="Expense not found"):
            sample_expense_manager.load_expense_by_id(1)

    def test_get_all_ids(self, sample_expense_manager: ExpenseManager) -> None:
        expenses = [
            Expense("A", 100, Category.FOOD, 1, "01-01-2026"),
            Expense("B", 100, Category.FUEL, 3, "01-01-2026"),
        ]
        self.add_expenses(sample_expense_manager, expenses)

        assert sample_expense_manager.get_all_ids() == [1, 3]

    def test_get_all_ids_rejects_empty_database(self, sample_expense_manager: ExpenseManager) -> None:
        with pytest.raises(ValueError, match="No expenses found"):
            sample_expense_manager.get_all_ids()

    def test_assign_id_starts_at_one_when_database_is_empty(
        self,
        sample_expense_manager: ExpenseManager,
    ) -> None:
        assert sample_expense_manager.assign_id() == 1

    def test_assign_id_returns_one_more_than_maximum(
        self,
        sample_expense_manager: ExpenseManager,
    ) -> None:
        self.add_expenses(
            sample_expense_manager,
            [
                Expense("A", 100, Category.FOOD, 5, "01-01-2026"),
                Expense("B", 100, Category.FUEL, 12, "01-01-2026"),
                Expense("C", 100, Category.OTHER, 3, "01-01-2026"),
            ],
        )

        assert sample_expense_manager.assign_id() == 13

    @pytest.mark.parametrize(
        ("option", "new_value", "field", "expected"),
        [
            ("1", "New name", "name", "New name"),
            ("2", 150.0, "amount", 150.0),
            ("3", Category.FUEL, "category", Category.FUEL),
            ("4", "New description", "description", "New description"),
        ],
    )
    def test_edit_expense_updates_selected_field(
        self,
        sample_expense_manager: ExpenseManager,
        option: str,
        new_value: object,
        field: str,
        expected: object,
    ) -> None:
        expense = Expense("A", 100, Category.FOOD, 1, "01-01-2026")
        sample_expense_manager.load_expense_by_id = MagicMock(
            return_value=self.make_expense_dict(expense)
        )
        sample_expense_manager.save_expense = MagicMock()
        sample_expense_manager.get_currency = MagicMock(return_value=Currency.EURO)
        sample_expense_manager.console = MagicMock()

        with patch("financeflow.views.Views") as mock_views:
            mock_views.return_value.get_str.side_effect = (
                [option, new_value] if option in {"1", "4"} else [option]
            )
            mock_views.return_value.get_amount.return_value = new_value
            mock_views.return_value.get_category.return_value = new_value

            sample_expense_manager.edit_expense(1)

        saved_expense = sample_expense_manager.save_expense.call_args.args[0]
        assert getattr(saved_expense, field) == expected

    def test_edit_expense_exit_does_not_save(self, sample_expense_manager: ExpenseManager) -> None:
        expense = Expense("A", 100, Category.FOOD, 1, "01-01-2026")
        sample_expense_manager.load_expense_by_id = MagicMock(
            return_value=self.make_expense_dict(expense)
        )
        sample_expense_manager.save_expense = MagicMock()
        sample_expense_manager.console = MagicMock()

        with patch("financeflow.views.Views") as mock_views:
            mock_views.return_value.get_str.return_value = "5"
            sample_expense_manager.edit_expense(1)

        sample_expense_manager.save_expense.assert_not_called()

    def test_edit_expense_handles_invalid_option(self, sample_expense_manager: ExpenseManager) -> None:
        expense = Expense("A", 100, Category.FOOD, 1, "01-01-2026")
        sample_expense_manager.load_expense_by_id = MagicMock(
            return_value=self.make_expense_dict(expense)
        )
        sample_expense_manager.save_expense = MagicMock()
        sample_expense_manager.console = MagicMock()

        with patch("financeflow.views.Views") as mock_views:
            mock_views.return_value.get_str.side_effect = ["9", "5"]
            sample_expense_manager.edit_expense(1)

        sample_expense_manager.save_expense.assert_not_called()
        sample_expense_manager.console.print.assert_called()

    def test_edit_expense_handles_load_error(self, sample_expense_manager: ExpenseManager) -> None:
        expense = Expense("A", 100, Category.FOOD, 1, "01-01-2026")
        sample_expense_manager.load_expense_by_id = MagicMock(
            side_effect=[Exception("Database error"), self.make_expense_dict(expense)]
        )
        sample_expense_manager.save_expense = MagicMock()
        sample_expense_manager.console = MagicMock()

        with patch("financeflow.views.Views") as mock_views:
            mock_views.return_value.get_str.return_value = "5"
            sample_expense_manager.edit_expense(1)

        sample_expense_manager.save_expense.assert_not_called()
        sample_expense_manager.console.print.assert_called()
