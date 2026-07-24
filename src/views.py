from src.data_manager import DataManager
from src.models import Category, Currency
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, FloatPrompt, IntPrompt, Confirm

class Views:
    def __init__(self) -> None:
        self.data_manager = DataManager()
        self.console = Console()

    def show_all_expenses(self, currency: str) -> None:
            """
            Prints all saved expenses to the console.
    
            Args:
                currency (str): Currency symbol/name displayed alongside amounts.
    
            Raises:
                ValueError: If no expenses are found.
            """
            expenses = self.data_manager.load_all_expenses()
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
                for expense in expenses:
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
            "[bold cyan]1.[/bold cyan] ➕ [white]Save expense[/white]\n"
            "[bold cyan]2.[/bold cyan] 📜 [white]Show expenses[/white]\n"
            "[bold cyan]3.[/bold cyan] ✏️  [white]Edit expense[/white]\n"
            "[bold cyan]4.[/bold cyan] 💱 [white]Change currency[/white]\n"
            "[bold cyan]5.[/bold cyan] 📅 [white]Show all expenses from a given month[/white]\n"
            "[bold cyan]6.[/bold cyan] 📊 [white]Get most common expense cateogry[/white]\n"
            "[bold cyan]7.[/bold cyan] 📈 [white]Show month with the highest expenses[/white]\n"
            "[bold red]8.[/bold red] 🔚 [white]Exit[/white]"
        )
        self.console.print(Panel(menu_text, title='[bold green]💸 FinanceFlow Menu 💸[/bold green]'))

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

    def choose_category(self) -> Category:
        self._show_categories()
        categories = [category for category in Category]

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

    def get_str(self, message: str, options: list[str] | None = None) -> str:
        result = Prompt.ask(f'[bold magenta]{message}[/bold magenta]', choices=options)
        return result

    def get_int(self, message: str, options: list[str] | None = None) -> int:
        result = IntPrompt.ask(f'[bold dark_blue]{message}[/bold dark_blue]', choices=options)
        return result

    def confirm(self, message: str) -> bool:
        result = Confirm.ask(
            f'[bold green]{message}[/bold green]'
        )
        return result