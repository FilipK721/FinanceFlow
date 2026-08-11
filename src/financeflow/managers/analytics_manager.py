from financeflow.managers.data_manager import DataManager
from financeflow.models import Category

class AnalyticsManager(DataManager):
    def all_expenses_from_a_given_month(self, month: int) -> list[dict]:
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
            
        monthly_totals = {}
        for exp in expenses:
            month_year = "-".join(exp['date'].split("-")[1:])
            amount = float(exp['amount'])
            monthly_totals[month_year] = monthly_totals.get(month_year, 0.0) + amount
                
            
        highest_month = max(monthly_totals, key=monthly_totals.get)
        return f'💰 month with the highest expenses: {highest_month} ({monthly_totals[highest_month]} {currency})'

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