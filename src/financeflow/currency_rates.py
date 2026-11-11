"""Fetch current exchange rates from the Frankfurter API."""

from decimal import Decimal, InvalidOperation
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from financeflow.models import Currency

def get_exchange_rate(base: Currency, quote: Currency) -> Decimal:
    """Return the latest rate for one supported currency unit to another."""
    if base == quote:
        return Decimal('1')

    base_code = base.value
    quote_code = quote.value
    url = (
        'https://api.frankfurter.dev/v1/latest'
        f'?base={base_code}&symbols={quote_code}'
    )
    request = Request(url, headers={'Accept': 'application/json'})
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f'Could not retrieve exchange rate from {base_code} to {quote_code}'
        ) from error

    try:
        rate = Decimal(str(payload['rates'][quote_code]))
    except (KeyError, TypeError, InvalidOperation) as error:
        raise RuntimeError(
            f'Exchange rate response did not contain {base_code}/{quote_code}'
        ) from error

    if not rate.is_finite() or rate <= 0:
        raise RuntimeError(f'Invalid exchange rate for {base_code}/{quote_code}')
    return rate
