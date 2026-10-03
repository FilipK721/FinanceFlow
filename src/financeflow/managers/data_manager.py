"""Persistence helpers for application settings and expense records."""

from financeflow.models import Currency
from financeflow.db.engine import SessionLocal, get_db_path
from financeflow.db.models import SettingRow, ExpenseRow
from rich.console import Console
from financeflow.config.logging import LoggerConfig

logger = LoggerConfig.get_file_logger(__name__)


class DataManager:
    """Manage database-backed settings and expense data for the application."""

    def __init__(self) -> None:
        """Create a database session and initialize runtime state used by the manager."""
        self.session = SessionLocal()
        self.path = get_db_path()
        self.console = Console()

    def set_currency(self, currency: Currency | None) -> None:
        """Persist the selected currency or remove it when no currency is provided.

        Args:
            currency: The currency to store, or None to delete the saved setting.
        """
        existing = self.session.get(SettingRow, 'currency')

        if currency is None:
            if existing is not None:
                self.session.delete(existing)
        else:
            if existing is not None:
                existing.value = currency.value

            else:
                new_setting = SettingRow(key='currency', value=currency.value)
                self.session.add(new_setting)

        self.session.commit()

    def get_currency(self) -> Currency | None:
        """Return the saved app currency if one has been configured."""
        existing = self.session.get(SettingRow, 'currency')
        if existing is not None:
            return Currency(existing.value)
        return None

    def load_all_expenses(self) -> list[dict]:
        """Return all expense rows as dictionaries suitable for UI or API usage.

        Returns:
            A list of expense records containing the stored fields for each row.
        """
        rows = self.session.query(ExpenseRow).all()

        expenses = []
        for row in rows:
            expenses.append({
                'name': row.name,
                'amount': row.amount,
                'category': row.category,
                'description': row.description,
                'id': row.id,
                'date': row.date
            })

        return expenses