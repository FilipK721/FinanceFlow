import pytest
from src.data_manager import DataManager
from src.models import Expense, Category, Currency
import os
import json
from unittest.mock import patch

@pytest.fixture
def sample_manager(fs) -> DataManager:
    manager = DataManager()
    return manager

class TestDataManager:
    def test_data_manager_init(self, sample_manager) -> None:
        assert os.path.exists(sample_manager.path)

        with open(sample_manager.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            assert data == {}

    class TestSaveAllExpenses:
        def test_save_all_expenses_succes(self, sample_manager) -> None:
            expenses = [
                Expense('A', 100, Category.FOOD, 1, 'F').to_dict(),
                Expense('B', 200, Category.FUEL, 2, 'G').to_dict(),
                Expense('C', 300, Category.ENTERTAINMENT, 3, 'V').to_dict()
            ]

            sample_manager.save_all_expenses(expenses)

            with open(sample_manager.path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            assert len(data['expenses']) == 3
            assert data['expenses'] == expenses

        def test_save_all_expenses_propagates_os_error(self, sample_manager) -> None:
            expenses = [Expense('A', 100, Category.FOOD, 1, 'F').to_dict()]

            with patch('builtins.open', side_effect=OSError('No permission')):
                with pytest.raises(OSError) as err:
                    sample_manager.save_all_expenses(expenses)

            assert 'No permission' in str(err.value)

    def test_save_expense(self, sample_manager) -> None:
        expense = Expense('A', 100, Category.FOOD, 1, '26-07-2026')
        sample_manager.save_expense(expense)
        with open(sample_manager.path, 'r') as file:
            data = json.load(file)

        expenses = data['expenses']
        assert expense.to_dict() == expenses[0]

    def test_load_all_expenses(self, sample_manager) -> None:
        expenses = [
            Expense('A', 100, Category.FOOD, 1, 'F').to_dict(),
            Expense('B', 200, Category.FUEL, 2, 'G').to_dict(),
            Expense('C', 300, Category.ENTERTAINMENT, 3, 'V').to_dict()
        ]
        with open(sample_manager.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            data['expenses'] = expenses
        with open(sample_manager.path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

        file_expenses = sample_manager.load_all_expenses()

        assert file_expenses == expenses
        assert len(file_expenses) == 3

    def test_load_file(self, sample_manager) -> None:
        expenses = [Expense('A', 100, Category.FOOD, 1, 'F').to_dict()]

        with open(sample_manager.path, 'w', encoding='utf-8') as file:
            json.dump({'expenses': expenses}, file, indent=4)

        file_data = sample_manager.load_file()

        assert expenses == file_data['expenses']
        assert file_data['expenses'] == expenses

    class TestDeleteExpense:
        def test_delete_expense_succes(self, sample_manager) -> None:
            expense_a = Expense('A', 100, Category.FOOD, 1, 'F').to_dict()
            expense_b = Expense('B', 200, Category.FUEL, 2, 'V').to_dict()
            expenses = [expense_a,
                        expense_b]
            
            with open(sample_manager.path, 'w', encoding='utf-8') as file:
                json.dump({'expenses': expenses}, file, indent=4)

            sample_manager.delete_expense(1)
            with open(sample_manager.path, 'r', encoding='utf-8') as file:
                file_data = json.load(file)

            assert expense_b in file_data['expenses']
            assert expense_a not in file_data['expenses']

        def test_raises_error_when_non_existing_id(self, sample_manager) -> None:
            expense_a = Expense('A', 100, Category.FOOD, 1, 'F').to_dict()
            expense_b = Expense('B', 200, Category.FUEL, 2, 'V').to_dict()
            expenses = [expense_a,
                        expense_b]

            with open(sample_manager.path, 'w', encoding='utf-8') as file:
                json.dump({'expenses': expenses}, file, indent=4)

            with pytest.raises(KeyError, match='Expense id not found'):
                sample_manager.delete_expense(5)

        def test_raises_error_when_no_expenses(self, sample_manager) -> None:
            with open(sample_manager.path, 'r') as file:
                expenses = json.load(file)
            with pytest.raises(ValueError, match='No expenses found'):
                sample_manager.delete_expense(1)
 
    class TestTheMostCommonExpenseCategory:
        def test_the_most_common_expense_category_success(self, sample_manager) -> None:
            expenses = [
        Expense('A', 100, Category.FOOD, 1, 'F').to_dict(),
        Expense('B', 200, Category.FUEL, 2, 'G').to_dict(),
        Expense('C', 150, Category.FOOD, 3, 'V').to_dict()
        ]
            with open(sample_manager.path, 'w', encoding='utf-8') as file:
                json.dump({'expenses': expenses}, file, indent=4)

            the_most_common_category = sample_manager.the_most_common_expense_category()

            assert the_most_common_category == Category.FOOD

        def test_raises_error_due_to_no_expenses(self, sample_manager) -> None:
            with open(sample_manager.path, 'w', encoding='utf-8') as file:
                json.dump({'expenses': []}, file, indent=4)

            with pytest.raises(ValueError, match='No expenses found'):
                sample_manager.the_most_common_expense_category()

    class TestMonthWithTheHighestExpenses:
        def test_month_with_the_highest_expenses_success(self, sample_manager) -> None:
            expenses = [
            Expense('A', 100, Category.FOOD, 1, '22-07-2026').to_dict(),
            Expense('B', 200, Category.FUEL, 2, '01-07-2026').to_dict(),
            Expense('C', 150, Category.FOOD, 3, '01-06-2026').to_dict(),
            Expense('D', 150, Category.FOOD, 4, '01-05-2026').to_dict()
                ]
            with open(sample_manager.path, 'w', encoding='utf-8') as file:
                json.dump({'expenses': expenses}, file, indent=4)

            currency = Currency.EURO
            result = sample_manager.month_with_the_highest_expenses(currency)

            assert result == f'💰 month with the highest expenses: 07-2026 (300.0 {currency})'

        def test_raises_error_due_to_no_expenses(self, sample_manager) -> None:
            currency = Currency.EURO
            with pytest.raises(ValueError, match='No expenses found.'):
                sample_manager.month_with_the_highest_expenses(currency)

    class TestLoadExpenseById:
        def test_load_expense_by_id_succes(self, sample_manager) -> None:
            expense_a = Expense('A', 100, Category.FOOD, 1, 'F').to_dict()
            expense_b = Expense('B', 200, Category.FUEL, 2, 'V').to_dict()
            expenses = [expense_a, expense_b]
            
            with open(sample_manager.path, 'w') as file:
                json.dump({'expenses': expenses}, file)

            expense = sample_manager.load_expense_by_id(2)

            assert expense == expense_b
        
        def test_raises_error_when_wrong_id(self, sample_manager) -> None:
            expense_a = Expense('A', 100, Category.FOOD, 1, 'F').to_dict()
            expense_b = Expense('B', 200, Category.FUEL, 2, 'V').to_dict()
            expenses = [expense_a, expense_b]

            with open(sample_manager.path, 'w') as file:
                json.dump({'expenses': expenses}, file)

            with pytest.raises(ValueError, match='Expense not found'):
                sample_manager.load_expense_by_id(4)

    def test_all_expenses_from_a_given_month(self, sample_manager) -> None:
        expense_a = Expense('A', 100, Category.FOOD, 1, '28-07-2026').to_dict()
        expense_b = Expense('B', 200, Category.FUEL, 2, '01-07-2026').to_dict()
        expense_c = Expense('C', 230, Category.EDUCATION, 3, '03-02-2026').to_dict()
        expenses = [expense_a, expense_b, expense_c]

        with open(sample_manager.path, 'w') as file:
            json.dump({'expenses': expenses}, file)

        expenses_from_a_given_month = sample_manager.all_expenses_from_a_given_month(7)

        assert expenses_from_a_given_month == [expense_a, expense_b]
        assert len(expenses_from_a_given_month) == 2
    
    def test_set_currency(self, sample_manager) -> None:
        currency = Currency.EURO
        with open(sample_manager.path, 'w') as file:
            json.dump({'currency': currency}, file)

        sample_manager.set_currency(Currency.PLN)
        with open(sample_manager.path, 'r') as file:
            data = json.load(file)

        assert data['currency'] == Currency.PLN

    class TestGetCurrency:
        def test_get_currency_success(self, sample_manager) -> None:
            currency = Currency.EURO
            with open(sample_manager.path, 'w') as file:
                json.dump({'currency': currency}, file)

            file_currency = sample_manager.get_currency()

            assert currency == file_currency

        def test_get_currency_returns_none_when_no_saved_currency(self, sample_manager) -> None:
            none = sample_manager.get_currency()
            assert none == None

    class TestGetAllIds:
        def test_get_all_ids_success(self, sample_manager) -> None:
            expense_a = Expense('A', 100, Category.FOOD, 1, '28-07-2026').to_dict()
            expense_b = Expense('B', 200, Category.FUEL, 2, '01-07-2026').to_dict()
            expense_c = Expense('C', 230, Category.EDUCATION, 3, '03-02-2026').to_dict()
            expenses = [expense_a, expense_b, expense_c]

            with open(sample_manager.path, 'w') as file:
                json.dump({'expenses': expenses}, file)

            all_ids = sample_manager.get_all_ids()
            assert all_ids == [1, 2, 3]
        def test_raises_error_due_to_no_expense(self, sample_manager) -> None:
            with pytest.raises(ValueError, match='No expenses found'):
                sample_manager.get_all_ids()