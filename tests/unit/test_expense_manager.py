from datetime import date
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
    def make_expense_dict(expense: Expense) -> dict[str, float | int | str | date]:
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
        expense = Expense("A", 100, Category.FOOD, 1, date(2026, 1, 1))

        sample_expense_manager.save_expense(expense)

        assert sample_expense_manager.load_all_expenses() == [self.make_expense_dict(expense)]

    def test_save_expense_updates_existing_record(self, sample_expense_manager: ExpenseManager) -> None:
        original = Expense("A", 100, Category.FOOD, 1, date(2026, 1, 1))
        sample_expense_manager.save_expense(original)
        updated = Expense("Updated", 150, Category.FUEL, 1, date(2026, 1, 2), "note")

        sample_expense_manager.save_expense(updated)

        assert sample_expense_manager.load_all_expenses() == [self.make_expense_dict(updated)]

    def test_delete_expense(self, sample_expense_manager: ExpenseManager) -> None:
        first = Expense("A", 100, Category.FOOD, 1, date(2026, 1, 1))
        second = Expense("B", 200, Category.FUEL, 2, date(2026, 1, 2))
        self.add_expenses(sample_expense_manager, [first, second])

        sample_expense_manager.delete_expense(1)

        assert sample_expense_manager.load_all_expenses() == [self.make_expense_dict(second)]

    def test_delete_expense_rejects_empty_database(self, sample_expense_manager: ExpenseManager) -> None:
        with pytest.raises(ValueError, match="No expenses found"):
            sample_expense_manager.delete_expense(1)

    def test_delete_expense_rejects_unknown_id(self, sample_expense_manager: ExpenseManager) -> None:
        self.add_expenses(
            sample_expense_manager,
            [Expense("A", 100, Category.FOOD, 1, date(2026, 1, 1))],
        )

        with pytest.raises(KeyError, match="Expense with id: 2 not found"):
            sample_expense_manager.delete_expense(2)

    def test_load_expense_by_id(self, sample_expense_manager: ExpenseManager) -> None:
        expense = Expense("A", 100, Category.FOOD, 1, date(2026, 1, 1))
        self.add_expenses(sample_expense_manager, [expense])

        assert sample_expense_manager.load_expense_by_id(1) == self.make_expense_dict(expense)

    def test_load_expense_by_id_rejects_unknown_id(self, sample_expense_manager: ExpenseManager) -> None:
        with pytest.raises(ValueError, match="Expense not found"):
            sample_expense_manager.load_expense_by_id(1)

    def test_get_all_ids(self, sample_expense_manager: ExpenseManager) -> None:
        expenses = [
            Expense("A", 100, Category.FOOD, 1, date(2026, 1, 1)),
            Expense("B", 100, Category.FUEL, 3, date(2026, 1, 1)),
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
                Expense("A", 100, Category.FOOD, 5, date(2026, 1, 1)),
                Expense("B", 100, Category.FUEL, 12, date(2026, 1, 1)),
                Expense("C", 100, Category.OTHER, 3, date(2026, 1, 1)),
            ],
        )

        assert sample_expense_manager.assign_id() == 13

    def test_search_expenses_applies_filters_and_sorting(
        self,
        sample_expense_manager: ExpenseManager,
    ) -> None:
        expenses = [
            Expense("Coffee", 5, Category.FOOD, 1, date(2026, 1, 2), "At work"),
            Expense("Coffee", 3, Category.FOOD, 2, date(2026, 1, 4), "With a friend"),
            Expense("Tea", 2, Category.FOOD, 3, date(2026, 1, 3)),
            Expense("Coffee", 1, Category.FUEL, 4, date(2026, 1, 3)),
            Expense("Breakfast", 6, Category.FOOD, 5, date(2026, 1, 3), "Coffee meeting"),
            Expense("Coffee", 7, Category.FOOD, 6, date(2025, 12, 31)),
        ]
        self.add_expenses(sample_expense_manager, expenses)

        results = sample_expense_manager.search_expenses(
            text="coffee",
            category=Category.FOOD,
            date_from=date(2026, 1, 1),
            date_to=date(2026, 1, 5),
            sort_by="amount",
            descending=False,
        )

        assert [expense["id"] for expense in results] == [2, 1, 5]
        assert [expense["name"] for expense in results] == [
            "Coffee",
            "Coffee",
            "Breakfast",
        ]

    def test_search_expenses_returns_empty_list_when_no_rows_match(
        self,
        sample_expense_manager: ExpenseManager,
    ) -> None:
        results = sample_expense_manager.search_expenses(text="not found")

        assert results == []

    @pytest.mark.parametrize(
        ("sort_by", "descending", "expected_ids"),
        [
            ("date", False, [2, 3, 1]),
            ("name", False, [2, 3, 1]),
            ("category", True, [2, 3, 1]),
        ],
    )
    def test_search_expenses_sorts_by_requested_column(
        self,
        sample_expense_manager: ExpenseManager,
        sort_by: str,
        descending: bool,
        expected_ids: list[int],
    ) -> None:
        self.add_expenses(
            sample_expense_manager,
            [
                Expense("Zulu", 10, Category.FOOD, 1, date(2026, 1, 3)),
                Expense("Alpha", 20, Category.OTHER, 2, date(2026, 1, 1)),
                Expense("Bravo", 30, Category.GROCERIES, 3, date(2026, 1, 2)),
            ],
        )

        results = sample_expense_manager.search_expenses(
            sort_by=sort_by,
            descending=descending,
        )

        assert [expense["id"] for expense in results] == expected_ids

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
        expense = Expense("A", 100, Category.FOOD, 1, date(2026, 1, 1))
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
        expense = Expense("A", 100, Category.FOOD, 1, date(2026, 1, 1))
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
        expense = Expense("A", 100, Category.FOOD, 1, date(2026, 1, 1))
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
        expense = Expense("A", 100, Category.FOOD, 1, date(2026, 1, 1))
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
