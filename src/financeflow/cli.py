"""Application setup and top-level loop for the FinanceFlow CLI."""

import sys

from rich.console import Console

from financeflow.cli_menus import (
    analytics_menu,
    budget_menu,
    expenses_menu,
    export_menu,
    settings_menu,
)
from financeflow.config.logging import LoggerConfig
from financeflow.managers.analytics_manager import AnalyticsManager
from financeflow.managers.budget_manager import BudgetManager
from financeflow.managers.data_manager import DataManager
from financeflow.managers.expense_manager import ExpenseManager
from financeflow.managers.export_manager import ExportManager
from financeflow.views import Views

logger = LoggerConfig.get_file_logger(__name__)


def run_cli() -> None:
    """Initialize the application and run the top-level CLI loop."""
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
            
            except KeyboardInterrupt:
                logger.info('App closed by ctrl + c')
                console.print('\nClosing app...', style='bold dark_blue')
                sys.exit()
                            
        while True:
            try:
                if not data_manager.get_currency():
                    break
                views.display_menu()

                menu_option = views.get_str('Enter option', ['1', '2', '3', '4', '5', '0'])

                match menu_option:
                    case '1':
                        assert currency is not None
                        expenses_menu(views, currency, console, budget_manager, expense_manager)

                    case '2':
                        assert currency is not None
                        analytics_menu(views, currency, console, analytics_manager)

                    case '3':
                        assert currency is not None
                        budget_menu(views, currency, console, budget_manager)

                    case '4':
                        settings_menu(views, data_manager, console)
                        currency = data_manager.get_currency()
                        if currency is None:
                            break

                    case '5':
                        assert currency is not None
                        export_menu(views, export_manager, console, currency)

                    case '0':
                        console.print('Closing app...', style='bold dark_blue')
                        logger.info('Aplication closed by user')
                        sys.exit()

            except Exception as e:
                logger.error('Unexpected application error')
                console.print(f'❌ Error: {e.args[0]}', style='bold red')

            except KeyboardInterrupt:
                logger.info('App closed by ctrl + c')
                console.print('\nClosing app...', style='bold dark_blue')
                sys.exit()