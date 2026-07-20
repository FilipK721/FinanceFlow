from src.models import Expense, assign_id, Category
from src.data_manager import DataManager
from datetime import datetime
import sys

def main() -> None:
    data_manager = DataManager()
    print('Welcome to FinanceFlow')
    currency = None
    while currency is None:
        try:
            currency = input('Enter Currency (Euro, Dollars, Pounds, Yen, zł)\n>')
            if currency not in ['Euro', 'Dollars', 'Pounds', 'Yen', 'zł']:
                currency = None
                raise ValueError('Wrong currency')
        except ValueError as e:
            print(f'❌ Error: {e}')
        
    while True:
        try:
            print('\nChoose option (1-8)')
            print('1. Save expense')
            print('2. Read all expenses')
            print('3. Edit expense')
            print('4. Show all expenses from a given month')
            print('5. Get most common expense category')
            print('6. the month with the highest expenses')
            print('7. Exit')
            option = input('\nEnter your choice\n>')

            match option:
                case '1':
                    name = input('Enter the name of expense\n>')
                    amount = float(input(f'Enter amount of expense ({currency})\n>'))
                    description = input('Enter description (Leave blank to skip)\n>')
                    id = assign_id()
                    category = Category(input('Enter the category (Food, Groceries, Health, Entertainment, Education, Utilities, Other)\n>'))
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
                    data_manager.show_all_expenses(currency)
                case '3':
                    data_manager.show_all_expenses(currency)
                    expense_id = int(input('Enter id of expense that you want to edit\n>'))
                    data_manager.edit_expense(expense_id)
                case '4':
                    month = int(input('Select month (1-12)'))
                    expenses_in_a_given_month = data_manager.all_expenses_from_a_given_month(month)
                    for expense in expenses_in_a_given_month:
                        print(expense)
                        print('\n\n')
                case '5':
                    print(f'The most common expense category: {data_manager.the_most_common_expense_category()}')

                case '6':
                    print({data_manager.month_with_the_highest_expenses(currency)})

                case '7':
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