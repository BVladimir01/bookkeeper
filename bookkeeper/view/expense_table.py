from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QEvent, QObject, Qt, QSize, Signal
from view.category_view import CategoryDialog


class ExpenseTable(QtWidgets.QTableWidget):

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
        self.tranlator = {i:j for i, j in
                          zip("pk Дата Сумма category Комментарий".split(), self.attr_headers)}


    def update_expenses(self, expenses: list, categories: list):
        headers = self.headers
        translator = self.tranlator
        self.itemChanged.disconnect(self.change_slot)
        for j in range(self.rowCount()):
            self.removeRow(0)
    
        for k in range(len(expenses)):
            self.insertRow(0)
            expense = expenses[k]
            category = categories[k]
            for i, header in enumerate(headers):
                if header == 'Категория':
                    if category: text = str(category.name)
                    else: text = ''
                elif header == 'category':
                    if category: text = str(category.pk)
                    else: text = ''                    
                else:
                    attr_name = translator[header]
                    text = str(getattr(expense, attr_name))
                self.setItem(0, i, QtWidgets.QTableWidgetItem(text))
                pass

        self.sortByColumn(1, QtCore.Qt.SortOrder.DescendingOrder)
        self.itemChanged.connect(self.change_slot)


    def contextMenuEvent(self, arg__1: QtGui.QContextMenuEvent) -> None:
        print(type(self.itemAt(arg__1.pos())))
        self.last_active_item = self.itemAt(arg__1.pos())
        active_item = self.last_active_item
        if type(active_item) == QtWidgets.QTableWidgetItem:
            self.menu = QtWidgets.QMenu(self)

            delete_action = self.menu.addAction('delete entry')
            delete_action.triggered.connect(self.delete_slot)

            if active_item.column() == 4:
                change_category = self.menu.addAction('Change_category')
                change_category.triggered.connect(self.change_category_slot)
            
            self.menu.exec(arg__1.globalPos())
            return super().contextMenuEvent(arg__1)
        else:
            pass    


    def register_change(self, handler):
        self.change_func = handler


    def change_slot(self, item: QtWidgets.QTableWidgetItem):
        attr_val_dict = {}
        for i in range(len(self.headers)):
            header = self.headers[i]
            attr_name = self.tranlator.get(header)
            if attr_name: attr_val_dict[attr_name] = self.item(item.row(), i).text()
        self.change_func(attr_val_dict)
    

    def register_delete(self, handler):
        self.delete_func = handler


    def delete_slot(self, action):
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
            self.delete_process = True
            row = self.last_active_item.row()
            pk = int(self.item(row, 0).text())
            print(pk)
            self.delete_func(pk)
        

    def register_exp_category_change(self, handler):
        self.exp_category_change_func = handler


    def change_category_slot(self, action):
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


    def add_entry(self, obj):
        print(obj)
        self.itemChanged.disconnect(self.change_slot)
        self.insertRow(0)
        self.setItem(0, 0, QtWidgets.QTableWidgetItem(str(obj.pk)))
        self.setItem(0, 1, QtWidgets.QTableWidgetItem(str(obj.expense_date)))
        self.setItem(0, 2, QtWidgets.QTableWidgetItem(str(obj.amount)))
        if obj.category != None:
            self.setItem(0, 3, QtWidgets.QTableWidgetItem(str(obj.category)))
        else:
            self.setItem(0, 3, QtWidgets.QTableWidgetItem(''))
        self.setItem(0, 4, QtWidgets.QTableWidgetItem(str(obj.comment)))
        self.presenter.exp_repo.add(obj)
        self.itemChanged.connect(self.change_slot)
        self.update_table()