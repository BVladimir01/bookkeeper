import sys
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QEvent, QObject, Qt, QSize, Signal
from datetime import date
from view.budget_table import *
from view.category_view import *
from view.expense_table import *


class MyWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.expenses_table = ExpenseTable(self)
        self.budget_table = BudgetTable(self)
        self.init_ui()

        self.setWindowTitle('The Bookkeeper app')
        self.resize(600, 800)


    def init_ui(self):
        self.general_layout = QtWidgets.QVBoxLayout()

        self.general_layout.addWidget(QtWidgets.QLabel('Записи'))
        self.general_layout.addWidget(self.expenses_table)

        self.general_layout.addWidget(QtWidgets.QLabel('Бюджет'))
        self.general_layout.addWidget(self.budget_table)

        self.add_edit_layout()

        self.setLayout(self.general_layout)


    def add_edit_layout(self):
        edit_layout = QtWidgets.QGridLayout()

        edit_layout.addWidget(QtWidgets.QLabel('Дата расхода'), 0, 0)
        self.edit_date_line = QtWidgets.QLineEdit(str(date.today()))
        edit_layout.addWidget(self.edit_date_line, 0, 1)

        edit_layout.addWidget(QtWidgets.QLabel('Сумма'), 1, 0)
        self.edit_amount_line = QtWidgets.QLineEdit()
        edit_layout.addWidget(self.edit_amount_line, 1, 1)

        category_labels_layout = QtWidgets.QVBoxLayout()
        category_labels_layout.addWidget(QtWidgets.QLabel('Категория'))
        self.chosen_category_label = QtWidgets.QLabel('')
        category_labels_layout.addWidget(self.chosen_category_label)
        edit_layout.addLayout(category_labels_layout, 2, 0)

        category_buttons_layout = QtWidgets.QHBoxLayout()
        self.choose_category_button = QtWidgets.QPushButton('Выбрать категорию')
        category_buttons_layout.addWidget(self.choose_category_button)
        self.choose_category_button.clicked.connect(self.choose_category_slot)

        self.edit_category_button = QtWidgets.QPushButton('Редактировать категории')
        category_buttons_layout.addWidget(self.edit_category_button)
        edit_layout.addLayout(category_buttons_layout, 2, 1)
        self.edit_category_button.clicked.connect(self.edit_category_slot)

        edit_layout.addWidget(QtWidgets.QLabel('Комментарий'), 3, 0)
        self.edit_comment_line = QtWidgets.QTextEdit()
        edit_layout.addWidget(self.edit_comment_line, 3, 1)

        self.add_entry_button = QtWidgets.QPushButton('Добавить')
        edit_layout.addWidget(self.add_entry_button, 4, 1)
        self.add_entry_button.clicked.connect(self.add_exp_enrty_slot)

        self.edit_layout = edit_layout
        self.general_layout.addLayout(edit_layout)


    def add_exp_enrty_slot(self):
        if not hasattr(self, 'chosen_category_pk'):
            self.chosen_category_pk = 0
        amount = self.edit_amount_line.text()
        expense_date = self.edit_date_line.text()
        category_pk = self.chosen_category_pk
        comment = self.edit_comment_line.toPlainText()
        attr_val_dict = {}
        attr_val_dict['amount'] = amount
        attr_val_dict['expense_date'] = expense_date
        attr_val_dict['comment'] = comment
        attr_val_dict['category'] = category_pk
        self.add_exp_func(attr_val_dict)

        delattr(self, 'chosen_category_pk')
        self.chosen_category_label.setText('')

    def choose_category_slot(self):
        self.dlg = CategoryDialog(self, self.update_categories_func)
        self.update_categories_func()
        res = self.dlg.exec()


    def edit_category_slot(self):
        self.dlg = CategoryDialogEdit(self, self.update_categories_func, self.change_category_func,
                                      self.add_category_func, self.delete_category_func)
        self.update_categories_func()
        res = self.dlg.exec()


    def register_exp_add(self, handler):
        self.add_exp_func = handler

    def register_exp_delete(self, handler):
        self.expenses_table.register_delete(handler)

    def update_expenses(self, expenses, categories):
        self.expenses_table.update_expenses(expenses, categories)

    def register_exp_change(self, handler):
        self.expenses_table.register_change(handler)

    def register_exp_category_change(self, handler):
        self.expenses_table.register_exp_category_change(handler)

    def display_expenses(self, expenses):
        self.budget_table.display_expenses(expenses)

    def update_budgets(self, budgets):
        self.budget_table.update_budgets(budgets)

    def register_budget_change(self, handler):
        self.budget_table.register_budget_change(handler)

    def register_update_categories(self, handler):
        self.update_categories_func = handler

    def update_categories(self, categories):
        self.dlg.update_categories(categories)

    def register_category_change(self, handler):
        self.change_category_func = handler

    def register_category_add(self, handler):
        self.add_category_func = handler
    
    def register_category_delete(self, handler):
        self.delete_category_func = handler

    # def register_children_getter(self, handler):
    #     self.children_getter = handler

    # def register_parent_getter(self, handler):
    #     self.parent_getter = handler

if __name__ == '__main__':
    app = QtWidgets.QApplication()
    window = MyWindow()
    window.show()
    sys.exit(app.exec())