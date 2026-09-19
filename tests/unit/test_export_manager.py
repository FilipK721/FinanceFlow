from financeflow.managers.export_manager import ExportManager
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
from financeflow.models import Expense
import pytest
import os

class TestExportManager:
    @patch('financeflow.managers.export_manager.os.makedirs')
    @patch('financeflow.managers.export_manager.datetime')
    def test_creates_exports_directory(self, mock_datetime: MagicMock, mock_makedirs: MagicMock, sample_export_manager: ExportManager) -> None:
        mock_datetime.now.return_value = datetime(2026, 9, 19, 14, 30)
        
        result = sample_export_manager.get_default_export_path()
        
        expected_dir = os.path.join(os.path.dirname(sample_export_manager.path), 'exports')
        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)
        assert result == os.path.join(expected_dir, 'expenses_2026-09-19-14:30.csv')
    
    @patch('financeflow.managers.export_manager.datetime')
    def test_returns_path_inside_exports_directory(self, mock_datetime: MagicMock, sample_export_manager: ExportManager) -> None:
        mock_datetime.now.return_value = datetime(2026, 9, 19, 14, 30)
        
        result = sample_export_manager.get_default_export_path()
        
        expected_dir = os.path.join(os.path.dirname(sample_export_manager.path), 'exports')
        
        assert os.path.dirname(result) == expected_dir
    
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
