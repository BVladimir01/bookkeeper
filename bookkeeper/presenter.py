from repository.abstract_repository import AbstractRepository
import sys



class Bookkeeper:
    def __init__(self, cat_repo: AbstractRepository, bud_repo: AbstractRepository, exp_repo: AbstractRepository,
                 cat_class, budget_class, exp_class) -> None:
        self.cat_class = cat_class
        self.budget_class = budget_class
        self.exp_class = exp_class
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
        cat = self.cat_class(name, parent)
        self.cat_repo.add(cat)

    
    def cat_list_to_tree_like(self):
        pass
        

def insert_list(list):
    pass