import json
import os
from src.models import Expense, Category, Currency

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
                json.dump({}, file, indent=4)

    def save_expense(self, expense: Expense) -> None:
        dict_expense = expense.to_dict()
        all_expenses = self.load_all_expenses()
        corrected_expenses = [expense for expense in all_expenses if expense['id'] != dict_expense['id']]
                
        corrected_expenses.append(dict_expense)

        self.save_all_expenses(corrected_expenses)
    
    def save_all_expenses(self, expenses: list[dict[str, int | float | str | Category]]) -> None:
        file_data = self.load_file()
        with open(self.path, 'w', encoding='utf-8') as file:
            file_data['expenses'] = expenses
            json.dump(file_data, file, indent=4)


    def load_all_expenses(self) -> list[dict[str, int | str | float | Category]]:
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            expenses = data['expenses']
            return expenses
    
    def load_file(self) -> dict[str, list[dict] | str]:
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data

    def delete_expense(self, expense_id: int) -> None:
        data = self.load_all_expenses()
        all_expenses = data['expenses']
        corrected_expenses = [expense for expense in all_expenses if expense['id'] != expense_id]
        
        self.save_all_expenses(corrected_expenses)

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
    
    def load_expense_by_id(self, expense_id: int) -> dict[str, float | Category | int | str]:
        found_expense = None
        expenses = self.load_all_expenses()
        for expense in expenses:
            if expense['id'] == expense_id:
                found_expense = expense
        if found_expense:
          return found_expense  
        else:
            raise ValueError('Expense not found')
    def edit_expense(self, expense_id: int) -> None:
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
                print(f'1. {expense.name}')
                print(f'2. {expense.amount}')
                print(f'3. {expense.category}')
                print(f'4. {expense.description}')
                print('5. Exit')


                option = input(f'What do you want to change (1-5)')
                match option:
                    case '1':
                        new_name = input('Enter new name\n>')
                        expense.name = new_name
                        self.save_expense(expense)
                        break
                    case '2':
                        new_amount = float(input('Enter new amount\n>'))
                        expense.amount = new_amount
                        self.save_expense(expense)
                        break
                    case '3':
                        print(f'categories: {Category()}')
                        new_category = Category(input('Enter new category\n>'))
                        expense.category = new_category
                        self.save_expense(expense)
                        break
                    case '4':
                        new_description = input('Enter new description\n>')
                        expense.description = new_description
                        self.save_expense(expense)
                        break
                    case '5':
                        break
                    case _:
                        raise ValueError('Wrong option')
            except Exception as e:
                print(f'❌Error: {e.args}')
                break
    
    def show_all_expenses(self, currency: str) -> None:
        expenses_list = self.load_all_expenses()
        if not expenses_list:
            raise ValueError('No expenses found!')
        else:
            for expense_dict in expenses_list:
                expense = Expense(
                    expense_dict['name'],
                    expense_dict['amount'], 
                    expense_dict['category'], 
                    expense_dict['id'], 
                    expense_dict['date'], 
                    expense_dict['description']
                )
                print(expense, currency)
                print('\n\n')
        
    def all_expenses_from_a_given_month(self, month: int) -> list[Expense]:
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
        file_data = self.load_file()
        file_data['currency'] = currency
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(file_data, file)
    
    def get_currency(self) -> Currency | None:
        file_data = self.load_file()
        if 'currency' not in file_data:
            return None
        elif not file_data['currency']:
            return None
        else:
            currency = Currency(file_data['currency'])
            return currency
        