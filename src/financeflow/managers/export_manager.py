"""Export helpers for saving expense data to CSV files."""

from financeflow.managers.data_manager import DataManager
from datetime import datetime
import csv
import os


class ExportManager(DataManager):
    """Export stored expense records to spreadsheet-friendly CSV files."""

    def get_default_export_path(self) -> str:
        """Return the default CSV export path for today's export."""
        data_dir = os.path.dirname(self.path)
        export_dir = os.path.join(data_dir, 'exports')
        os.makedirs(export_dir, exist_ok=True)

        filename = f'expenses_{datetime.now().strftime('%Y-%m-%d-%H-%M')}.csv'
        return os.path.join(export_dir, filename)

    def export_to_csv(self, file_path: str | None = None) -> str:
        """Export all expenses to a CSV file and return its path.

        Args:
            file_path: Optional explicit destination path. If omitted, a timestamped
                file under the exports directory is used.

        Returns:
            The file path where the CSV was written.

        Raises:
            ValueError: If there are no expenses to export.
        """
        expenses = self.load_all_expenses()
        if not expenses:
            raise ValueError('No expenses found')

        if file_path is None:
            file_path = self.get_default_export_path()

        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['name', 'amount', 'category', 'description', 'id', 'date'])
            writer.writeheader()
            for expense in expenses:
                writer.writerow(expense)
        return file_path