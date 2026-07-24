"""
Data management and business logic module for FinanceFlow.

The DataManager class handles JSON read/write operations, analytical methods,
and CRUD operations for expenses.
"""

import json
import os
from src.models import Expense, Category, Currency
from rich.console import Console
from config.logging import LoggerConfig
logger = LoggerConfig.get_file_logger(__name__)

class DataManager:
    """
    Manages persistent data storage, expense operations, and currency configurations.

    Attributes:
        path (str): Absolute file path to the JSON storage file (expenses.json).
    """
    def __init__(self) -> None:
        """
        Initializes the DataManager instance.

        Sets absolute path to `data/expenses.json`.
        Creates directory and empty JSON file if they do not exist.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(current_dir, '..', 'data', 'expenses.json')
        self.path = os.path.abspath(self.path)
        self.console = Console()
        
        directory = os.path.dirname(self.path)
        
        if not os.path.exists(directory):
            os.makedirs(directory)

            logger.info("Created data directory: %s", directory)
            
        if not os.path.exists(self.path) or os.stat(self.path).st_size == 0:
            with open(self.path, 'w', encoding='utf-8') as file:
                json.dump({}, file, indent=4)
                logger.info("Created new expenses storage file: %s", self.path)

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
        try:
            with open(self.path, 'w', encoding='utf-8') as file:
                file_data['expenses'] = expenses
                json.dump(file_data, file, indent=4)
        except OSError:
            logger.exception("Failed to save expenses data")
            raise

    def load_all_expenses(self) -> list[dict]:
        """
        Loads and returns the list of all expense dictionaries stored in the file.

        Returns:
            list[dict]: List of expense dictionaries.
        """
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get('expenses', [])
    
    def load_file(self) -> dict[str, list[dict] | str]:
        """
        Loads raw structure of the entire JSON file.

        Returns:
            dict[str, list[dict] | str]: Root dictionary stored in the JSON file.
        """
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data
        except json.JSONDecodeError:
            logger.exception("Invalid JSON format in storage file")
            raise
        except OSError:
            logger.exception("Failed to read storage file")
            raise

    def delete_expense(self, expense_id: int) -> None:
        """
        Deletes an expense with the specified ID from the database.

        Args:
            expense_id (int): Identifier of the expense to delete.
        """
        data = self.load_all_expenses()
        all_expenses = data['expenses']
        corrected_expenses = [expense for expense in all_expenses if expense['id'] != expense_id]
        
        self.save_all_expenses(corrected_expenses)

    def the_most_common_expense_category(self) -> Category:
        """
        Determines and returns the most frequently occurring expense category.

        Returns:
            Category: Category enum instance corresponding to the most frequent category.

        Raises:
            ValueError: If no expenses or categories are found in storage.
        """
        expenses = self.load_all_expenses()
        if not expenses:
            raise ValueError('No expenses found')
            
        categories = [exp['category'] for exp in expenses if 'category' in exp]
        if not categories:
            raise ValueError('No categories found')
            
        most_common_string = max(set(categories), key=categories.count)
        return Category(most_common_string)

    def month_with_the_highest_expenses(self, currency: str) -> str:
        """
        Analyzes expense history and finds the month with the highest total spending.

        Args:
            currency (str): Currency label used in output message.

        Returns:
            str: Formatted string showing month (MM-YYYY) and total amount.

        Raises:
            ValueError: If storage is empty or date/amount formats are invalid.
        """
        expenses = self.load_all_expenses()
        if not expenses:
            raise ValueError("No expenses found.")
            
        monthly_totals = {}
        for exp in expenses:
            if 'date' not in exp or 'amount' not in exp:
                raise ValueError("Invalid expense data structure.")
            try:
                month_year = "-".join(exp['date'].split("-")[1:])
                if len(month_year) != 7:
                    raise ValueError
                amount = float(exp['amount'])
                monthly_totals[month_year] = monthly_totals.get(month_year, 0.0) + amount
            except (ValueError, IndexError):
                raise ValueError(f"Invalid date or amount format.")
                
        if not monthly_totals:
            raise ValueError("No valid monthly data found.")
            
        highest_month = max(monthly_totals, key=monthly_totals.get)
        return f'💰 month with the highest expenses: {highest_month} ({monthly_totals[highest_month]}{currency})'
    
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

    def edit_expense(self, expense_id: int) -> None:
        """
        Launches an interactive CLI menu to edit fields of a chosen expense.

        Allows modifying name, amount, category, and description.

        Args:
            expense_id (int): ID of the expense to edit.
        """
        from src.views import Views
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
                        new_category = self.views.choose_category()
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
                self.console(f'❌Error: {e.args}', style='bold red')
                logger.exception("Failed to edit expense (id=%s)", expense_id)
        
    def all_expenses_from_a_given_month(self, month: int) -> list[Expense]:
        """
        Filters and returns Expense objects from a specific month.

        Args:
            month (int): Month number (1 to 12).

        Returns:
            list[Expense]: List of Expense objects for the given month.

        Raises:
            ValueError: If no expenses exist for the specified month.
        """
        all_expenses = self.load_all_expenses()
        given_month_expenses_dict = []
        
        for expense in all_expenses:
            date = expense['date'].split('-')
            expense_month = int(date[1]) 
            
            if expense_month == month:
                given_month_expenses_dict.append(expense)
                
        if not given_month_expenses_dict:
            raise ValueError('No expenses in a given month')
            
        given_month_expenses = []
        for expense in given_month_expenses_dict:
            given_month_expenses.append(Expense(
                expense['name'],
                expense['amount'],
                expense['category'],
                expense['id'],
                expense['date'],
                expense['description']
            ))
        return given_month_expenses
    
    def set_currency(self, currency: Currency | None) -> None:
        """
        Saves default application currency to JSON configuration.

        Args:
            currency (Currency | None): Currency enum instance or None to reset.
        """
        file_data = self.load_file()
        file_data['currency'] = currency
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(file_data, file, indent=4)
    
    def get_currency(self) -> Currency | None:
        """
        Reads configured default currency from JSON file.

        Returns:
            Currency | None: Configured Currency object, or None if not set.
        """
        file_data = self.load_file()
        if 'currency' not in file_data:
            return None
        elif not file_data['currency']:
            return None
        else:
            currency = Currency(file_data['currency'])
            return currency

    def get_all_ids(self) -> list[str]:
        expenses = self.load_all_expenses()
        ids = []
        for expense in expenses:
            ids.append(str(expense['id']))
        return ids
