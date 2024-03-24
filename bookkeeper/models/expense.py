from dataclasses import dataclass
from datetime import datetime


@dataclass
class Expense:
    """
    Категория расходов, хранит название в
    атрибуте name и ссылку (id) на родителя в
    атрибуте parent (у категорий верхнего
    уровня None).
    """
    amount: int
    category: int
    pk: int = 0
    expense_date: datetime = datetime.now()
    added_date:  datetime = datetime.now()
    comment: str = ''
