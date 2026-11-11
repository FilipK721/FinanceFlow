from unittest.mock import MagicMock

import pytest
from financeflow import cli
from financeflow.models import Currency


def test_run_cli_dispatches_each_menu_choice(
    monkeypatch: pytest.MonkeyPatch,
    cli_dependencies: tuple[MagicMock, MagicMock],
) -> None:
    views, _ = cli_dependencies
    views.get_str.side_effect = ['1', '2', '3', '4', '5', '0']
    menu_handlers = {
        'expenses_menu': MagicMock(),
        'analytics_menu': MagicMock(),
        'budget_menu': MagicMock(),
        'settings_menu': MagicMock(),
        'export_menu': MagicMock(),
    }
    for name, handler in menu_handlers.items():
        monkeypatch.setattr(cli, name, handler)

    with pytest.raises(SystemExit):
        cli.run_cli()

    for handler in menu_handlers.values():
        handler.assert_called_once()


def test_changing_currency_converts_and_persists_the_selection(
    cli_dependencies: tuple[MagicMock, MagicMock],
) -> None:
    views, data_manager = cli_dependencies
    data_manager.get_currency.side_effect = [
        Currency.EURO,
        Currency.EURO,
        Currency.PLN,
        Currency.PLN,
    ]
    views.get_str.side_effect = ['4', '1', '0']
    views.get_currency_from_user.return_value = Currency.PLN

    with pytest.raises(SystemExit):
        cli.run_cli()

    views.get_currency_from_user.assert_called_once()
    data_manager.set_currency.assert_called_once_with(Currency.PLN)


def test_run_cli_retries_after_invalid_currency(
    cli_dependencies: tuple[MagicMock, MagicMock],
) -> None:
    views, _ = cli_dependencies
    cli.DataManager.return_value.get_currency.side_effect = [
        None,
        Currency.EURO,
    ]
    views.get_currency_from_user.side_effect = [
        ValueError('Unsupported currency'),
        Currency.EURO,
    ]
    views.get_str.return_value = '0'
    console = cli.Console.return_value

    with pytest.raises(SystemExit):
        cli.run_cli()

    assert views.get_currency_from_user.call_count == 2
    console.print.assert_any_call(
        '❌ Error: Unsupported currency',
        style='bold red',
    )


def test_run_cli_returns_to_setup_when_currency_is_missing(
    cli_dependencies: tuple[MagicMock, MagicMock],
) -> None:
    views, data_manager = cli_dependencies
    data_manager.get_currency.side_effect = [
        Currency.EURO,
        None,
        Currency.EURO,
    ]
    views.get_str.return_value = '0'

    with pytest.raises(SystemExit):
        cli.run_cli()

    views.display_menu.assert_called_once()


def test_run_cli_reports_unexpected_menu_errors(
    cli_dependencies: tuple[MagicMock, MagicMock],
) -> None:
    views, _ = cli_dependencies
    views.get_str.side_effect = [RuntimeError('Menu input failed'), '0']
    console = cli.Console.return_value

    with pytest.raises(SystemExit):
        cli.run_cli()

    console.print.assert_any_call(
        '❌ Error: Menu input failed',
        style='bold red',
    )
