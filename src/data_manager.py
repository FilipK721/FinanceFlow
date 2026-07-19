import json
import os
from src.models import Expense, Category

class DataManager:
    def __init__(self) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(current_dir, '..', 'data', 'expenses.json')
        self.path = os.path.abspath(self.path)
        
        directory = os.path.dirname(self.path)
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        if not os.path.exists(self.path) or os.stat(self.path).st_size == 0:
            with open(self.path, 'w', encoding='utf-8') as file:
                json.dump([], file)

    def save_expense(self, expense: Expense) -> None:
        dict_expense = expense.to_dict()
        all_expenses = self.load_all_expenses()
        all_expenses.append(dict_expense)

        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(all_expenses, file, indent=4)
    
    def load_all_expenses(self) -> list[dict[str, int | str | float | Category]]:
        with open(self.path, 'r', encoding='utf-8') as file:
            expenses = json.load(file)
            return expenses
    
    def the_most_common_expense_category(self) -> Category:
        expenses = self.load_all_expenses()
        if not expenses:
            raise ValueError('No expenses found')
            
        categories = [exp['category'] for exp in expenses if 'category' in exp]
        if not categories:
            raise ValueError('No categories found')
            
        most_common_string = max(set(categories), key=categories.count)
        return Category(most_common_string)

    def month_with_the_highest_expenses(self, currency: str) -> str:
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