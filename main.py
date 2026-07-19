from src.models import Expense, assign_id
from src.data_manager import DataManager
from datetime import datetime
import sys

def main() -> None:
    data_manager = DataManager()
    print('Welcome to FinanceFlow')
    while True:
        try:
            print('\nChoose option (1-3)')
            print('1. Save expense')
            print('2. Read all expenses')
            print('3. Exit')
            option = input('\nEnter your choice\n>')

            match option:
                case '1':
                    name = input('Enter the name of expense\n>')
                    amount = float(input('Enter amount of expense\n>'))
                    description = input('Enter description (Leave blank to skip)\n>')
                    id = assign_id()
                    category = input('Enter the category (Food)\n>')
                    date_choice = input('Enter date (yes/no) (no to set current date)\n>')
                    
                    if date_choice == 'yes':
                        year = int(input('Enter year\n>'))
                        month = int(input('Enter month (1-12)\n>'))
                        day = int(input('Enter day (1-31)\n>'))
                        if not (1 <= month <= 12):
                            raise ValueError('Wrong month! (1-12)')
                        if not (1 <= day <= 31):
                            raise ValueError('Wrong day! (1-31)')
                        
                        date = datetime(year, month, day).strftime('%d-%m-%Y')
                        
                    elif date_choice == 'no':
                        date = datetime.today().strftime('%d-%m-%Y')
                    else:
                        raise ValueError('Wrong option! Type "yes" or "no".')
                    
                    expense = Expense(name, amount, category, id, date, description)
                    data_manager.save_expense(expense)
                    print('✅ Expense saved successfully!')
                    
                case '2':
                    expenses_list = data_manager.load_all_expenses()
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
                            print(expense)
                            print('\n\n')
                case '3':
                    print('Goodbye!')
                    sys.exit()
                case _:
                    raise ValueError('Wrong option! Choose 1, 2, or 3.')

        except ValueError as e:
            print(f'❌ Error: {e}')
        except Exception as e:
            print(f'❌ Unexpected error: {e}')

if __name__ == '__main__':
    main()