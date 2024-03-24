from repository.abstract_repository import AbstractRepository
import sys
from models.category import Category

class Bookkeeper:
    def __init__(self, cat_repo: AbstractRepository = None, bud_repo: AbstractRepository = None, exp_repo: AbstractRepository = None) -> None:
        self.cat_repo = cat_repo
        self.bud_repo = bud_repo
        self.exp_repo = exp_repo


    def add_category(self, name, parent):
        if parent == '':
            parent = None
        cats = self.cat_repo.get_all()
        if name in [c.name for c in cats]:
            raise Exception.ValidationError(
            f'Категория {name} уже существует')
        cat = Category(name, parent)
        self.cat_repo.add(cat)