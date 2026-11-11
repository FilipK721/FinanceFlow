"""Exact decimal handling for persisted monetary amounts."""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from sqlalchemy import Integer
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

MONEY_DECIMAL_PLACES = 2
MINOR_UNITS_PER_UNIT = 100


def decimal_amount(
    value: Decimal | float | int | str,
    decimal_places: int = MONEY_DECIMAL_PLACES,
) -> Decimal:
    """Convert a numeric amount to a finite decimal at the requested precision."""
    if decimal_places < 0:
        raise ValueError('Decimal places cannot be negative')
    try:
        amount = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f'Invalid monetary amount: {value}') from error
    if not amount.is_finite():
        raise ValueError('Monetary amount must be finite')
    quantum = Decimal(1).scaleb(-decimal_places)
    return amount.quantize(quantum, rounding=ROUND_HALF_UP)


class MinorUnitAmount(TypeDecorator[Decimal]):
    """Store decimal amounts as integer minor units in SQLite."""

    impl = Integer
    cache_ok = True

    def process_bind_param(
        self,
        value: Decimal | float | int | str | None,
        dialect: Dialect,
    ) -> int | None:
        if value is None:
            return None
        return int(decimal_amount(value) * MINOR_UNITS_PER_UNIT)

    def process_result_value(self, value: int | None, dialect: Dialect) -> Decimal | None:
        if value is None:
            return None
        return (Decimal(value) / MINOR_UNITS_PER_UNIT).quantize(
            Decimal('0.01')
        )
