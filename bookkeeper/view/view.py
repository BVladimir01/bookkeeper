import sys
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QEvent, QObject, Qt, QSize, Signal
from datetime import date

class ExpenseTable(QtWidgets.QTableWidget):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)

        self.setColumnCount(5)
        self.setRowCount(0)

        self.setHorizontalHeaderLabels("pk Дата Сумма Категория Комментарий".split())
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        self.hideColumn(0)

        self.verticalHeader().hide()
        self.itemChanged.connect(self.change_slot)
        # self.cols = ['pk', 'expense_date', 'amount', 'category', 'comment']

        # self.tranlator = {i:j for i, j in zip("pk Дата Сумма Категория Комментарий".split(), self.cols)}

        # self.itemChanged.connect(self.change_slot)
        # self.update_table()


    def update_expenses(self, expenses: list, categories: list, headers: list, translator):
        self.itemChanged.disconnect(self.change_slot)
        self.clearContents()
        for k, expense in enumerate(expenses):
            self.insertRow(0)
            cat = categories[k]
            for i, attr in enumerate(headers):
                text = str(getattr(expense, attr))
                if text != 'None':
                    if attr == 'category':
                        text = str(cat.name)
                    self.setItem(0, i, QtWidgets.QTableWidgetItem(text))
                else:
                    self.setItem(0, i, QtWidgets.QTableWidgetItem(''))

        self.sortByColumn(1, QtCore.Qt.SortOrder.DescendingOrder)
        self.itemChanged.connect(self.change_slot)


    def contextMenuEvent(self, arg__1: QtGui.QContextMenuEvent) -> None:
        print(type(self.itemAt(arg__1.pos())))
        self.last_active_item = self.itemAt(arg__1.pos())
        if type(self.itemAt(arg__1.pos())) == QtWidgets.QTableWidgetItem:
            self.menu = QtWidgets.QMenu(self)

            delete_action = self.menu.addAction('delete entry')
            delete_action.triggered.connect(self.delete_action_slot)

            # add other required actions
            self.menu.exec(arg__1.globalPos())
            return super().contextMenuEvent(arg__1)
        else:
            pass    


    def register_change(self, handler):
        self.change_func = handler


    def change_slot(self, item: QtWidgets.QTableWidgetItem):
        # pass
        # row = item.row()
        # pk = int(self.item(row, 0).text())
        # old_obj = self.presenter.exp_repo.get(pk)
        # attr_name = self.cols[item.column()]
        # attr_type = old_obj.__annotations__[attr_name]
        # if attr_name == 'expense_date':
        #     old_obj.expense_date = date.fromisoformat(item.text())
        # elif attr_name == 'amount':
        #     old_obj.amount = int(item.text())
        # elif attr_name == 'category':
        #     cat_obj = self.presenter.cat_repo.get_all({'name': item.text()})[0]
        #     old_obj.category = cat_obj.pk
        # elif attr_name == 'comment':
        #     old_obj.comment = item.text()

        # print('changing')
        # print(old_obj)
        # self.presenter.exp_repo.update(old_obj)
        # self.update_table()
        attr_val_dict = { header_name: self.item(item.row, i).text()
                         for (i, header_name) in enumerate(self.horizontalHeader)}
        self.change_func(attr_val_dict)
    

    def register_delete(self, handler):
        self.delete_func = handler


    def delete_action_slot(self, action):
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
            self.update_expenses()
        

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


class MyWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.expenses_table = ExpenseTable(self)
        self.init_ui()

        self.setWindowTitle('The Bookkeeper app')
        self.resize(600, 800)


    def init_ui(self):
        self.general_layout = QtWidgets.QVBoxLayout()

        self.general_layout.addWidget(QtWidgets.QLabel('Записи'))
        self.general_layout.addWidget(self.expenses_table)

        self.setLayout(self.general_layout)


    def register_exp_add(self, handler):
        pass


    def register_exp_delete(self, handler):
        self.expenses_table.register_delete(handler)

    
    def update_expenses(self, expenses, categories, headers, tranlator):
        self.expenses_table.update_expenses(expenses, categories, headers, tranlator)


if __name__ == '__main__':
    app = QtWidgets.QApplication()
    window = MyWindow()
    window.show()
    sys.exit(app.exec())