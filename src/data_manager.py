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
    