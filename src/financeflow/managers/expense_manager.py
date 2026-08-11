from financeflow.managers.data_manager import DataManager
from financeflow.models import Expense, Category
from financeflow.config import logging
import json
logger = logging.getLogger(__name__)

class ExpenseManager(DataManager):
    def save_expense(self, expense: Expense) -> None:
        """
        Saves a new expense or updates an existing record in the database.

        If an expense with the same ID exists, it is overwritten with new data.

        Args:
            expense (Expense): Expense object to save.
        """
        dict_expense = expense.to_dict()
        all_expenses = self.load_all_expenses()
        corrected_expenses = [expense for expense in all_expenses if expense['id'] != dict_expense['id']]
                
        corrected_expenses.append(dict_expense)

        self.save_all_expenses(corrected_expenses)

    def save_all_expenses(self, expenses: list[dict[str, int | float | str | Category]]) -> None:
        """
        Saves a full list of expense dictionaries to the JSON file.

        Args:
            expenses (list[dict]): List of dictionaries representing expenses.
        """
        file_data = self.load_file()
        with open(self.path, 'w', encoding='utf-8') as file:
            file_data['expenses'] = expenses
            json.dump(file_data, file, indent=4)


    def delete_expense(self, expense_id: int) -> None:
        """
        Deletes an expense with the specified ID from the database.

        Args:
            expense_id (int): Identifier of the expense to delete.
        """
        expenses = self.load_all_expenses()
        if not expenses or expenses == []:
            raise ValueError('No expenses found')
        expense_with_correct_id = None
        for expense in expenses:
            if expense['id'] == expense_id:
                expense_with_correct_id = expense
        if not expense_with_correct_id:
            raise KeyError('Expense id not found')
        corrected_expenses = [expense for expense in expenses if expense['id'] != expense_id]
        self.save_all_expenses(corrected_expenses)

    def edit_expense(self, expense_id: int) -> None:
        """
        Launches an interactive CLI menu to edit fields of a chosen expense.

        Allows modifying name, amount, category, and description.

        Args:
            expense_id (int): ID of the expense to edit.
        """
        from financeflow.views import Views
        self.views = Views()
        while True:
            try:
                expense_dict = self.load_expense_by_id(expense_id)
                expense = Expense(
                    expense_dict['name'],
                    expense_dict['amount'],
                    expense_dict['category'],
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
        """
        Finds and returns an expense dictionary by its ID.

        Args:
            expense_id (int): ID of the requested expense.

        Returns:
            dict: Dictionary containing expense details.

        Raises:
            ValueError: If expense with given ID does not exist.
        """
        found_expense = None
        expenses = self.load_all_expenses()
        for expense in expenses:
            if expense['id'] == expense_id:
                found_expense = expense
        if found_expense:
          return found_expense  
        else:
            logger.warning("Expense not found (id=%s)", expense_id)
            raise ValueError('Expense not found')

    def get_all_ids(self) -> list[int]:
        expenses = self.load_all_expenses()
        if not expenses:
            raise ValueError('No expenses found')
        ids = []
        for expense in expenses:
            ids.append(expense['id'])
        return ids

    def assign_id(self) -> int:
        """
        Calculates and returns the next unique ID for a new expense.

        Reads existing expenses using DataManager, finds the highest current ID, and returns value + 1.

        Returns:
            int: New unique expense ID (starting from 1).
        """

        expenses = self.load_all_expenses()

        if not expenses:
            return 1

        max_id = 0
        for expense in expenses:
            if expense['id'] > max_id:
                max_id = expense['id']

        return max_id + 1