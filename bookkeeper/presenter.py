from repository.abstract_repository import AbstractRepository
from repository.sqlite_repository import SQLiteRepository
from models.budget import Budget
from models.category import Category
from models.expense import Expense
from PySide6 import QtWidgets
import sys
from view.view import MyWindow


class Presenter:
    def __init__(self, cat_repo: AbstractRepository, bud_repo: AbstractRepository, exp_repo: AbstractRepository,
                 cat_class: Category, budget_class: Budget, exp_class: Expense, view: QtWidgets.QWidget) -> None:
        

        self.col_headers = ['pk', 'expense_date', 'amount', 'category', 'comment']
        self.tranlator = {i:j for i, j in zip("pk Дата Сумма category Комментарий".split(), self.col_headers)}
    
        self.cat_class = cat_class
        self.budget_class = budget_class
        self.exp_class = exp_class
        self.cat_repo = cat_repo
        self.bud_repo = bud_repo
        self.exp_repo = exp_repo
        self.view = view

        self.view.register_exp_add(self.add_expense)
        self.view.register_exp_delete(self.delete_expense)
        self.view.register_exp_change(self.change_expense)
        self.update_expenses()


    def add_expense(self, expense_date, amount, category, comment, added_date = None):
        if added_date:
            exp = Expense(amount=amount, category=category, expense_date=expense_date, comment=comment, added_date=added_date)
        else:
            exp = Expense(amount=amount, category=category, expense_date=expense_date, comment=comment)
        self.exp_repo.add(exp)
        self.update_expenses()


    def delete_expense(self, pk):
        self.exp_repo.delete(pk=pk)
        self.update_expenses()


    def change_expense(self, attr_val_dict):
        new_obj = self.exp_class(**attr_val_dict)
        self.exp_repo.update(new_obj)
        self.update_expenses()


    def update_expenses(self):
        expenses = self.exp_repo.get_all()
        categories = []
        for exp in expenses:
            cat_pk = exp.category
            categories.append(self.cat_repo.get(cat_pk))
        self.view.update_expenses(expenses, categories)


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


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    window = MyWindow()
    cat_repo = SQLiteRepository('D:\\физтех\\proga\\bookkeeper_project\\tests\\test_db.db', Category)
    budget_repo = SQLiteRepository('D:\\физтех\\proga\\bookkeeper_project\\tests\\test_db.db', Budget)
    expense_repo = SQLiteRepository('D:\\физтех\\proga\\bookkeeper_project\\tests\\test_db.db', Expense)
    presenter = Presenter(cat_repo=cat_repo, bud_repo=budget_repo, exp_repo=expense_repo,
                          cat_class=Category, budget_class=Budget, exp_class=Expense, view=window)
    window.show()
    sys.exit(app.exec())