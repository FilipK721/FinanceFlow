"""Persistence helpers for application settings and expense records."""

from decimal import Decimal

from financeflow.models import Currency
from financeflow.db.engine import get_db_path, get_session_local
from financeflow.db.models import CategoryLimitRow, SettingRow, ExpenseRow
from sqlalchemy.orm import Session
from rich.console import Console
from financeflow.config.logging import LoggerConfig
from financeflow.currency_rates import get_exchange_rate
from financeflow.money import decimal_amount

logger = LoggerConfig.get_file_logger(__name__)


class DataManager:
    """Manage database-backed settings and expense data for the application."""

    def __init__(self, session: Session | None = None) -> None:
        if session is None:
            self.session = get_session_local()()
        else:
            self.session = session
        self.path = get_db_path()
        self.console = Console()

    def set_currency(self, currency: Currency | None) -> None:
        """Persist the selected currency or remove it when no currency is provided.

        Args:
            currency: The currency to store, or None to delete the saved setting.
        """
        try:
            existing = self.session.get(SettingRow, 'currency')

            if currency is None:
                if self._has_financial_amounts():
                    raise ValueError(
                        'Cannot remove the currency while financial amounts exist'
                    )
                if existing is not None:
                    self.session.delete(existing)
            else:
                previous_currency = (
                    Currency(existing.value) if existing is not None else None
                )
                if previous_currency is not None and previous_currency != currency:
                    rate = get_exchange_rate(previous_currency, currency)
                    self._convert_financial_amounts(rate)
                elif previous_currency is None and self._has_financial_amounts():
                    raise ValueError(
                        'Cannot convert existing amounts because their currency is unknown'
                    )

                if existing is not None:
                    existing.value = currency.value
                else:
                    self.session.add(SettingRow(key='currency', value=currency.value))

            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def _has_financial_amounts(self) -> bool:
        """Return whether amounts exist without a known currency."""
        return (
            self.session.query(ExpenseRow).first() is not None
            or self.session.query(CategoryLimitRow).first() is not None
            or self.session.get(SettingRow, 'limit') is not None
        )

    def _convert_financial_amounts(self, rate: Decimal) -> None:
        """Convert stored expenses and budget limits using the supplied rate."""
        for expense in self.session.query(ExpenseRow).all():
            expense.amount = decimal_amount(expense.amount * rate)

        for category_limit in self.session.query(CategoryLimitRow).all():
            category_limit.limit = decimal_amount(category_limit.limit * rate)

        monthly_limit = self.session.get(SettingRow, 'limit')
        if monthly_limit is not None:
            converted_limit = decimal_amount(Decimal(monthly_limit.value) * rate)
            monthly_limit.value = str(converted_limit)

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