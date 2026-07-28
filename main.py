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
                currency = views.get_currency_from_user()
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
                        category = views.get_category()
                        date_choice = views.confirm('Do you want to enter date? (n to set current date)')
                        
                        if date_choice == True:
                            year = views.get_int('Enter year')
                            month_options = [str(option) for option in range(1, 32)]
                            month = views.get_int('Enter month (1-12)', options=month_options, show_choices=False)
                            day_options = [str(option) for option in range(1, 13)]
                            day = views.get_int('Enter day (1-31', options=day_options, show_choices=False)
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
                        ids = sorted(data_manager.get_all_ids())
                        expense_id = views.get_int('Enter id of expense that you want to edit', ids)
                        data_manager.edit_expense(expense_id)
                        logger.info('Expense edited (id=%s)', expense_id)
                    
                    case '4':
                        data_manager.set_currency(None)
                        logger.info('currency reset by user')
                        break
                    case '5':
                        month_options = [str(option) for option in range(1, 13)]
                        month = views.get_int('Select month (1-12)', options=month_options, show_choices=False)
                        views.show_all_expenses_in_a_given_month(month, currency)
                        logger.info('Displayed expenses for month %s', month)
                    case '6':
                        console.print(f'The most common expense category: {data_manager.the_most_common_expense_category()}', style='bold blue')
                        logger.info('Displayed most common expense category')
                    case '7':
                        console.print(data_manager.month_with_the_highest_expenses(currency), style='bold blue')
                        logger.info('Displayed month with highest expenses')

                    case '8':
                        console.print('Goodbye!', style='green')
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