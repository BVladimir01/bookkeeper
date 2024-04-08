"""
Describes ExpenseTable class
"""


from PySide6 import QtWidgets, QtGui, QtCore
from view.category_view import CategoryDialog
from models.category import Category
from models.expense import Expense


class ExpenseTable(QtWidgets.QTableWidget):
    """
    Widget
    Displays table with info about entries of Expense model
    Allows user to add and edit entries
    """

    expense_table = True

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self.my_parent = parent
        self.setColumnCount(6)
        self.setRowCount(0)

        self.setHorizontalHeaderLabels("pk Дата Сумма category Категория Комментарий".split())
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)
        # self.hideColumn(0)
        # self.hideColumn(3)

        self.verticalHeader().hide()
        self.itemChanged.connect(self.change_slot)

        self.headers = "pk Дата Сумма category Категория Комментарий".split()
        self.attr_headers = ['pk', 'expense_date', 'amount', 'category', 'comment']
        self.tranlator = dict(zip("pk Дата Сумма category Комментарий".split(), self.attr_headers))


    def update_expenses(self, expenses: list[Expense], categories: list[Category]) -> None:
        """
        Renews expenses entries in user interface
        Gets information from expenses and categores arguments
        """
        headers = self.headers
        translator = self.tranlator
        self.itemChanged.disconnect(self.change_slot)
        for j in range(self.rowCount()):
            self.removeRow(0)

        for expense, category in zip(expenses, categories):
            self.insertRow(0)
            for i, header in enumerate(headers):
                if header == 'Категория':
                    if category:
                        text = str(category.name)
                    else: text = ''
                elif header == 'category':
                    if category:
                        text = str(category.pk)
                    else: text = ''
                else:
                    attr_name = translator[header]
                    text = str(getattr(expense, attr_name))
                self.setItem(0, i, QtWidgets.QTableWidgetItem(text))

        self.sortByColumn(1, QtCore.Qt.SortOrder.DescendingOrder)
        self.itemChanged.connect(self.change_slot)


    def contextMenuEvent(self, arg__1: QtGui.QContextMenuEvent) -> None:
        """
        Displays options to manage expenses
        Connects options with functions
        User can delete entry or change category of entry
        """
        print(type(self.itemAt(arg__1.pos())))
        self.last_active_item = self.itemAt(arg__1.pos())
        active_item = self.last_active_item
        if isinstance(active_item, QtWidgets.QTableWidgetItem):
            menu = QtWidgets.QMenu(self)

            delete_action = menu.addAction('delete entry')
            delete_action.triggered.connect(self.delete_slot)

            change_category = menu.addAction('Change_category')
            change_category.triggered.connect(self.change_category_slot)

            menu.exec(arg__1.globalPos())


    def register_change(self, handler) -> None:
        """
        Registers handler as function to handle change of expense entry
        Handler function manages back end
        """
        self.change_func = handler


    def change_slot(self, item: QtWidgets.QTableWidgetItem) -> None:
        """
        Called when field of expense entry
        are changed by user via user interface
        Collects data and delegates to handler
        """
        attr_val_dict = {}
        for i, header in enumerate(self.headers):
            attr_name = self.tranlator.get(header)
            if attr_name:
                attr_val_dict[attr_name] = self.item(item.row(), i).text()
        self.change_func(attr_val_dict)


    def register_delete(self, handler) -> None:
        """
        Registers handler as function to handle deletions of expense enrty
        Handler function manages back end
        """
        self.delete_func = handler


    def delete_slot(self) -> None:
        """
        Called when delete option is chosen by user
        Opens dialog window to confirm deletion
        Collects data and delegates to handler
        """
        delete_button = QtWidgets.QMessageBox.StandardButton.Discard
        cancel_button = QtWidgets.QMessageBox.StandardButton.Cancel

        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Удаление")
        dlg.setText("Вы уверены, что хотите удалить?")
        dlg.addButton(delete_button)
        dlg.setButtonText(delete_button, 'Удалить')

        dlg.addButton(cancel_button)
        dlg.setButtonText(cancel_button, 'Отмена')
        dlg.setIcon(QtWidgets.QMessageBox.Question)

        res = dlg.exec()
        if res == delete_button:
            row = self.last_active_item.row()
            pk = int(self.item(row, 0).text())
            print(pk)
            self.delete_func(pk)


    def register_exp_category_change(self, handler) -> None:
        """
        Registers handler as function to handle change of category
        Handler function manages back end
        """
        self.exp_category_change_func = handler


    def change_category_slot(self) -> None:
        """
        Called when change category option is chosen by user
        Opens dialog window to choose new category
        Collects data and delegates to handler
        """
        parent = self.my_parent
        parent = self.parent()
        parent.dlg = CategoryDialog(self, parent.update_categories_func)
        parent.update_categories_func()
        res = parent.dlg.exec()
        if res:
            category_pk = self.chosen_exp_category_pk
            row = self.last_active_item.row()
            item = self.item(row, 3)
            item.setText(category_pk)
            delattr(self, 'chosen_exp_category_pk')


    def add_entry(self, obj) -> None:
        """
        Called when user adds new category from main windowe
        Collects data and delegates to handler
        """
        print(obj)
        self.itemChanged.disconnect(self.change_slot)
        self.insertRow(0)
        self.setItem(0, 0, QtWidgets.QTableWidgetItem(str(obj.pk)))
        self.setItem(0, 1, QtWidgets.QTableWidgetItem(str(obj.expense_date)))
        self.setItem(0, 2, QtWidgets.QTableWidgetItem(str(obj.amount)))
        if obj.category is not None:
            self.setItem(0, 3, QtWidgets.QTableWidgetItem(str(obj.category)))
        else:
            self.setItem(0, 3, QtWidgets.QTableWidgetItem(''))
        self.setItem(0, 4, QtWidgets.QTableWidgetItem(str(obj.comment)))
        self.presenter.exp_repo.add(obj)
        self.itemChanged.connect(self.change_slot)
        self.update_table()
