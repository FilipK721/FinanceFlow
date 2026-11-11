from io import BytesIO
import json
from decimal import Decimal
from unittest.mock import MagicMock
from urllib.error import URLError

import pytest

from financeflow.currency_rates import get_exchange_rate
from financeflow.models import Currency


def test_get_exchange_rate_uses_current_frankfurter_rate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = BytesIO(
        json.dumps({'rates': {'USD': 1.08}}).encode('utf-8')
    )
    request_mock = MagicMock(return_value=response)
    monkeypatch.setattr('financeflow.currency_rates.urlopen', request_mock)

    rate = get_exchange_rate(Currency.EURO, Currency.DOLLARS)

    assert rate == Decimal('1.08')
    request = request_mock.call_args.args[0]
    assert request.full_url == (
        'https://api.frankfurter.dev/v1/latest?base=EUR&symbols=USD'
    )
    assert request_mock.call_args.kwargs == {'timeout': 10}


def test_get_exchange_rate_returns_one_for_same_currency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    urlopen = MagicMock()
    monkeypatch.setattr('financeflow.currency_rates.urlopen', urlopen)

    assert get_exchange_rate(Currency.PLN, Currency.PLN) == Decimal('1')
    urlopen.assert_not_called()


def test_get_exchange_rate_reports_network_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        'financeflow.currency_rates.urlopen',
        MagicMock(side_effect=URLError('offline')),
    )

    with pytest.raises(RuntimeError, match='Could not retrieve exchange rate'):
        get_exchange_rate(Currency.EURO, Currency.PLN)


@pytest.mark.parametrize(
    ('payload', 'message'),
    [
        ({'rates': {}}, 'did not contain EUR/USD'),
        ({'rates': {'USD': 0}}, 'Invalid exchange rate'),
    ],
)
def test_get_exchange_rate_rejects_missing_or_invalid_rate(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
    message: str,
) -> None:
    response = BytesIO(json.dumps(payload).encode('utf-8'))
    monkeypatch.setattr(
        'financeflow.currency_rates.urlopen',
        MagicMock(return_value=response),
    )

    with pytest.raises(RuntimeError, match=message):
        get_exchange_rate(Currency.EURO, Currency.DOLLARS)
