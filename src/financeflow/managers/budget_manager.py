from financeflow.managers.analytics_manager import AnalyticsManager
from financeflow.models import Category
from financeflow.views import Views
import json
from datetime import date

class BudgetManager(AnalyticsManager):
    def set_limit(self, limit: float) -> None:
        file_data = self.load_file()
        file_data['limit'] = limit
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(file_data, file, indent=4)
    
    def set_limit_for_category(self, category: Category, limit: float) -> None:
        file_data = self.load_file()
        category_limits = file_data['category_limits']
        category_limits[category.value] = limit
        
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(file_data, file, indent=4)
    
    def get_category_limit(self, category: Category) -> float | None:
        file_data = self.load_file()
        category_limits = file_data.get('category_limits', {})
        return category_limits.get(category, None)
    
    def delete_category_limit(self, category: Category) -> None:
        file_data = self.load_file()
        category_limits = file_data.get('category_limits', None)
        if category_limits:
            if category_limits.get(category, None) is None:
                self.console.print(f'{category} limit for not found', style='red')
            else:
                category_limits[category] = None
                with open(self.path, 'w', encoding='utf-8') as file:
                    json.dump(file_data, file, indent=4)
                self.console.print(f'{category} limit deleted successfully', style='bright_green')

    def get_limit(self) -> float | None:
            file_data = self.load_file()
            return file_data.get('limit', None)
    
    def make_limits_check(self) -> bool:
        categories = Category.get_all_values()
        
        if self.get_limit():
            if self.percentage_of_the_limit() >= 100:
                return False
        for category in categories:
            if self.get_category_limit(category) is not None:
                if self.get_percentage_of_category_limit(category) >= 100:
                    return False
        return True
    
    def delete_limit(self) -> None:
        file_data = self.load_file()
        if 'limit' in file_data:
            file_data['limit'] = None
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
    
    def get_percentage_of_category_limit(self, category: Category) -> int:
        current_month = date.today().month
        all_expenses = self.all_expenses_from_a_given_month(current_month)
        limit = self.get_category_limit(category)
        if limit is None or limit == 0:
            return 0
        total_amount = 0
        for expense in all_expenses:
            if expense['category'] == category:
                total_amount += expense['amount']
        return int(total_amount / limit * 100)