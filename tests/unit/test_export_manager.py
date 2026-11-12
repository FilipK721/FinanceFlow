from datetime import date, datetime
from decimal import Decimal
import os
from unittest.mock import MagicMock, mock_open, patch

from openpyxl import load_workbook
import pytest

from financeflow.managers.export_manager import ExportManager
from financeflow.models import Currency, Expense

class TestExportManager:
    @patch('financeflow.managers.export_manager.os.makedirs')
    @patch('financeflow.managers.export_manager.datetime')
    def test_creates_exports_directory(self, mock_datetime: MagicMock, mock_makedirs: MagicMock, sample_export_manager: ExportManager) -> None:
        mock_datetime.now.return_value = datetime(2026, 9, 19, 14, 30)
        
        result = sample_export_manager.get_default_export_path()
        
        expected_dir = os.path.join(os.path.dirname(sample_export_manager.path), 'exports')
        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)
        assert result == os.path.join(expected_dir, 'expenses_2026-09-19_14-30.csv')
    
    @patch('financeflow.managers.export_manager.datetime')
    def test_returns_path_inside_exports_directory(self, mock_datetime: MagicMock, sample_export_manager: ExportManager) -> None:
        mock_datetime.now.return_value = datetime(2026, 9, 19, 14, 30)
        
        result = sample_export_manager.get_default_export_path()
        
        expected_dir = os.path.join(os.path.dirname(sample_export_manager.path), 'exports')
        
        assert os.path.dirname(result) == expected_dir

    @patch('financeflow.managers.export_manager.os.makedirs')
    @patch('financeflow.managers.export_manager.datetime')
    def test_creates_default_xlsx_export_path(
        self,
        mock_datetime: MagicMock,
        mock_makedirs: MagicMock,
        sample_export_manager: ExportManager,
    ) -> None:
        mock_datetime.now.return_value = datetime(2026, 9, 19, 14, 30)

        result = sample_export_manager.get_default_xlsx_export_path()

        expected_dir = os.path.join(os.path.dirname(sample_export_manager.path), 'exports')
        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)
        assert result == os.path.join(expected_dir, 'expenses_2026-09-19_14-30.xlsx')
    
    @patch('financeflow.managers.export_manager.ExportManager.load_all_expenses')
    def test_raises_value_error_when_no_expenses(self, mock_load_all_expenses, sample_export_manager: ExportManager) -> None:
        mock_load_all_expenses.return_value = []
        with pytest.raises(ValueError, match='No expenses found'):
            sample_export_manager.export_to_csv()
    
    def test_export_uses_default_path_when_none_given(self, sample_export_manager: ExportManager, sample_expenses: list[Expense]) -> None:
        sample_export_manager.load_all_expenses = MagicMock(
        return_value=[vars(e) for e in sample_expenses]
        )
        sample_export_manager.get_default_export_path = MagicMock(
        return_value='/fake/path/expenses_test.csv'
        )

        with patch('financeflow.managers.export_manager.open', mock_open()) as mocked_open, \
        patch('financeflow.managers.export_manager.csv.DictWriter') as mock_writer_class:

            result = sample_export_manager.export_to_csv()

        sample_export_manager.get_default_export_path.assert_called_once()
        mocked_open.assert_called_once_with('/fake/path/expenses_test.csv', 'w', newline='', encoding='utf-8')
        assert result == '/fake/path/expenses_test.csv'

    def test_xlsx_export_contains_formatted_numeric_expenses_and_totals(
        self,
        tmp_path,
        sample_export_manager: ExportManager,
    ) -> None:
        sample_export_manager.load_all_expenses = MagicMock(
            return_value=[
                {
                    'date': date(2026, 8, 7),
                    'name': 'Coffee',
                    'category': 'Food',
                    'description': 'Morning coffee',
                    'id': 42,
                    'amount': Decimal('12.34'),
                },
                {
                    'date': date(2026, 8, 8),
                    'name': 'Lunch',
                    'category': 'Food',
                    'description': '',
                    'id': 43,
                    'amount': Decimal('5.66'),
                },
            ]
        )
        path = tmp_path / 'report.xlsx'

        result = sample_export_manager.export_to_xlsx(str(path), Currency.EURO)

        workbook = load_workbook(result, data_only=False)
        worksheet = workbook['Expenses']
        assert worksheet['A1'].value == 'FinanceFlow — Expense Report'
        assert 'Currency: EUR (€)' in worksheet['A2'].value
        assert worksheet['A4'].value == 'EXPENSES'
        assert worksheet['B4'].value == 2
        assert worksheet['D4'].value == 'TOTAL SPENDING'
        assert worksheet['E4'].value == '=SUM(F7:F8)'
        assert [worksheet.cell(row=6, column=column).value for column in range(1, 7)] == [
            'Date', 'Name', 'Category', 'Description', 'ID', 'Amount',
        ]
        assert worksheet['A7'].value.date() == date(2026, 8, 7)
        assert worksheet['B7'].value == 'Coffee'
        assert worksheet['F7'].value == 12.34
        assert worksheet['F7'].data_type == 'n'
        assert worksheet['F7'].number_format == '#,##0.00 "€";[Red]-#,##0.00 "€"'
        assert worksheet['F9'].value == '=SUM(F7:F8)'
        assert worksheet['E9'].value == 'TOTAL'
        assert worksheet.freeze_panes == 'A7'
        assert list(worksheet.tables) == ['ExpenseRecords']
        assert worksheet.tables['ExpenseRecords'].ref == 'A6:F8'
        assert worksheet.tables['ExpenseRecords'].autoFilter.ref == 'A6:F8'
        assert worksheet['A6'].fill.fgColor.rgb.endswith('168C83')
        assert worksheet.column_dimensions['D'].width == 38
        assert worksheet.sheet_view.showGridLines is False

    def test_xlsx_export_uses_zero_decimal_format_for_yen(
        self,
        tmp_path,
        sample_export_manager: ExportManager,
    ) -> None:
        sample_export_manager.load_all_expenses = MagicMock(
            return_value=[
                {
                    'date': date(2026, 8, 7),
                    'name': 'Transit',
                    'category': 'Other',
                    'description': '',
                    'id': 1,
                    'amount': Decimal('1200'),
                },
            ]
        )
        path = tmp_path / 'yen.xlsx'

        sample_export_manager.export_to_xlsx(str(path), Currency.YEN)

        worksheet = load_workbook(path)['Expenses']
        assert worksheet['F7'].value == 1200
        assert worksheet['F7'].number_format == '#,##0 "¥";[Red]-#,##0 "¥"'

    def test_xlsx_export_raises_when_no_expenses(
        self,
        sample_export_manager: ExportManager,
    ) -> None:
        sample_export_manager.load_all_expenses = MagicMock(return_value=[])

        with pytest.raises(ValueError, match='No expenses found'):
            sample_export_manager.export_to_xlsx(currency=Currency.EURO)

    def test_xlsx_export_requires_configured_currency(
        self,
        tmp_path,
        sample_export_manager: ExportManager,
    ) -> None:
        sample_export_manager.load_all_expenses = MagicMock(
            return_value=[
                {
                    'date': date(2026, 8, 7),
                    'name': 'Coffee',
                    'category': 'Food',
                    'description': '',
                    'id': 1,
                    'amount': Decimal('12.34'),
                },
            ]
        )
        sample_export_manager.get_currency = MagicMock(return_value=None)

        with pytest.raises(ValueError, match='Currency is not configured'):
            sample_export_manager.export_to_xlsx(str(tmp_path / 'no-currency.xlsx'))
