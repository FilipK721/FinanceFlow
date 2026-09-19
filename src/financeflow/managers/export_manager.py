from financeflow.managers.data_manager import DataManager
from datetime import datetime
import csv
import os

class ExportManager(DataManager):
    def get_default_export_path(self) -> str:
        data_dir = os.path.dirname(self.path)
        export_dir = os.path.join(data_dir, 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        filename = f'expenses_{datetime.now().strftime('%Y-%m-%d-%H:%M')}.csv'
        return os.path.join(export_dir, filename)
        
            
    def export_to_csv(self, file_path: str | None = None) -> None:
        expenses = self.load_all_expenses()
        if not expenses:
            raise ValueError('No expenses found')
        
        if file_path is None:
            file_path = self.get_default_export_path()
        
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'name', 'amount', 'category', 'description', 'id', 'date'])
            writer.writeheader()
            for expense in expenses:
                writer.writerow(expense)