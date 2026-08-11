"""
Main execution module (entry point) for FinanceFlow application.

Launches interactive command-line interface (CLI) allowing users to enter/edit expenses,
set currency, and view financial analytics.
"""

from financeflow.models import Expense, Currency
from financeflow.data_manager import DataManager
from financeflow.views import Views
from datetime import datetime
import sys
from rich.console import Console
from financeflow.config.logging import LoggerConfig
logger = LoggerConfig.get_file_logger(__name__)

def expenses_menu(views: Views, data_manager: DataManager, currency: Currency, console: Console) -> None:
    while True:
        views.display_expenses_menu()
        expense_option = views.get_str('Enter option', ['1', '2', '3', '4', '0'])
        match expense_option:
            case '1':
                if data_manager.get_limit():
                    views.display_limit()
                    if data_manager.percantage_of_the_limit() >= 100:
                        break

                name = views.get_str('Enter the name of expense')
                amount = views.get_amount(currency)
                description = views.get_str('Enter description (Leave blank to skip)')
                id = data_manager.assign_id()
                category = views.get_category()
                date_choice = views.confirm('Do you want to enter date? (n to set current date)')
                
                if date_choice == True:
                    year = views.get_int('Enter year')
                    month_options = [str(option) for option in range(1, 13)]
                    month = views.get_int('Enter month (1-12)', options=month_options, show_choices=False)
                    day_options = [str(option) for option in range(1, 32)]
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
                if data_manager.get_limit():
                    views.display_limit()
                views.show_all_expenses(currency)
                logger.info('Displayed all expenses')
            case '3':
                if data_manager.get_limit():
                    views.display_limit()
                views.show_all_expenses(currency)
                ids = sorted(data_manager.get_all_ids())
                str_ids = [str(id) for id in ids]
                expense_id = views.get_int('Enter id of expense that you want to edit', str_ids)
                data_manager.edit_expense(expense_id)
                logger.info('Expense edited (id=%s)', expense_id)

            case '4':
                confirmed = views.confirm('Do you want to delete expense?')
                if confirmed == True:
                    views.show_all_expenses(currency)
                    ids = data_manager.get_all_ids()
                    str_ids = [str(id) for id in ids]
                    expense_id = views.get_int('Enter the id of expense that you want to delete', sorted(str_ids))
                    data_manager.delete_expense(expense_id)
                    logger.info('Deleted expense with id: %s', expense_id)
                    console.print('✅ Expense deleted successfully!', style='bright_green')
                else:
                    console.print('Coming back to menu', style='bold white')
                    break

            case '0':
                console.print('Going back to menu', style='bold white')
                break

def analytics_menu(views: Views, data_manager: DataManager, currency: Currency, console: Console) -> None:
    while True:
        views.display_analytics_menu()
        analytics_option = views.get_str('Enter option', ['1', '2', '3', '0'])
        match analytics_option:
            case '1':
                if data_manager.get_limit():
                    views.display_limit()
                month_options = [str(option) for option in range(1, 13)]
                month = views.get_int('Select month (1-12)', options=month_options, show_choices=False)
                views.show_all_expenses_in_a_given_month(month, currency)
                logger.info('Displayed expenses for month %s', month)

            case '2':
                if data_manager.get_limit():
                    views.display_limit()
                console.print(f'The most common expense category: {data_manager.the_most_common_expense_category()}', style='bold blue')
                logger.info('Displayed most common expense category')

            case '3':
                if data_manager.get_limit():
                    views.display_limit()
                console.print(data_manager.month_with_the_highest_expenses(currency), style='bold blue')
                logger.info('Displayed month with highest expenses')

            case '0':
                console.print('Going back to menu', style='bold white')
                break

def budget_menu(views: Views, data_manager: DataManager, currency: Currency, console: Console) -> None:
    while True:
        views.display_budget_menu()
        budget_option = views.get_str('Enter option', ['1', '2', '0'])
        match budget_option:
            case '1':
                limit = views.get_limit(currency)
                data_manager.set_limit(limit)
                console.print(f'The limit is set to {limit}', style='bright_green')
                logger.info('User set limit: %s', limit)

            case '2':
                data_manager.delete_limit()
                console.print('Limit deleted successfully', style='bright_green')
                logger.info('User deleted limit')

            case '0':
                console.print('Going back to menu', style='bold white')
                break

def settings_menu(views: Views, data_manager: DataManager, console: Console) -> None:
    while True:
        views.display_settings()
        settings_option = views.get_str('Enter option', ['1', '0'])
        match settings_option:
            case '1':
                data_manager.set_currency(None)
                logger.info('currency reset by user')
                break

            case '0':
                console.print('Going back to menu', style='bold white')
                break

def main() -> None:
    """
    Main entry function controlling FinanceFlow CLI flow.

    Manages interactive loop:
    1. Retrieves or initializes currency settings.
    2. Displays options menu (1-8).
    3. Processes user input and delegates to DataManager methods.
    """
    console = Console()
    views = Views()
    data_manager = DataManager()
    views.display_welcome_banner()
    currency = data_manager.get_currency()
    while True:
        while currency is None:
            try:
                currency = views.get_currency_from_user()
                data_manager.set_currency(currency)
            except ValueError as e:
                console.print(f'❌ Error: {e}', style='bold red')
                logger.info('Wrong currency entered: %s', e)
        while True:
            try:
                if not data_manager.get_currency():
                    break
                views.display_menu()
                if data_manager.get_limit():
                    views.display_limit()
                menu_option = views.get_str('Enter option', ['1', '2', '3', '4', '0'])

                match menu_option:
                    case '1':
                        expenses_menu(views, data_manager, currency, console)
        
                    case '2':
                        analytics_menu(views, data_manager, currency, console)

                    case '3':
                        budget_menu(views, data_manager, currency, console)

                    case '4':
                        settings_menu(views, data_manager, console)
                        currency = data_manager.get_currency()
                        if currency is None:
                            break
                    case '0':
                        console.print('Closing app...', style='bold dark_blue')
                        logger.info('Aplication closed by user')
                        sys.exit()

            except Exception as e:
                logger.error('Unexpected application error')
                console.print(f'❌ Unexpected error: {e}', style='bold red')

if __name__ == '__main__':
    main()