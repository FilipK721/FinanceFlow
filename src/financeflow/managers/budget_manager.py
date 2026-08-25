from financeflow.managers.analytics_manager import AnalyticsManager
import json
from datetime import date

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
    
    def percentage_of_the_limit(self) -> int:
        current_month = date.today().month
        all_expenses = self.all_expenses_from_a_given_month(current_month)
        limit = self.get_limit()
        if limit is None or limit == 0:
            return 0
        total_amount = 0
        for expense in all_expenses:
            total_amount += expense['amount']
        return int(total_amount / limit * 100)