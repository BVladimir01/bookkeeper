"""
Describes Presenter class
If called opens application
"""


import sys
from datetime import date, timedelta
from PySide6 import QtWidgets
from repository.abstract_repository import AbstractRepository
from repository.sqlite_repository import SQLiteRepository
from models.budget import Budget
from models.category import Category
from models.expense import Expense
from view.view import MyWindow
from view import abstract_view


class Presenter:
    """
    Presenter class
    binds repository and view
    Declares all method for managing them
    """

    def __init__(self, cat_repo: AbstractRepository, bud_repo: AbstractRepository,
                 exp_repo: AbstractRepository, cat_class: Category, budget_class: Budget,
                 exp_class: Expense, view: abstract_view) -> None:

        self.cat_class = cat_class
        self.budget_class = budget_class
        self.exp_class = exp_class
        self.cat_repo = cat_repo
        self.bud_repo = bud_repo
        self.exp_repo = exp_repo
        self.view = view

        self.initiate_budget_repo()

        self.view.register_exp_add(self.add_expense)
        self.view.register_exp_delete(self.delete_expense)
        self.view.register_exp_change(self.change_expense)
        self.update_expenses()

        self.view.register_budget_change(self.change_budget)
        self.count_expenses()
        self.update_budgets()

        self.view.register_update_categories(self.update_categories)
        self.view.register_category_change(self.change_category)
        self.view.register_category_add(self.add_category)
        self.view.register_category_delete(self.delete_category)

        self.view.register_update_all(self.update_all)


    def initiate_budget_repo(self):
        """
        Initiates budget repo with 3 entries
        (since no option to add new entries)
        """
        for time_period in ('День', 'Неделя', 'Месяц'):
            if not self.bud_repo.get_all(where={'time_period': time_period}):
                obj = self.budget_class(time_period=time_period)
                self.bud_repo.add(obj)


    def add_expense(self, attr_val_dict: dict):
        """
        Adds new entry of expense to repo
        attr_val_argument is a dict of arguments {key: value}
        calls update_expenses
        """
        if 'amount' in attr_val_dict.keys():
            amount = attr_val_dict['amount']
            try:
                int(amount)
            except ValueError:
                raise ValueError('Сумма должна быть целым числом')
            if int(amount) != float(amount):
                raise ValueError('Сумма должна быть целым числом')
            if int(amount) < 0:
                raise ValueError('Сумма должна быть неотрицательной')
        if 'expense_date' in attr_val_dict.keys():
            expense_date = attr_val_dict['expense_date']
            try:
                date.fromisoformat(expense_date)
            except ValueError:
                raise ValueError('Укажите дату в формате YYYY-MM-DD')
        exp = self.exp_class(**attr_val_dict)
        self.exp_repo.add(exp)
        self.update_expenses()


    def delete_expense(self, pk: int | str):
        """
        Deletes expense entry with id=pk from repo
        calls update_expenses
        """
        self.exp_repo.delete(pk=pk)
        self.update_expenses()


    def change_expense(self, attr_val_dict: dict):
        """
        Updates expense entry with new obj
        attr_val_argument is a dict of arguments
        {key: value} for new obj
        calls update_expenses
        """
        if 'amount' in attr_val_dict.keys():
            amount = attr_val_dict['amount']
            try:
                int(amount)
            except ValueError:
                raise ValueError('Сумма должна быть целым числом')
            if int(amount) != float(amount):
                raise ValueError('Сумма должна быть целым числом')
            if int(amount) < 0:
                raise ValueError('Сумма должна быть неотрицательной')
        if 'expense_date' in attr_val_dict.keys():
            expense_date = attr_val_dict['expense_date']
            try:
                if not isinstance(expense_date, date):
                    date.fromisoformat(expense_date)
            except ValueError:
                raise ValueError('Укажите дату в формате YYYY-MM-DD')
        new_obj = self.exp_class(**attr_val_dict)
        self.exp_repo.update(new_obj)
        self.update_expenses()


    def update_expenses(self):
        """
        Gets expenses from repo
        Calls function to update
        expenses in view (user interface)
        """
        expenses = self.exp_repo.get_all()
        categories = []
        for exp in expenses:
            cat_pk = exp.category
            categories.append(self.cat_repo.get(cat_pk))
        self.view.update_expenses(expenses, categories)
        self.count_expenses()


    def count_expenses(self):
        """
        Counts expenses, calls function to
        display it in view(user interface)
        """
        expenses = []
        today = date.today()
        day_delta = timedelta(days=1)
        for num_days in range(30):
            day = today - num_days*day_delta
            entries = self.exp_repo.get_all(where={'expense_date': str(day)})
            expenses = expenses + entries

        day_expense = 0
        for expense in expenses:
            if expense.expense_date <= today - day_delta:
                break
            day_expense += expense.amount


        week_expense = 0
        for expense in expenses:
            if expense.expense_date <= today - 7*day_delta:
                break
            week_expense += expense.amount

        month_expense = sum(map(lambda x: getattr(x, 'amount'), expenses))

        self.view.display_expenses((day_expense, week_expense, month_expense))


    def update_budgets(self):
        """
        Gets budgets from repo
        Calls function to update
        budgets in view (user interface)
        """
        day = self.bud_repo.get_all(where={'time_period': 'День'})[0]
        week = self.bud_repo.get_all(where={'time_period': 'Неделя'})[0]
        month = self.bud_repo.get_all(where={'time_period': 'Месяц'})[0]
        self.view.update_budgets((day, week, month))


    def change_budget(self, attr_val_dict):
        """
        Updates budget entry with new obj
        attr_val_argument is a dict of arguments
        {key: value} for new obj
        calls update_budgets
        """
        if 'amount' in attr_val_dict.keys():
            amount = attr_val_dict['amount']
            try:
                int(amount)
            except ValueError:
                raise ValueError('Сумма должна быть целым числом')
            if int(amount) != float(amount):
                raise ValueError('Сумма должна быть целым числом')
            if int(amount) < 0:
                raise ValueError('Сумма должна быть неотрицательной')
        new_obj = self.budget_class(**attr_val_dict)
        self.bud_repo.update(new_obj)
        self.update_budgets()


    def update_categories(self):
        """
        Gets categories from repo
        Calls function to update
        budgets in view (user interface)
        """
        categories = self.cat_repo.get_all()
        self.view.update_categories(categories)


    def change_category(self, attr_val_dict: dict):
        """
        Updates category entry with new obj
        attr_val_argument is a dict of arguments
        {key: value} for new obj
        calls update_categories
        """
        old_object = self.cat_repo.get(attr_val_dict['pk'])
        if not 'parent' in attr_val_dict.keys():
            attr_val_dict['parent'] = old_object.parent
        new_obj = self.cat_class(**attr_val_dict)
        self.cat_repo.update(new_obj)
        self.update_categories()


    def add_category(self, attr_val_dict: dict):
        """
        Adds new entry of category to repo
        attr_val_argument is a dict of arguments {key: value}
        calls update_categories
        """
        new_obj = self.cat_class(**attr_val_dict)
        self.cat_repo.add(new_obj)
        self.update_categories()


    def delete_category(self, pk: int | str, transfer: bool):
        """
        Deletes category entry with id=pk from repo
        if transfer is true transfers children to parent
        Also auto manages expenses with deleted category
        calls update_expenses and update_categories
        """
        deleting_obj = self.cat_repo.get(pk)
        new_parent_pk = int(deleting_obj.parent)

        def manage_expenses(deleting_pk: int | str):
            """
            Changes expenses, when their category is delted
            Changes its category to parent if exists
            """
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
            def delete_obj_in_tree(obj: Category):
                """
                Deletes category instance of obj
                and all its ancestors
                """
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


    def update_all(self):
        """
        Updates everything in view
        """
        self.update_budgets()
        self.update_expenses()


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    window = MyWindow()
    DIRECTORY = 'database.db'
    cat_repo = SQLiteRepository(DIRECTORY, Category)
    budget_repo = SQLiteRepository(DIRECTORY, Budget)
    expense_repo = SQLiteRepository(DIRECTORY, Expense)
    presenter = Presenter(cat_repo=cat_repo, bud_repo=budget_repo, exp_repo=expense_repo,
                          cat_class=Category, budget_class=Budget, exp_class=Expense, view=window)
    window.show()
    sys.exit(app.exec())
