from datetime import date
from unittest.mock import MagicMock

import pytest

from financeflow import cli_menus
from financeflow.models import Category, Currency, Expense


def test_expenses_menu_adds_expense(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
) -> None:
    views, console, budget_manager, expense_manager, _ = menu_dependencies
    budget_manager.make_limits_check.return_value = True
    expense_manager.assign_id.return_value = 12
    views.get_str.side_effect = ['1', 'Coffee', 'Morning coffee', '0']
    views.get_amount.return_value = 4.5
    views.get_category.return_value = Category.FOOD
    views.confirm.return_value = False

    cli_menus.expenses_menu(views, Currency.EURO, console, budget_manager, expense_manager)

    expense = expense_manager.save_expense.call_args.args[0]
    assert isinstance(expense, Expense)
    assert (expense.name, expense.amount, expense.category, expense.id) == (
        'Coffee',
        4.5,
        Category.FOOD,
        12,
    )
    assert expense.date == date.today()
    assert expense.description == 'Morning coffee'


def test_expenses_menu_blocks_add_when_budget_limit_is_exceeded(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
) -> None:
    views, console, budget_manager, expense_manager, _ = menu_dependencies
    budget_manager.make_limits_check.return_value = False
    views.get_str.return_value = '1'

    cli_menus.expenses_menu(views, Currency.EURO, console, budget_manager, expense_manager)

    expense_manager.save_expense.assert_not_called()
    console.print.assert_called_once()


def test_expenses_menu_saves_user_entered_date(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
) -> None:
    views, console, budget_manager, expense_manager, _ = menu_dependencies
    budget_manager.make_limits_check.return_value = True
    expense_manager.assign_id.return_value = 13
    views.get_str.side_effect = ['1', 'Lunch', 'With friends', '0']
    views.get_amount.return_value = 18.0
    views.get_category.return_value = Category.FOOD
    views.confirm.return_value = True
    views.get_date.return_value = date(2026, 10, 15)

    cli_menus.expenses_menu(views, Currency.EURO, console, budget_manager, expense_manager)

    expense = expense_manager.save_expense.call_args.args[0]
    assert expense.date == date(2026, 10, 15)
    views.get_date.assert_called_once()


def test_expenses_menu_displays_all_expenses(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
) -> None:
    views, _, budget_manager, _, _ = menu_dependencies
    views.get_str.side_effect = ['2', '0']

    cli_menus.expenses_menu(views, Currency.EURO, MagicMock(), budget_manager, MagicMock())

    views.show_all_expenses.assert_called_once_with(Currency.EURO)


def test_expenses_menu_edits_selected_expense(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
) -> None:
    views, _, budget_manager, expense_manager, _ = menu_dependencies
    views.get_str.side_effect = ['4', '0']
    views.get_int.return_value = 7
    expense_manager.get_all_ids.return_value = [7, 2]

    cli_menus.expenses_menu(views, Currency.EURO, MagicMock(), budget_manager, expense_manager)

    views.get_int.assert_called_once_with(
        'Enter id of expense that you want to edit',
        ['2', '7'],
    )
    expense_manager.edit_expense.assert_called_once_with(7)


def test_expenses_menu_searches_and_displays_matching_expenses(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
) -> None:
    views, _, budget_manager, expense_manager, _ = menu_dependencies
    criteria = {'text': 'coffee', 'sort_by': 'name', 'descending': False}
    results = [{'name': 'Coffee', 'id': 1}]
    views.get_str.side_effect = ['3', '0']
    views.get_search_criteria.return_value = criteria
    expense_manager.search_expenses.return_value = results

    cli_menus.expenses_menu(views, Currency.EURO, MagicMock(), budget_manager, expense_manager)

    expense_manager.search_expenses.assert_called_once_with(**criteria)
    views.show_expenses_table.assert_called_once_with(results, Currency.EURO)


def test_expenses_menu_reports_when_search_has_no_matches(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
) -> None:
    views, console, budget_manager, expense_manager, _ = menu_dependencies
    views.get_str.side_effect = ['3', '0']
    views.get_search_criteria.return_value = {'text': 'missing'}
    expense_manager.search_expenses.return_value = []

    cli_menus.expenses_menu(views, Currency.EURO, console, budget_manager, expense_manager)

    console.print.assert_any_call('No expenses found!', style='red')
    views.show_expenses_table.assert_not_called()


def test_expenses_menu_deletes_confirmed_expense(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
) -> None:
    views, console, budget_manager, expense_manager, _ = menu_dependencies
    views.get_str.side_effect = ['5', '0']
    views.confirm.return_value = True
    views.get_int.return_value = 3
    expense_manager.get_all_ids.return_value = [3]

    cli_menus.expenses_menu(views, Currency.EURO, console, budget_manager, expense_manager)

    expense_manager.delete_expense.assert_called_once_with(3)
    console.print.assert_any_call('✅ Expense deleted successfully!', style='bright_green')


