"""Convert persisted financial amounts between supported currencies."""

from decimal import Decimal
from typing import Callable

from sqlalchemy.orm import Session

from financeflow.currency_rates import get_exchange_rate
from financeflow.db.models import CategoryLimitRow, ExpenseRow, SettingRow
from financeflow.models import Currency
from financeflow.money import decimal_amount


class CurrencyConversionManager:
    """Apply current exchange rates to expenses and budget limits."""

    def __init__(
        self,
        session: Session,
        rate_provider: Callable[[Currency, Currency], Decimal] = get_exchange_rate,
    ) -> None:
        self.session = session
        self.rate_provider = rate_provider

    def convert_amounts(self, source: Currency, target: Currency) -> None:
        """Convert all stored financial amounts to the target currency.

        The caller owns the database transaction and must commit or roll back.
        """
        rate = self.rate_provider(source, target)

        for expense in self.session.query(ExpenseRow).all():
            expense.amount = decimal_amount(
                expense.amount * rate,
                target.decimal_places,
            )

        for category_limit in self.session.query(CategoryLimitRow).all():
            category_limit.limit = decimal_amount(
                category_limit.limit * rate,
                target.decimal_places,
            )

        monthly_limit = self.session.get(SettingRow, 'limit')
        if monthly_limit is not None:
            converted_limit = decimal_amount(
                Decimal(monthly_limit.value) * rate,
                target.decimal_places,
            )
            monthly_limit.value = str(converted_limit)
