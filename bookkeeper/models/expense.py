"""
Describes Expense model class
"""


from dataclasses import dataclass
from datetime import date


@dataclass
class Expense:
    """
    Категория расходов, хранит название в
    атрибуте name и ссылку (id) на родителя в
    атрибуте parent (у категорий верхнего
    уровня None).
    """

    pk: int = 0
    amount: int = 0
    category: int = 0
    expense_date: date = date.today()
    added_date:  date = date.today()
    comment: str = ''


    def __post_init__(self):
        """
        extra init procedures for dataclass
        corrects types of __init__ args
        """

        for attr_name, attr_type in self.__annotations__.items():
            value = getattr(self, attr_name)
            if attr_name in ('expense_date', 'added_date'):
                if not isinstance(value, attr_type):
                    setattr(self, attr_name, date.fromisoformat(value))
            else:
                if not isinstance(value, attr_type):
                    setattr(self, attr_name, attr_type(value))
