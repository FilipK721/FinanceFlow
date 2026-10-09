import pytest
from financeflow.models import Expense, Category, Currency


class TestExpense:
    def test_raises_error_when_amount_is_negative(self) -> None:
        with pytest.raises(ValueError) as err:
            Expense('A', -5, Category.FUEL, 1, '')

    def test_str(self, sample_expenses) -> None:
        expense = sample_expenses[0]
        str_expense = str(expense)

        if expense.description:
            assert str_expense == f"""name: {expense.name},
amount: {expense.amount},
category: {expense.category},
description:{expense.description},
id: {expense.id},
date: {expense.date}"""
        else:
            assert str_expense == f"""name: {expense.name},
amount: {expense.amount},
category: {expense.category},
id: {expense.id},
date: {expense.date}"""
    
class TestCategory:
    def test_values(self) -> None:
        assert Category.FOOD == 'Food'
        assert Category.GROCERIES == 'Groceries'
        assert Category.HEALTH == 'Health'
        assert Category.ENTERTAINMENT == 'Entertainment'
        assert Category.BILLS == 'Bills'
        assert Category.EDUCATION == 'Education'
        assert Category.FUEL == 'Fuel'
        assert Category.OTHER == 'Other'
        all_categories = Category.get_all_values()
        assert len(all_categories) == 8


class TestCurrency:
    def test_values(self) -> None:
            assert Currency.EURO == 'Euro'
            assert Currency.DOLLARS == 'Dollars'
            assert Currency.POUNDS == 'Pounds'
            assert Currency.YEN == 'Yen'
            assert Currency.PLN == 'Zł'
            all_categories = Currency.get_all_values()
            assert len(all_categories) == 5