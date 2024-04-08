"""
Describes Category model class
"""


from dataclasses import dataclass
from typing import List
from repository.abstract_repository import AbstractRepository


@dataclass
class Category:
    """
    Категория расходов, хранит название в
    атрибуте name и ссылку (id) на родителя в
    атрибуте parent (у категорий верхнего
    уровня None).
    """

    pk: int = 0
    name: str = ''
    parent: int = 0


    def __post_init__(self):
        """
        extra init procedures for dataclass
        corrects types of __init__ args
        """
        for attr_name, attr_type in self.__annotations__.items():
            value = getattr(self, attr_name)
            if not isinstance(value, attr_type):
                setattr(self, attr_name, attr_type(value))


    def get_parent(self, repo: AbstractRepository['Category']) -> 'Category | None':
        """
        return parent object from repository
        """
        if self.parent == 0:
            return None
        return repo.get(self.parent)


    def get_children(self, repo: AbstractRepository['Category']) -> 'List[Category] | None':
        """
        returns child category objects of given object
        """
        res = repo.get_all({'parent': self.pk})
        return res
