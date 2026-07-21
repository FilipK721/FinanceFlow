"""
Main execution module (entry point) for FinanceFlow application.

Launches interactive command-line interface (CLI) allowing users to enter/edit expenses,
set currency, and view financial analytics.
"""

from src.models import Expense, assign_id, Category, Currency
from src.data_manager import DataManager
from datetime import datetime
import sys

def main() -> None:
    """
    Main entry function controlling FinanceFlow CLI flow.

    Manages interactive loop:
    1. Retrieves or initializes currency settings.
    2. Displays options menu (1-8).
    3. Processes user input and delegates to DataManager methods.
    """
    while True:
        data_manager = DataManager()
        print('Welcome to FinanceFlow')
        currency = data_manager.get_currency()
        while currency is None:
            try:
                currency = Currency(input('Enter Currency (Euro, Dollars, Pounds, Yen, Zł)\n>'))
                data_manager.set_currency(currency)
            except ValueError as e:
                print(f'❌ Error: {e}')
        while True:
            try:
                print('\nąChoose option (1-8)')
                print('1. Save expense')
                print('2. Read all expenses')
                print('3. Edit expense')
                print('4. Change currency')
                print('5. Show all expenses from a given month')
                print('6. Get most common expense category')
                print('7. the month with the highest expenses')
                print('8. Exit')
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
                        expense_id = int(input('Enter id of expense that you want to edit?\n>'))
                        data_manager.edit_expense(expense_id)
                    
                    case '4':
                        data_manager.set_currency(None)
                        break
                    case '5':
                        month = int(input('Select month (1-12)'))
                        expenses_in_a_given_month = data_manager.all_expenses_from_a_given_month(month)
                        for expense in expenses_in_a_given_month:
                            print(expense)
                            print('\n\n')
                    case '6':
                        print(f'The most common expense category: {data_manager.the_most_common_expense_category()}')

                    case '7':
                        print({data_manager.month_with_the_highest_expenses(currency)})

                    case '8':
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