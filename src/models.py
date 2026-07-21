"""
Data models and enumerations module for the FinanceFlow application.

Contains definitions for expense categories, supported currencies, and the
Expense class representing individual transactions.
"""

from enum import StrEnum


class Category(StrEnum):
    """
    Enum representing available expense categories.

    Values represent text labels used for transaction classification.
    """
    FOOD = 'Food'
    GROCERIES = 'Groceries'
    HEALTH = 'Health'
    ENTERTAINMENT = 'Entertainment'
    UTILITIES = 'Utilities'
    EDUCATION = 'Education'
    OTHER = 'Other'


class Currency(StrEnum):
    """
    Enum representing supported currencies in the application.

    Available currencies:
    - EURO: Euro (€)
    - DOLLARS: Dollar ($)
    - POUNDS: Pound (£)
    - YEN: Yen (¥)
    - ZŁ: Polish Złoty (zł)
    """
    
    EURO = 'Euro'
    DOLLARS = 'Dollars'
    POUNDS = 'Pounds'
    YEN = 'Yen'
    ZŁ = 'Zł'


class Expense:
    """
    Represents an individual expense (financial transaction).

    Attributes:
        name (str): Title or name of the expense.
        amount (float): Transaction amount.
        category (Category): Expense category.
        id (int): Unique numerical identifier.
        date (str): Expense date in 'DD-MM-YYYY' format.
        description (str | None): Optional additional description.
    """

    def __init__(
        self,
        name: str,
        amount: float,
        category: Category,
        id: int,
        date: str,
        description: str | None = None
    ) -> None:
        """
        Initializes a new instance of the Expense class.

        Args:
            name (str): Name of the expense.
            amount (float): Transaction amount.
            category (Category): Expense category from Category enum.
            id (int): Unique numerical ID of the expense.
            date (str): Transaction date in DD-MM-YYYY format.
            description (str | None, optional): Additional description. Defaults to None.
        """
        self.name = name
        self.amount = amount
        self.category = category
        self.id = id
        self.date = date
        self.description = description

    def to_dict(self) -> dict[str, int | str | Category | float | None]:
        """
        Converts the expense object to a dictionary suitable for JSON serialization.

        Returns:
            dict[str, int | str | Category | float | None]: Dictionary representing expense data.
        """
        return {
            'name': self.name,
            'amount': float(self.amount),
            'category': self.category,
            'description': self.description,
            'id': self.id,
            'date': self.date
        }

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the expense for console output.

        Returns:
            str: Formatted string showing expense details.
        """
        if self.description:
            return (
                f'name: {self.name},\n'
                f'amount: {self.amount},\n'
                f'category: {self.category},\n'
                f'description:\n{self.description},\n'
                f'id: {self.id},\n'
                f'date: {self.date}'
            )
        else:
            return (
                f'name: {self.name},\n'
                f'amount: {self.amount},\n'
                f'category: {self.category},\n'
                f'id: {self.id},\n'
                f'date: {self.date}'
            )


def assign_id() -> int:
    """
    Calculates and returns the next unique ID for a new expense.

    Reads existing expenses using DataManager, finds the highest current ID, and returns value + 1.

    Returns:
        int: New unique expense ID (starting from 1).
    """
    from src.data_manager import DataManager
    data_manager = DataManager()
    expenses = data_manager.load_all_expenses()

    if not expenses:
        return 1

    max_id = 0
    for expense in expenses:
        if expense['id'] > max_id:
            max_id = expense['id']

    return max_id + 1