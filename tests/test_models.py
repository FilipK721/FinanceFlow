import pytest
from src.models import Expense, Category, assign_id, Currency
from unittest.mock import patch


class TestExpense:
    def test_raises_error_when_amount_is_negative(self) -> None:
        with pytest.raises(ValueError) as err:
            Expense('A', -5, Category.FUEL, 1, '')

    def test_to_dict(self, sample_expenses) -> None:
        dict_expense = sample_expenses[0].to_dict()

        assert 'Pizza' == dict_expense['name']
        assert 40 == dict_expense['amount']
        assert Category.FOOD == dict_expense['category']
        assert '' == dict_expense['description']
        assert 1 == dict_expense['id']
        assert '07-08-2026' == dict_expense['date']
    
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

class TestAssignId:

    @patch('src.data_manager.DataManager.load_all_expenses')
    def test_assign_id_empty_list(self, mock_load):
        mock_load.return_value = []
        
        result = assign_id()
        
        assert result == 1

    @patch('src.data_manager.DataManager.load_all_expenses')
    def test_assign_id_with_existing_expenses(self, mock_load):
        mock_load.return_value = [
            {'id': 5, 'name': 'Zakupy', 'amount': 50.0},
            {'id': 12, 'name': 'Paliwo', 'amount': 200.0},
            {'id': 3, 'name': 'Kino', 'amount': 35.0}
        ]
        
        result = assign_id()
        
        assert result == 13

class TestCurrency:
    def test_values(self) -> None:
            assert Currency.EURO == 'Euro'
            assert Currency.DOLLARS == 'Dollars'
            assert Currency.POUNDS == 'Pounds'
            assert Currency.YEN == 'Yen'
            assert Currency.PLN == 'Zł'
            all_categories = Currency.get_all_values()
            assert len(all_categories) == 5