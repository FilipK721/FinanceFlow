from enum import StrEnum

class Category(StrEnum):
    FOOD = 'Food'
    GROCERIES = 'Groceries'
    HEALTH = 'Health'
    ENTERTAINMENT = 'Entertainment'
    UTILITIES = 'Utilities'
    EDUCATION = 'Education'
    OTHER = 'Other'

class Currency(StrEnum):
    EURO = 'Euro'
    DOLLARS = 'Dollars'
    POUNDS = 'Pounds'
    YEN = 'Yen'
    ZŁ = 'Zł'

class Expense:
    def __init__(self, name: str, amount: float, category: Category, id: int, date: str, description: str | None = None) -> None:
        self.name = name
        self.amount = amount
        self.category = category
        self.id = id
        self.date = date
        self.description = description

    def to_dict(self) -> dict[str, int | str | Category | float | None]:
        return {'name': self.name,
                'amount': float(self.amount),
                'category': self.category,
                'description': self.description,
                'id': self.id,
                'date': self.date
                }
    
    def __str__(self) -> str:
        if self.description:
            return f'name: {self.name},\namount: {self.amount},\ncategory: {self.category},\ndescription:\n{self.description},\nid: {self.id},\ndate: {self.date}'
        else:
            return f'name: {self.name},\namount: {self.amount},\ncategory: {self.category},\nid: {self.id},\ndate: {self.date}'


def assign_id() -> int:
    from src.data_manager import DataManager
    data_manager = DataManager()
    expenses = data_manager.load_all_expenses()
    
    if not expenses:
        return 1
    
    max_id = 0
    for expense in expenses:
        if expense['id'] > max_id:
            max_id = expense['id']
            
    return max_id + 1