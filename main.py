"""
Main execution module (entry point) for FinanceFlow application.

Launches interactive command-line interface (CLI) allowing users to enter/edit expenses,
set currency, and view financial analytics.
"""

from src.models import Expense, assign_id, Category, Currency
from src.data_manager import DataManager
from src.views import Views
from datetime import datetime
import sys
from rich.console import Console
from config.logging import LoggerConfig
logger = LoggerConfig.get_file_logger(__name__)

def main() -> None:
    """
    Main entry function controlling FinanceFlow CLI flow.

    Manages interactive loop:
    1. Retrieves or initializes currency settings.
    2. Displays options menu (1-8).
    3. Processes user input and delegates to DataManager methods.
    """
    while True:
        console = Console()
        views = Views()
        data_manager = DataManager()
        views.display_welcome_banner()
        currency = data_manager.get_currency()
        while currency is None:
            try:
                currency = Currency(input('Enter Currency (Euro, Dollars, Pounds, Yen, Zł)\n>'))
                data_manager.set_currency(currency)
            except ValueError as e:
                console.print(f'❌ Error: {e}', style='bold red')
                logger.info('Wrong currency entered: %s', e)
        while True:
            try:
                views.display_menu()
                option = views.get_str('Enter option', ['1', '2', '3', '4', '5', '6', '7', '8'])

                match option:
                    case '1':
                        name = views.get_str('Enter the name of expense')
                        amount = views.get_amount(currency)
                        description = views.get_str('Enter description (Leave blank to skip)')
                        id = assign_id()
                        category = views.choose_category()
                        date_choice = views.confirm('Do you want to enter date?')
                        
                        if date_choice == True:
                            year = views.get_int('Enter year')
                            month = views.get_int('Enter month (1-12)')
                            day = views.get_int('Enter day (1-31')
                            if not (1 <= month <= 12):
                                raise ValueError('Wrong month! (1-12)')
                            if not (1 <= day <= 31):
                                raise ValueError('Wrong day! (1-31)')
                            
                            date = datetime(year, month, day).strftime('%d-%m-%Y')
                            
                        elif date_choice == False:
                            date = datetime.today().strftime('%d-%m-%Y')
                        else:
                            raise ValueError('Wrong option! Type "y" or "n".')
                        expense = Expense(name, amount, category, id, date, description)
                        data_manager.save_expense(expense)
                        logger.info(
                                    'Expense saved (id=%s, amount=%.2f, category=%s)',
                                    expense.id,
                                    expense.amount,
                                    expense.category.value,
                                )
                        console.print('[green]✅ Expense saved successfully![/green]')
                        
                    case '2':
                        views.show_all_expenses(currency)
                        logger.info('Displayed all expenses')
                    case '3':
                        views.show_all_expenses(currency)
                        ids = data_manager.get_all_ids()
                        expense_id = views.get_int('Enter id of expense that you want to edit', ids)
                        data_manager.edit_expense(expense_id)
                        logger.info('Expense edited (id=%s)', expense_id)
                    
                    case '4':
                        data_manager.set_currency(None)
                        logger.info('currency reset by user')
                        break
                    case '5':
                        month = int(input('Select month (1-12)'))
                        expenses_in_a_given_month = data_manager.all_expenses_from_a_given_month(month)
                        for expense in expenses_in_a_given_month:
                            print(expense)
                            print('\n\n')
                        logger.info('Displayed expenses for month %s', month)
                    case '6':
                        print(f'The most common expense category: {data_manager.the_most_common_expense_category()}')
                        logger.info('Displayed most common expense category')

                    case '7':
                        print({data_manager.month_with_the_highest_expenses(currency)})
                        logger.info('Displayed month with highest expenses')

                    case '8':
                        print('Goodbye!')
                        logger.info('Aplication closed by user')
                        sys.exit()
                    case _:
                        logger.info('Invalid menu option %s', option)
                        raise ValueError('Wrong option! Choose 1-8.')
            except Exception as e:
                logger.error('Unexpected application error')
                console.print(f'❌ Unexpected error: {e}', style='bold red')

if __name__ == '__main__':
    main()