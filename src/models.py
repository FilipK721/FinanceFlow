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
    BILLS = 'Bills'
    EDUCATION = 'Education'
    FUEL = 'Fuel'
    OTHER = 'Other'

    @classmethod
    def get_all_values(cls) -> list[str]:
        return [item.value for item in cls]

class Currency(StrEnum):
    """
    Enum representing supported currencies in the application.

    Available currencies:
    - EURO: Euro (€)
    - DOLLARS: Dollar ($)
    - POUNDS: Pound (£)
    - YEN: Yen (¥)
    - PLN: Polish Złoty (Zł)
    """
    
    EURO = 'Euro'
    DOLLARS = 'Dollars'
    POUNDS = 'Pounds'
    YEN = 'Yen'
    PLN = 'Zł'

    @classmethod
    def get_all_values(cls) -> list[str]:
        return [item.value for item in cls]

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
        description: str = ''
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
        if amount < 0:
            raise ValueError('Amount cannot be negative')
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
f'description:{self.description},\n'
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

