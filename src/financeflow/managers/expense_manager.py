"""Business logic for creating, updating, deleting, and querying expenses."""

from financeflow.managers.data_manager import DataManager
from financeflow.models import Expense, Category
from financeflow.config import logging
from financeflow.db.models import ExpenseRow

logger = logging.getLogger(__name__)


class ExpenseManager(DataManager):
    """Manage expense records persisted in the application's database."""

    def save_expense(self, expense: Expense) -> None:
        """Insert or update an expense record in the database.

        Args:
            expense: The expense object to save.
        """
        existing = self.session.get(ExpenseRow, expense.id)

        if existing is not None:
            existing.name = expense.name
            existing.amount = expense.amount
            existing.category = expense.category.value
            existing.date = expense.date
            existing.description = expense.description
        else:
            new_row = ExpenseRow(
                id=expense.id,
                name=expense.name,
                amount=expense.amount,
                category=expense.category.value,
                date=expense.date,
                description=expense.description
            )
            self.session.add(new_row)

        self.session.commit()

    def delete_expense(self, expense_id: int) -> None:
        """Delete an expense by its ID.

        Args:
            expense_id: Identifier of the expense to remove.

        Raises:
            ValueError: If no expense records are present.
            KeyError: If the specified expense does not exist.
        """
        if self.session.query(ExpenseRow).count() == 0:
            raise ValueError('No expenses found')

        existing = self.session.get(ExpenseRow, expense_id)
        if existing is None:
            raise KeyError(f'Expense with id: {expense_id} not found')

        self.session.delete(existing)
        self.session.commit()

    def edit_expense(self, expense_id: int) -> None:
        """Open an interactive CLI flow to modify a stored expense.

        The user can update the name, amount, category, or description using the
        application's view layer.

        Args:
            expense_id: ID of the expense to edit.
        """
        from financeflow.views import Views

        self.views = Views()
        while True:
            try:
                expense_dict = self.load_expense_by_id(expense_id)
                expense = Expense(
                    expense_dict['name'],
                    expense_dict['amount'],
                    Category(expense_dict['category']),
                    expense_dict['id'],
                    expense_dict['date'],
                    expense_dict['description']
                )
                self.console.print(f'1. {expense.name}', style='bold white')
                self.console.print(f'2. {expense.amount}', style='bold white')
                self.console.print(f'3. {expense.category}', style='bold white')
                self.console.print(f'4. {expense.description}', style='bold white')
                self.console.print('5. Exit', style='bold red')

                option = self.views.get_str('What do you want to change', ['1', '2', '3', '4', '5'])
                match option:
                    case '1':
                        new_name = self.views.get_str('Enter new name')
                        expense.name = new_name
                        self.save_expense(expense)
                        break
                    case '2':
                        currency = self.get_currency()
                        new_amount = self.views.get_amount(currency)
                        expense.amount = new_amount
                        self.save_expense(expense)
                        break
                    case '3':
                        new_category = self.views.get_category()
                        expense.category = new_category
                        self.save_expense(expense)
                        break
                    case '4':
                        new_description = self.views.get_str('Enter new description')
                        expense.description = new_description
                        self.save_expense(expense)
                        break
                    case '5':
                        break
                    case _:
                        raise ValueError('Wrong option')
            except Exception as e:
                self.console.print(f'❌Error: {e.args}', style='bold red')
                logger.exception("Failed to edit expense (id=%s)", expense_id)

    def load_expense_by_id(self, expense_id: int) -> dict[str, float | Category | int | str]:
        """Return a single expense record in dictionary form.

        Args:
            expense_id: Identifier of the expense to fetch.

        Returns:
            A dictionary containing the expense's stored fields.

        Raises:
            ValueError: If the expense with the given ID does not exist.
        """
        found_expense = None
        expenses = self.load_all_expenses()
        for expense in expenses:
            if expense['id'] == expense_id:
                found_expense = expense
        if found_expense:
            return found_expense
        logger.warning("Expense not found (id=%s)", expense_id)
        raise ValueError('Expense not found')

    def get_all_ids(self) -> list[int]:
        """Return all stored expense IDs.

        Returns:
            A list of expense identifiers.

        Raises:
            ValueError: If no expenses are present.
        """
        expenses = self.load_all_expenses()
        if not expenses:
            raise ValueError('No expenses found')
        ids = []
        for expense in expenses:
            ids.append(expense['id'])
        return ids

    def assign_id(self) -> int:
        """Generate the next available unique ID for a new expense.

        Returns:
            The next ID after the current maximum stored expense ID.
        """
        expenses = self.load_all_expenses()

        if not expenses:
            return 1

        max_id = 0
        for expense in expenses:
            if expense['id'] > max_id:
                max_id = expense['id']

        return max_id + 1