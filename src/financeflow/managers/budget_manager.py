from financeflow.managers.analytics_manager import AnalyticsManager
from datetime import datetime
import json

class BudgetManager(AnalyticsManager):
    def set_limit(self, limit: float) -> None:
        file_data = self.load_file()
        file_data['limit'] = limit
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(file_data, file, indent=4)

    def get_limit(self) -> float | None:
            file_data = self.load_file()
            return file_data.get('limit', None)
    
    def delete_limit(self) -> None:
        file_data = self.load_file()
        if 'limit' in file_data:
            del file_data['limit']
            with open(self.path, 'w', encoding='utf-8') as file:
                json.dump(file_data, file, indent=4)
        else:
            return
    
    def percantage_of_the_limit(self) -> int:
        current_month = datetime.today().month
        all_expenses = self.all_expenses_from_a_given_month(current_month)
        limit = self.get_limit()
        total_amount = 0
        for expense in all_expenses:
            total_amount += expense['amount']
        return int(total_amount / limit * 100)
