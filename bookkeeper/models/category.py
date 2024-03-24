from dataclasses import dataclass
from repository.abstract_repository import AbstractRepository

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