"""
Main execution module (entry point) for FinanceFlow application.

Launches interactive command-line interface (CLI) allowing users to enter/edit expenses,
set currency, and view financial analytics.
"""

from financeflow.models import Expense, Currency
from financeflow.managers.data_manager import DataManager
from financeflow.managers.expense_manager import ExpenseManager
from financeflow.managers.budget_manager import BudgetManager
from financeflow.managers.analytics_manager import AnalyticsManager
from financeflow.managers.export_manager import ExportManager
from financeflow.views import Views
from datetime import date
import sys
import os
from rich.console import Console
from financeflow.config.logging import LoggerConfig
logger = LoggerConfig.get_file_logger(__name__)

def expenses_menu(views: Views,
                  currency: Currency,
                  console: Console,
                  budget_manager: BudgetManager,
                  expense_manager: ExpenseManager) -> None:
    while True:        
        views.display_expenses_menu()
        expense_option = views.get_str('Enter option', ['1', '2', '3', '4', '0'])
        match expense_option:
            case '1':
                if not budget_manager.make_limits_check():
                    console.print('❌ You have exceeded one of your budget limits! Cannot add new expense.', style='bold red')
                    logger.info('Expense blocked - budget limit exceeded')
                    break

                name = views.get_str('Enter the name of expense')
                amount = views.get_amount(currency)
                description = views.get_str('Enter description (Leave blank to skip)')
                id = expense_manager.assign_id()
                category = views.get_category()
                date_choice = views.confirm('Do you want to enter date? (n to set current date)')
                
                if date_choice == True:
                    expense_date = views.get_date()
                elif date_choice == False:
                    expense_date = date.today().strftime('%d-%m-%Y')
                expense = Expense(name, amount, category, id, expense_date, description)
                expense_manager.save_expense(expense)
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
                ids = sorted(expense_manager.get_all_ids())
                str_ids = [str(id) for id in ids]
                expense_id = views.get_int('Enter id of expense that you want to edit', str_ids)
                expense_manager.edit_expense(expense_id)
                logger.info('Expense edited (id=%s)', expense_id)

            case '4':
                confirmed = views.confirm('Do you want to delete expense?')
                if confirmed == True:
                    views.show_all_expenses(currency)
                    ids = expense_manager.get_all_ids()
                    str_ids = [str(id) for id in ids]
                    expense_id = views.get_int('Enter the id of expense that you want to delete', sorted(str_ids))
                    expense_manager.delete_expense(expense_id)
                    logger.info('Deleted expense with id: %s', expense_id)
                    console.print('✅ Expense deleted successfully!', style='bright_green')
                else:
                    console.print('Coming back to menu', style='bold white')
                    break

            case '0':
                console.print('Going back to menu', style='bold white')
                break

def analytics_menu(views: Views,
                   currency: Currency,
                   console: Console,
                   budget_manager: BudgetManager,
                   analytics_manager: AnalyticsManager) -> None:
    while True:
        views.display_analytics_menu()
        analytics_option = views.get_str('Enter option', ['1', '2', '3', '0'])
        match analytics_option:
            case '1':
    
                month_options = [str(option) for option in range(1, 13)]
                month = views.get_int('Select month (1-12)', options=month_options, show_choices=False)
                views.show_all_expenses_in_a_given_month(month, currency)
                logger.info('Displayed expenses for month %s', month)

            case '2':
                console.print(f'The most common expense category: {analytics_manager.the_most_common_expense_category()}', style='bold blue')
                logger.info('Displayed most common expense category')

            case '3':                
                console.print(analytics_manager.month_with_the_highest_expenses(currency), style='bold blue')
                logger.info('Displayed month with highest expenses')

            case '0':
                console.print('Going back to menu', style='bold white')
                break

def budget_menu(views: Views,
                currency: Currency,
                console: Console,
                budget_manager: BudgetManager) -> None:
    while True:
        views.display_budget_menu()
        budget_option = views.get_str('Enter option', ['1', '2', '3', '4', '0'])
        match budget_option:
            case '1':
                limit = views.get_limit(currency)
                budget_manager.set_limit(limit)
                console.print(f'The limit is set to {limit}', style='bright_green')
                logger.info('User set limit: %s', limit)

            case '2':
                budget_manager.delete_limit()
                console.print('Limit deleted successfully', style='bright_green')
                logger.info('User deleted limit')
            
            case '3':
                category = views.get_category()
                limit = views.get_limit(currency)
                budget_manager.set_limit_for_category(category, limit)
                console.print(f'The {category} limit is set to {limit}', style='bright_green')
                logger.info('User set %s limit: %s', category, limit)
            
            case '4':
                category = views.get_category()
                budget_manager.delete_category_limit(category)
                logger.info('User deleted %s limit', category)

            case '0':
                console.print('Going back to menu', style='bold white')
                break

def export_menu(views: Views, export_manager: ExportManager, console: Console) -> None:
    while True:
        views.display_export_menu()
        export_options = views.get_str('Enter option', ['1', '0'])
        
        match export_options:
            case '1':
                path = export_manager.export_to_csv()
                console.print(f'Exported expenses to {path} successfully', style='bold green')
                logger.info('Exported expenses to: %s', path)
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
    budget_manager = BudgetManager()
    expense_manager = ExpenseManager()
    analytics_manager = AnalyticsManager()
    export_manager = ExportManager()
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
                
                menu_option = views.get_str('Enter option', ['1', '2', '3', '4', '5', '0'])

                match menu_option:
                    case '1':
                        expenses_menu(views, currency, console, budget_manager, expense_manager)
        
                    case '2':
                        analytics_menu(views, currency, console, budget_manager, analytics_manager)

                    case '3':
                        budget_menu(views, currency, console, budget_manager)

                    case '4':
                        settings_menu(views, data_manager, console)
                        currency = data_manager.get_currency()
                        if currency is None:
                            break
                    
                    case '5':
                        export_menu(views, export_manager, console)
                    
                    case '0':
                        console.print('Closing app...', style='bold dark_blue')
                        logger.info('Aplication closed by user')
                        sys.exit()

            except Exception as e:
                logger.error('Unexpected application error')
                console.print(f'❌ Unexpected error: {e}', style='bold red')

if __name__ == '__main__':
    main()
