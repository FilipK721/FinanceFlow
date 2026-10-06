"""Console view layer for the FinanceFlow CLI application."""

from financeflow.managers.data_manager import DataManager
from financeflow.managers.expense_manager import ExpenseManager
from financeflow.managers.analytics_manager import AnalyticsManager
from sqlalchemy.orm import Session
from financeflow.models import Category, Currency
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, FloatPrompt, IntPrompt, Confirm
from datetime import date
import plotext as plt


class Views:
    """Render the interactive terminal UI and collect user input."""

    def __init__(self, session: Session | None = None) -> None:
        """Initialize the CLI view layer and its supporting managers."""
        self.data_manager = DataManager(session=session)
        from financeflow.managers.budget_manager import BudgetManager
        self.budget_manager = BudgetManager(session=self.data_manager.session)
        self.expense_manager = ExpenseManager(session=self.data_manager.session)
        self.analytics_manager = AnalyticsManager(session=self.data_manager.session)
        self.console = Console()

    def show_all_expenses(self, currency: str) -> None:
        """Display every saved expense in a table.

        Args:
            currency: Currency label shown alongside the amounts.

        Raises:
            ValueError: If there are no stored expenses.
        """
        expenses = self.expense_manager.load_all_expenses()
        if not expenses:
            raise ValueError('No expenses found!')
        else:
            table = Table(title=f'📊 Expenses ({currency})')
            table.add_column("Name", style="bold")
            table.add_column("Amount", justify="right", style="green")
            table.add_column("Description")
            table.add_column("Category", style="magenta")
            table.add_column("Id", style="cyan", justify="center")
            table.add_column("Date", justify="center")
            sorted_expenses = sorted(expenses, key=lambda expense: expense['id'])
            for expense in sorted_expenses:
                table.add_row(
                    expense['name'],
                    f"{expense['amount']:.2f}",
                    expense["description"],
                    expense['category'],
                    str(expense['id']),
                    expense['date']
                )
            self.console.print(table)

    def display_welcome_banner(self) -> None:
        """Render the application's startup banner."""
        self.console.clear()

        welcome_text = (
            '[bold green]💰 Welcome to FinanceFlow[/bold green]\n'
            '[dim]Your personal home budget management center[/dim]'
        )
        self.console.print(Panel(welcome_text, border_style="green", expand=False))

    def display_menu(self) -> None:
        """Show the main FinanceFlow menu with active budget limits."""
        menu_text = (
            "\n[bold cyan]1.[/bold cyan] 💰 [white]Expenses[/white]\n\n"
            "[bold cyan]2.[/bold cyan] 📊 [white]Analytics[/white]\n\n"
            "[bold cyan]3.[/bold cyan] 🎯 [white]Budget[/white]\n\n"
            "[bold cyan]4.[/bold cyan] ⚙️ [white] Settings[/white]\n"
            "\n[bold cyan]5.[/bold cyan] 📤 [white]Export[/white]\n"
            "\n\n[bold red]0.[/bold red] 🔚 [white]Exit[/white]\n"
        )
        limits_text = self._build_limits_text()

        grid = Table.grid(expand=True, padding=(0, 2))
        grid.add_column(ratio=2)
        grid.add_column(ratio=1)
        grid.add_row(menu_text, limits_text)
        self.console.print(Panel(grid, title='[bold green]💸 FinanceFlow Menu[/bold green]'))

    def display_expenses_menu(self) -> None:
        """Show the expense-management submenu."""
        menu_text = (
            "\n[bold cyan]1.[/bold cyan] ➕ [white]Add expense[/white]\n\n"
            "[bold cyan]2.[/bold cyan] 📜 [white]Show expenses[/white]\n\n"
            "[bold cyan]3.[/bold cyan] ✏️ [white] Edit expense[/white]\n\n"
            "[bold cyan]4.[/bold cyan] ❌ [white]Delete expense[/white]\n"
            "\n\n[bold red]0.[/bold red] ↩️ [white] Back[/white]\n"
        )
        self.console.print(Panel(menu_text, title='[bold blue]💰 Expenses Menu[/bold blue]'))

    def display_analytics_menu(self) -> None:
        """Show the analytics submenu."""
        menu_text = (
            "\n[bold cyan]1.[/bold cyan] 📅 [white]Expenses by month[/white]\n\n"
            "[bold cyan]2.[/bold cyan] 🍔 [white]Most common category[/white]\n\n"
            "[bold cyan]3.[/bold cyan] 📈 [white]Highest-spending month[/white]\n\n"
            "[bold cyan]4.[/bold cyan] 📊 [white]Show category bar chart[/white]\n\n"
            "[bold cyan]5.[/bold cyan] 📉 [white]Show monthly trend chart[/white]\n\n"
            "\n\n[bold red]0.[/bold red] ↩️ [white] Back[/white]\n"
        )
        self.console.print(Panel(menu_text, title='[bold blue]📊 Analytics[/bold blue]'))

    def display_budget_menu(self) -> None:
        """Show the budget-management submenu."""
        menu_text = (
            "\n[bold cyan]1.[/bold cyan] 🚨 [white]Set monthly limit[/white]\n\n"
            "[bold cyan]2.[/bold cyan] ❌ [white]Delete monthly limit[/white]\n\n"
            "[bold cyan]3.[/bold cyan] 📊 [white]Set category limit for[/white]\n\n"
            "[bold cyan]4.[/bold cyan] ╳ [white]Delete category limit[/white]\n\n"
            "\n\n[bold red]0.[/bold red] ↩️ [white] Back[/white]\n"
        )
        self.console.print(Panel(menu_text, title='[bold blue]🎯 Budget[/bold blue]'))

    def display_settings(self) -> None:
        """Show the settings submenu."""
        menu_text = (
            "\n[bold cyan]1.[/bold cyan] 💱 [white]Change currency[/white]\n"
            "\n[bold red]0.[/bold red] ↩️ [white] Back[/white]\n"
        )
        self.console.print(Panel(menu_text, title='[bold blue]⚙️ Settings[/bold blue]'))

    def display_export_menu(self) -> None:
        """Show the export submenu."""
        menu_text = (
            '\n[bold cyan]1.[/bold cyan] 🧮 [white]Export to CSV file[/white]'
            '\n\n[bold red]0.[/bold red] ↩️ [white] Back[/white]\n'
        )
        self.console.print(Panel(menu_text, title='[bold green]📤 Export[/bold green]'))

    def _show_categories(self) -> None:
        """Print all available expense categories for user selection."""
        self.console.print('[bold blue]Categories:[/bold blue]')
        self.console.print(f'[cyan]•[/cyan]{Category.FOOD} 🍔')
        self.console.print(f'[cyan]•[/cyan]{Category.GROCERIES} 🛒')
        self.console.print(f'[cyan]•[/cyan]{Category.HEALTH} 💊')
        self.console.print(f'[cyan]•[/cyan]{Category.ENTERTAINMENT} 🎭')
        self.console.print(f'[cyan]•[/cyan]{Category.BILLS} 🧾')
        self.console.print(f'[cyan]•[/cyan]{Category.EDUCATION} 📖')
        self.console.print(f'[cyan]•[/cyan]{Category.FUEL} ⛽️')
        self.console.print(f'[cyan]•[/cyan]{Category.OTHER} 🔚')

    def get_category(self) -> Category:
        """Prompt the user to choose an expense category.

        Returns:
            The selected category as a Category enum member.
        """
        self._show_categories()
        categories = Category.get_all_values()

        result = Prompt.ask(
            '[bold magenta]Enter the category[/bold magenta]',
            choices=categories,
            default='Other',
            show_choices=False
        )

        return Category(result)

    def get_amount(self, currency: Currency) -> float:
        """Prompt for an expense amount in the configured currency."""
        amount = FloatPrompt.ask(
            f'[bold green]Enter the amount of expense ({currency})[/bold green]'
        )
        return amount

    def get_str(self, message: str, options: list[str] | None = None, show_choices: bool = True) -> str:
        """Prompt the user for a string value or menu choice."""
        result = Prompt.ask(f'[bold magenta]{message}[/bold magenta]', choices=options, show_choices=show_choices)
        return result

    def get_int(self, message: str, options: list[str] | None = None, show_choices: bool = True) -> int:
        """Prompt the user for an integer value or menu option."""
        result = IntPrompt.ask(f'[bold dark_blue]{message}[/bold dark_blue]', choices=options, show_choices=show_choices)
        return result

    def get_limit(self, currency: Currency) -> float:
        """Prompt the user to input a budget limit value."""
        return FloatPrompt.ask(f"[bold green]Enter the limit value ({currency})[/bold green]")

    def confirm(self, message: str) -> bool:
        """Prompt the user for a yes/no confirmation."""
        result = Confirm.ask(
            f'[bold green]{message}[/bold green]'
        )
        return result

    def get_currency_from_user(self) -> Currency:
        """Prompt the user to choose the default application currency."""
        currencies = Currency.get_all_values()
        currency = Prompt.ask(
            '[bold dark_blue]Enter the currency[/bold dark_blue]',
            choices=currencies,
            default='Euro'
        )
        return Currency(currency)

    def show_all_expenses_in_a_given_month(self, month: int, currency: Currency) -> None:
        """Display all expenses recorded in a selected month."""
        all_expenses_from_a_given_month = self.analytics_manager.all_expenses_from_a_given_month(month)
        if not all_expenses_from_a_given_month:
            self.console.print('No expenses in a given month found!', style='red')
            return
        table = Table(title=f'📊 Expenses ({currency})')
        table.add_column("Name", style="bold")
        table.add_column("Amount", justify="right", style="green")
        table.add_column("Description")
        table.add_column("Category", style="magenta")
        table.add_column("Id", style="cyan", justify="center")
        table.add_column("Date", justify="center")
        sorted_expenses = sorted(all_expenses_from_a_given_month, key=lambda expense: expense['id'])
        for expense in sorted_expenses:
            table.add_row(
                expense['name'],
                f"{expense['amount']:.2f}",
                expense["description"],
                expense['category'],
                str(expense['id']),
                expense['date']
            )
        self.console.print(table)

    def _build_limits_text(self) -> str:
        """Build a summary string showing current budget-limit usage."""
        lines = ['[bold blue]🎯 Limits[/bold blue]\n']

        for category in Category:
            limit = self.budget_manager.get_category_limit(category)
            if limit is None or limit == 0:
                continue
            percentage = self.budget_manager.percentage_of_category_limit(category)
            if percentage >= 100:
                lines.append(f'[bold red]{category}: {percentage}%[/bold red]')
            elif percentage >= 80:
                lines.append(f'[bold yellow]{category}: {percentage}%[/bold yellow]')
            else:
                lines.append(f'[green]{category}: {percentage}%[/green]')

        monthly_percentage = self.budget_manager.percentage_of_the_limit()
        limit = self.budget_manager.get_limit()
        if limit is not None and limit != 0:
            lines.append('')
            if monthly_percentage >= 100:
                lines.append(f'[bold red]Monthly: {monthly_percentage}%[/bold red]')
            elif monthly_percentage >= 80:
                lines.append(f'[bold yellow]Monthly: {monthly_percentage}%[/bold yellow]')
            else:
                lines.append(f'[green]Monthly: {monthly_percentage}%[/green]')

        if len(lines) == 1:
            lines.append('[dim]No limits set[/dim]')

        return '\n'.join(lines)

    def get_date(self) -> str:
        """Prompt the user for a valid date and return it as DD-MM-YYYY."""
        current_year = date.today().year

        while True:
            year = self.get_int('Enter year', show_choices=False)
            if 1900 <= year <= current_year:
                break
            self.console.print(f'❌ Year must be between 1900 and {current_year}. Try again.', style='bold red')

        while True:
            day = self.get_int('Enter day (1-31)', [str(i) for i in range(1, 32)], show_choices=False)
            month = self.get_int('Enter month (1-12)', [str(i) for i in range(1, 13)], show_choices=False)
            try:
                return date(year, month, day).strftime('%d-%m-%Y')
            except ValueError:
                self.console.print('❌ Invalid date (e.g. day doesn\'t exist in that month). Try again.', style='bold red')

    def show_category_bar_chart(self, currency: Currency) -> None:
        """Display a categorized spending chart for the current data set."""
        totals = self.analytics_manager.spending_by_category()

        labels = list(totals.keys())
        values = list(totals.values())

        plt.clf()
        plt.theme('dark')
        plt.simple_bar(labels, values, width=80, title=f'💸 Spending by category ({currency})')
        plt.show()
        plt.clf()

    def show_monthly_trend_chart(self, currency: Currency) -> None:
        """Display a monthly spending trend chart."""
        totals = self.analytics_manager.spending_by_month()

        months = list(totals.keys())
        amounts = list(totals.values())
        x_positions = list(range(1, len(months) + 1))

        plt.clf()
        plt.theme('clear')
        plt.plot(x_positions, amounts, marker='braille')
        plt.xticks(x_positions, months)
        plt.title(f'📈 Monthly spending trend ({currency})')
        plt.plotsize(80, 20)
        plt.show()
        plt.clf()