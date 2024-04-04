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
    class MyDate(date):
        def __new__(cls, date_str: str = '') -> None:
            return date.fromisoformat(date_str)
        

    pk: int = 0
    amount: int = None
    category: int = None
    expense_date: MyDate = date.today()
    added_date:  MyDate = date.today()
    comment: str = ''

    def __post_init__(self):
        for attr_name, attr_type in self.__annotations__.items():
            value = getattr(self, attr_name)
            if type(value) != attr_type:
                setattr(self, attr_name, attr_type(value)) 

if __name__ == '__main__':
    a = '2024-03-27'
    b = Expense.MyDate(a)
    print(b)

    test_obj = Expense(pk='1', amount='10', category='12', expense_date='2024-12-11', added_date='2024-12-11', comment=12)
    print(test_obj)