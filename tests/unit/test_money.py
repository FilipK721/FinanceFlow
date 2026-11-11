from decimal import Decimal

import pytest
from sqlalchemy.dialects.sqlite import dialect

from financeflow.money import MinorUnitAmount, decimal_amount


@pytest.mark.parametrize(
    ('value', 'places', 'expected'),
    [
        ('1.005', 2, Decimal('1.01')),
        ('12.5', 0, Decimal('13')),
        ('12.4', 0, Decimal('12')),
    ],
)
def test_decimal_amount_rounds_half_up(
    value: str,
    places: int,
    expected: Decimal,
) -> None:
    assert decimal_amount(value, places) == expected


@pytest.mark.parametrize('value', ['not-a-number', 'NaN', 'Infinity'])
def test_decimal_amount_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        decimal_amount(value)


def test_decimal_amount_rejects_negative_precision() -> None:
    with pytest.raises(ValueError, match='Decimal places cannot be negative'):
        decimal_amount('1', -1)


def test_minor_unit_type_round_trips_exact_decimal_values() -> None:
    amount_type = MinorUnitAmount()

    assert amount_type.process_bind_param(Decimal('12.34'), dialect()) == 1234
    assert amount_type.process_result_value(1234, dialect()) == Decimal('12.34')
    assert amount_type.process_bind_param(None, dialect()) is None
    assert amount_type.process_result_value(None, dialect()) is None
