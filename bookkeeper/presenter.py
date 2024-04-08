from repository.abstract_repository import AbstractRepository
from repository.sqlite_repository import SQLiteRepository
from models.budget import Budget
from models.category import Category
from models.expense import Expense
from PySide6 import QtWidgets
import sys
from view.view import MyWindow
from view import abstract_view

from datetime import date, timedelta

class Presenter:
    def __init__(self, cat_repo: AbstractRepository, bud_repo: AbstractRepository, exp_repo: AbstractRepository,
                 cat_class: Category, budget_class: Budget, exp_class: Expense, view: abstract_view) -> None:
        

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
        self.view.register_exp_category_change(self.change_expense_category)
        self.update_expenses()

        self.view.register_budget_change(self.change_budget)
        self.count_expenses()
        self.update_budgets()
        
        self.view.register_update_categories(self.update_categories)
        self.view.register_category_change(self.change_category)
        self.view.register_category_add(self.add_category)
        self.view.register_category_delete(self.delete_category)
        self.view.register_children_getter(self.get_category_children)
        self.view.register_parent_getter(self.get_category_parent)


    def add_expense(self, attr_val_dict):
        exp = self.exp_class(**attr_val_dict)
        self.exp_repo.add(exp)
        self.update_expenses()


    def delete_expense(self, pk):
        self.exp_repo.delete(pk=pk)
        self.update_expenses()


    def change_expense(self, attr_val_dict):
        new_obj = self.exp_class(**attr_val_dict)
        self.exp_repo.update(new_obj)
        self.update_expenses()


    def change_expense_category(self, *args):
        print('changing category in presenter')


    def update_expenses(self):
        expenses = self.exp_repo.get_all()
        categories = []
        for exp in expenses:
            cat_pk = exp.category
            categories.append(self.cat_repo.get(cat_pk))
        self.view.update_expenses(expenses, categories)
        self.count_expenses()


    def count_expenses(self):
        expenses = []
        today = date.today()
        day_delta = timedelta(days=1)
        for num_days in range(30):
            day = today - num_days*day_delta
            entries = self.exp_repo.get_all(where={'expense_date': str(day)})
            expenses = expenses + entries
        
        day_expense = 0
        for expense in expenses:
            if expense.expense_date <= today - day_delta: break
            day_expense += expense.amount


        week_expense = 0
        for expense in expenses:
            if expense.expense_date <= today - 7*day_delta: break
            week_expense += expense.amount

        month_expense = sum(map(lambda x: getattr(x, 'amount'), expenses))

        self.view.display_expenses((day_expense, week_expense, month_expense))
    

    def update_budgets(self):
        day = self.bud_repo.get_all(where={'time_period': 'День'})[0]
        week = self.bud_repo.get_all(where={'time_period': 'Неделя'})[0]
        month = self.bud_repo.get_all(where={'time_period': 'Месяц'})[0]
        self.view.update_budgets((day, week, month))


    def change_budget(self, attr_val_dict):
        new_obj = self.budget_class(**attr_val_dict)
        self.bud_repo.update(new_obj)
        self.update_budgets()


    def update_categories(self):
        categories = self.cat_repo.get_all()
        self.view.update_categories(categories)


    def change_category(self, attr_val_dict: dict):
        old_object = self.cat_repo.get(attr_val_dict['pk'])
        if not 'parent' in attr_val_dict.keys():
            attr_val_dict['parent'] = old_object.parent
        new_obj = self.cat_class(**attr_val_dict)
        self.cat_repo.update(new_obj)
        self.update_categories()


    def add_category(self, attr_val_dict):
        new_obj = self.cat_class(**attr_val_dict)
        self.cat_repo.add(new_obj)
        self.update_categories()


    def delete_category(self, pk, transfer):
        deleting_obj = self.cat_repo.get(pk)
        new_parent_pk = int(deleting_obj.parent)

        def manage_expenses(deleting_pk):
            suffered_expenses = self.exp_repo.get_all(where={'category': int(deleting_pk)})

            for expense in suffered_expenses:
                attr_val_dict = {'pk': expense.pk,
                                'amount': expense.amount,
                                'category': new_parent_pk,
                                'expense_date': expense.expense_date,
                                'added_date': expense.added_date,
                                'comment': expense.comment}
                self.change_expense(attr_val_dict)

        if not transfer:
            def delete_obj_in_tree(obj):
                children = obj.get_children(self.cat_repo)
                if children:
                    for child in children:
                        delete_obj_in_tree(child)
                manage_expenses(obj.pk)
                self.cat_repo.delete(obj.pk)

            delete_obj_in_tree(deleting_obj)
        else:
            children = deleting_obj.get_children(self.cat_repo)
            for child in children:
                attr_val_dict = {'pk': child.pk, 'name': child.name, 'parent': new_parent_pk}
                self.change_category(attr_val_dict)
            manage_expenses(deleting_obj.pk)
            self.cat_repo.delete(deleting_obj.pk)
    

        self.update_categories()
        self.update_expenses()


    def get_category_children(self, pk):
        obj = self.cat_repo.get(pk)
        children = obj.get_children(self.cat_repo)
        return children


    def get_category_parent(self, pk):
        obj = self.cat_repo.get(pk)
        parent_pk = obj.parent
        return parent_pk
    

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