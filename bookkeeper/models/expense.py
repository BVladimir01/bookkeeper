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


if __name__ == '__main__':
    a = '2024-03-27'
    b = Expense.MyDate(a)
    print(b)