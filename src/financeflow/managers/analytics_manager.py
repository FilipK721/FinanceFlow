"""Analytics helpers for summarizing expense data by month and category."""

from datetime import date
from decimal import Decimal

from financeflow.managers.data_manager import DataManager
from financeflow.models import Category
from financeflow.money import decimal_amount


class AnalyticsManager(DataManager):
    """Compute monthly and category-level summaries from stored expense records."""
    def all_expenses_from_a_given_month(self, month: int, year: int | None = None) -> list[dict]:
        """
        Filters and returns expenses from a specific month.

        Args:
            month (int): Month number (1 to 12).
            year (int | None): Year to match. If None, expenses from the
                given month in any year are returned.

        Returns:
            list[dict]: Expenses matching the given month (and year, if set).
        """
        all_expenses = self.load_all_expenses()
        given_month_expenses_dict = []
        
        for expense in all_expenses:
            expense_date = expense['date']
            if isinstance(expense_date, date):
                expense_month = expense_date.month
                expense_year = expense_date.year
            else:
                _, expense_month, expense_year = expense_date.split('-')
            
            if int(expense_month) != month:
                continue 
            
            if year is not None and int(expense_year) != year:
                continue
            
            given_month_expenses_dict.append(expense)
            
        return given_month_expenses_dict

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
            
        monthly_totals: dict[str, Decimal] = {}
        for exp in expenses:
            expense_date = exp['date']
            if isinstance(expense_date, date):
                month_year = f'{expense_date.month:02d}-{expense_date.year}'
            else:
                month_year = "-".join(expense_date.split("-")[1:])
            amount = decimal_amount(exp['amount'])
            monthly_totals[month_year] = monthly_totals.get(month_year, Decimal('0')) + amount
                
            
        highest_month = max(monthly_totals, key=lambda k: monthly_totals[k])
        return (
            f'💰 month with the highest expenses: {highest_month} '
            f'({monthly_totals[highest_month]:.2f} {currency})'
        )

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

        most_common_string = max(set(categories), key=categories.count)
        return Category(most_common_string)
    
    def spending_by_category(self) -> dict[str, Decimal]:
        """Aggregate total spending for each expense category."""
        expenses = self.load_all_expenses()
        if not expenses:
            raise ValueError('No expenses found')
        categories_and_expenses: dict[str, Decimal] = {}
        for expense in expenses:
            amount = decimal_amount(expense['amount'])
            category = expense['category']
            categories_and_expenses[category] = (
                categories_and_expenses.get(category, Decimal('0')) + amount
            )
        return categories_and_expenses

    def spending_by_month(self) -> dict[str, Decimal]:
        """Aggregate total spending for each month, sorted by year and month."""
        expenses = self.load_all_expenses()
        if not expenses:
            raise ValueError('No expenses found')
        monthly_totals: dict[str, Decimal] = {}
        for expense in expenses:
            amount = decimal_amount(expense['amount'])
            expense_date = expense['date']
            if isinstance(expense_date, date):
                key = f'{expense_date.month:02d}-{expense_date.year}'
            else:
                date_parts = expense_date.split('-')
                key = f'{date_parts[1]}-{date_parts[2]}'
            monthly_totals[key] = monthly_totals.get(key, Decimal('0')) + amount

        def sort_key(month_year: str) -> tuple[int, int]:
            """Return a sortable tuple for month-year strings."""
            month, year = month_year.split('-')
            return (int(year), int(month))

        sorted_keys = sorted(monthly_totals, key=sort_key)

        return {key: monthly_totals[key] for key in sorted_keys}