def test_expenses_menu_returns_without_deleting_when_cancelled(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
) -> None:
    views, console, budget_manager, expense_manager, _ = menu_dependencies
    views.get_str.return_value = '5'
    views.confirm.return_value = False

    cli_menus.expenses_menu(views, Currency.EURO, console, budget_manager, expense_manager)

    expense_manager.delete_expense.assert_not_called()
    console.print.assert_called_once_with('Coming back to menu', style='bold white')


@pytest.mark.parametrize(
    ('option', 'expected_action'),
    [
        ('1', 'month'),
        ('2', 'common_category'),
        ('3', 'highest_month'),
        ('4', 'category_chart'),
        ('5', 'monthly_chart'),
    ],
)
def test_analytics_menu_dispatches_selected_action(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
    option: str,
    expected_action: str,
) -> None:
    views, console, _, _, analytics_manager = menu_dependencies
    views.get_str.side_effect = [option, '0']
    views.get_int.return_value = 6
    analytics_manager.the_most_common_expense_category.return_value = 'Food'
    analytics_manager.month_with_the_highest_expenses.return_value = 'August'

    cli_menus.analytics_menu(views, Currency.EURO, console, analytics_manager)

    if expected_action == 'month':
        views.show_all_expenses_in_a_given_month.assert_called_once_with(6, Currency.EURO)
    elif expected_action == 'common_category':
        analytics_manager.the_most_common_expense_category.assert_called_once()
        console.print.assert_any_call(
            'The most common expense category: Food',
            style='bold blue',
        )
    elif expected_action == 'highest_month':
        analytics_manager.month_with_the_highest_expenses.assert_called_once_with(Currency.EURO)
        console.print.assert_any_call('August', style='bold blue')
    elif expected_action == 'category_chart':
        views.show_category_bar_chart.assert_called_once_with(Currency.EURO)
    else:
        views.show_monthly_trend_chart.assert_called_once_with(Currency.EURO)


@pytest.mark.parametrize(
    ('option', 'expected_action'),
    [
        ('1', 'set_limit'),
        ('2', 'delete_limit'),
        ('3', 'set_category_limit'),
        ('4', 'delete_category_limit'),
    ],
)
def test_budget_menu_dispatches_selected_action(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
    option: str,
    expected_action: str,
) -> None:
    views, console, budget_manager, _, _ = menu_dependencies
    views.get_str.side_effect = [option, '0']
    views.get_limit.return_value = 250.0
    views.get_category.return_value = Category.FOOD

    cli_menus.budget_menu(views, Currency.EURO, console, budget_manager)

    if expected_action == 'set_limit':
        budget_manager.set_limit.assert_called_once_with(250.0)
    elif expected_action == 'delete_limit':
        budget_manager.delete_limit.assert_called_once()
    elif expected_action == 'set_category_limit':
        budget_manager.set_limit_for_category.assert_called_once_with(Category.FOOD, 250.0)
    else:
        budget_manager.delete_category_limit.assert_called_once_with(Category.FOOD)


def test_export_menu_exports_csv(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
) -> None:
    views, console, _, _, export_manager = menu_dependencies
    views.get_str.side_effect = ['1', '0']
    export_manager.export_to_csv.return_value = '/tmp/expenses.csv'

    cli_menus.export_menu(views, export_manager, console, Currency.EURO)

    export_manager.export_to_csv.assert_called_once()
    console.print.assert_any_call(
        'Exported expenses to /tmp/expenses.csv successfully',
        style='bold green',
    )


def test_export_menu_exports_xlsx(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
) -> None:
    views, console, _, _, export_manager = menu_dependencies
    views.get_str.side_effect = ['2', '0']
    export_manager.export_to_xlsx.return_value = '/tmp/expenses.xlsx'

    cli_menus.export_menu(views, export_manager, console, Currency.PLN)

    export_manager.export_to_xlsx.assert_called_once_with(currency=Currency.PLN)
    console.print.assert_any_call(
        'Exported Excel report to /tmp/expenses.xlsx successfully',
        style='bold green',
    )


@pytest.mark.parametrize(('option', 'should_change'), [('1', True), ('0', False)])
def test_settings_menu_changes_currency_only_when_selected(
    menu_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock, MagicMock],
    option: str,
    should_change: bool,
) -> None:
    views, console, _, _, data_manager = menu_dependencies
    views.get_str.return_value = option
    views.get_currency_from_user.return_value = Currency.PLN

    cli_menus.settings_menu(views, data_manager, console)

    if should_change:
        data_manager.set_currency.assert_called_once_with(Currency.PLN)
        console.print.assert_not_called()
    else:
        data_manager.set_currency.assert_not_called()
        views.get_currency_from_user.assert_not_called()
        console.print.assert_called_once()
