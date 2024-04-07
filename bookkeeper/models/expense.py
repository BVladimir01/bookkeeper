from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Expense:
    
    """
    Категория расходов, хранит название в
    атрибуте name и ссылку (id) на родителя в
    атрибуте parent (у категорий верхнего
    уровня None).
    """
    pk: int = 0
    amount: int = None
    category: int = 0
    expense_date: date = date.today()
    added_date:  date = date.today()
    comment: str = ''

    def __post_init__(self):
        for attr_name, attr_type in self.__annotations__.items():
            value = getattr(self, attr_name)
            if attr_name == 'expense_date' or attr_name == 'added_date':
                if type(value)  != attr_type:
                    setattr(self, attr_name, date.fromisoformat(value))
            else:
                if type(value)  != attr_type:
                    setattr(self, attr_name, attr_type(value)) 


if __name__ == '__main__':
    test_obj = Expense(pk='1', amount='10', category='12', expense_date='2024-12-11', added_date='2024-12-11', comment=12)
    print(test_obj)