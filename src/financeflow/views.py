from financeflow.managers.data_manager import DataManager
from financeflow.managers.expense_manager import ExpenseManager
from financeflow.managers.analytics_manager import AnalyticsManager
from financeflow.managers.budget_manager import BudgetManager
from financeflow.models import Category, Currency
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, FloatPrompt, IntPrompt, Confirm

class Views:
    def __init__(self) -> None:
        self.data_manager = DataManager()
        self.budget_manager = BudgetManager()
        self.expense_manager = ExpenseManager()
        self.analytics_manager = AnalyticsManager()
        self.console = Console()

    def show_all_expenses(self, currency: str) -> None:
        """
        Prints all saved expenses to the console.

        Args:
            currency (str): Currency symbol/name displayed alongside amounts.

        Raises:
            ValueError: If no expenses are found.
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
        self.console.clear()

        welcome_text = (
            '[bold green]💰 Welcome to FinanceFlow[/bold green]\n'
            '[dim]Your personal home budget management center[/dim]'
        )
        self.console.print(Panel(welcome_text, border_style="green", expand=False))

    def display_menu(self) -> None:
        menu_text = (
            "\n[bold cyan]1.[/bold cyan] 💰 [white]Expenses[/white]\n\n"
            "[bold cyan]2.[/bold cyan] 📊 [white]Analytics[/white]\n\n"
            "[bold cyan]3.[/bold cyan] 🎯 [white]Budget[/white]\n\n"
            "[bold cyan]4.[/bold cyan] ⚙️ [white] Settings[/white]\n"
            "\n\n[bold red]0.[/bold red] 🔚 [white]Exit[/white]\n"
        )
        self.console.print(Panel(menu_text, title='[bold green]💸 FinanceFlow Menu[/bold green]'))

    def display_expenses_menu(self) -> None:
        menu_text = (
            "\n[bold cyan]1.[/bold cyan] ➕ [white]Add expense[/white]\n\n"
            "[bold cyan]2.[/bold cyan] 📜 [white]Show expenses[/white]\n\n"
            "[bold cyan]3.[/bold cyan] ✏️ [white] Edit expense[/white]\n\n"
            "[bold cyan]4.[/bold cyan] ❌ [white]Delete expense[/white]\n"
            "\n\n[bold red]0.[/bold red] ↩️ [white] Back[/white]\n"
        )
        self.console.print(Panel(menu_text, title='[bold blue]💰 Expenses Menu[/bold blue]'))

    def display_analytics_menu(self) -> None:
        menu_text = (
            "\n[bold cyan]1.[/bold cyan] 📅 [white]Expenses by month[/white]\n\n"
            "[bold cyan]2.[/bold cyan] 📊 [white]Most common category[/white]\n\n"
            "[bold cyan]3.[/bold cyan] 📈 [white]Highest-spending month[/white]\n\n"
            "\n\n[bold red]0.[/bold red] ↩️ [white] Back[/white]\n"
        )
        self.console.print(Panel(menu_text, title='[bold blue]📊 Analytics[/bold blue]'))
    
    def display_budget_menu(self) -> None:
        menu_text = (
            "\n[bold cyan]1.[/bold cyan] 🚨 [white]Set monthly limit[/white]\n\n"
            "[bold cyan]2.[/bold cyan] ↩️ [white]Delete monthly limit[/white]\n"
            "\n\n[bold red]0.[/bold red] ↩️ [white] Back[/white]\n"
        )
        self.console.print(Panel(menu_text, title='[bold blue]🎯 Budget[/bold blue]'))

    def display_settings(self) -> None:
        menu_text = (
            "\n[bold cyan]1.[/bold cyan] 💱 [white]Change currency[/white]\n"
            "\n[bold red]0.[/bold red] ↩️ [white] Back[/white]\n"
        )
        self.console.print(Panel(menu_text, title='[bold blue]⚙️ Settings[/bold blue]'))

    def _show_categories(self) -> None:
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
        amount = FloatPrompt.ask(
            f'[bold green]Enter the amount of expense ({currency})[/bold green]'
        )
        return amount

    def get_str(self, message: str, options: list[str] | None = None, show_choices: bool = True) -> str:
        result = Prompt.ask(f'[bold magenta]{message}[/bold magenta]', choices=options, show_choices=show_choices)
        return result

    def get_int(self, message: str, options: list[str] | None = None, show_choices: bool = True) -> int:
        result = IntPrompt.ask(f'[bold dark_blue]{message}[/bold dark_blue]', choices=options, show_choices=show_choices)
        return result

    def get_limit(self, currency: Currency) -> float:
        return FloatPrompt.ask(f"[bold green]Enter the limit value ({currency})[/bold green]")

    def confirm(self, message: str) -> bool:
        result = Confirm.ask(
            f'[bold green]{message}[/bold green]'
        )
        return result

    def get_currency_from_user(self) -> Currency:
        currencies = Currency.get_all_values()
        currency = Prompt.ask(
            '[bold dark_blue]Enter the currency[/bold dark_blue]',
            choices=currencies,
            default='Euro'
        )
        return Currency(currency)

    def show_all_expenses_in_a_given_month(self, month: int, currency: Currency) -> None:
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
    def display_limit(self) -> None:
        limit_percantage = self.budget_manager.percantage_of_the_limit()
        if 80 <= limit_percantage < 100:
            self.console.print(f'The value of monthly expenses reaached {limit_percantage}% of limit!!', style='bold yellow')
        elif limit_percantage >= 100:
            self.console.print(f'The value of monthly expenses exceeded the limit ({limit_percantage}%)!!!', style='bold red')
        else:
            self.console.print(f'The value of monthly expenses amounts to {limit_percantage}%', style='bright_green')
