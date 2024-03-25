from dataclasses import dataclass
from bookkeeper.repository.abstract_repository import AbstractRepository
from typing import List

@dataclass
class Category:
    """
    Категория расходов, хранит название в
    атрибуте name и ссылку (id) на родителя в
    атрибуте parent (у категорий верхнего
    уровня None).
    """
    name: str
    parent: int | None = None
    pk: int = 0

    def get_parent(self, repo: AbstractRepository['Category']) -> 'Category | None':
        """return parent object from repository"""
        if self.parent is None:
            return None
        return repo.get(self.parent)
    
    def get_children(self, repo: AbstractRepository['Category']) -> 'List[Category] | None':
        res = repo.get_all({'parent': self.pk})
        return res