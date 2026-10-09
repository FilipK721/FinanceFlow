"""Data models used across the FinanceFlow application.

This module defines the expense categories, supported currencies, and the
``Expense`` value object used to represent individual transactions.
"""

from enum import StrEnum


class Category(StrEnum):
    """Enumeration of supported expense categories."""

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
        """Return the string values of all category entries.

        Returns:
            A list of category labels as plain strings.
        """
        return [item.value for item in cls]


class Currency(StrEnum):
    """Enumeration of currencies supported by the application."""

    EURO = 'Euro'
    DOLLARS = 'Dollars'
    POUNDS = 'Pounds'
    YEN = 'Yen'
    PLN = 'Zł'

    @classmethod
    def get_all_values(cls) -> list[str]:
        """Return the string values of all supported currencies.

        Returns:
            A list of currency names as strings.
        """
        return [item.value for item in cls]


class Expense:
    """Represents a single expense record.

    Attributes:
        name: The title or description of the expense.
        amount: The monetary value of the transaction.
        category: The category assigned to the expense.
        id: Unique identifier for the expense record.
        date: The transaction date in the application's date format.
        description: Optional additional details about the expense.
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
        """Initialize an expense.

        Args:
            name: Name or short description of the expense.
            amount: Positive monetary amount for the transaction.
            category: Category used to classify the expense.
            id: Unique identifier for this expense record.
            date: Date of the transaction.
            description: Optional additional notes for the expense.

        Raises:
            ValueError: If the amount is negative.
        """
        if amount < 0:
            raise ValueError('Amount cannot be negative')
        self.name = name
        self.amount = amount
        self.category = category
        self.id = id
        self.date = date
        self.description = description

    def __str__(self) -> str:
        """Return a readable summary of the expense.

        Returns:
            A formatted string with the expense details.
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
        return (
            f'name: {self.name},\n'
            f'amount: {self.amount},\n'
            f'category: {self.category},\n'
            f'id: {self.id},\n'
            f'date: {self.date}'
        )

