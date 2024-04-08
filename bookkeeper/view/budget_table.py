from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QEvent, QObject, Qt, QSize, Signal


class BudgetTable(QtWidgets.QTableWidget):

    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)

        self.initiated = False

        self.setColumnCount(3)
        self.setRowCount(3)
        self.setHorizontalHeaderLabels(('Сумма', 'pk', 'Бюджет'))
        self.setVerticalHeaderLabels(('День', 'Неделя', 'Месяц'))
        hor_header = self.horizontalHeader()
        hor_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        hor_header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.setFixedHeight(116)
        
        # self.hideColumn(1)

        self.itemChanged.connect(self.change_slot)


    def register_budget_change(self, handler):
        self.change_budget = handler


    def change_slot(self, item: QtWidgets.QTableWidgetItem):
        if self.initiated:
            if item.column() == 2:
                attr_val_dict = {}
                try:
                    new_amount = item.text()
                    attr_val_dict['amount'] = new_amount
                    header = self.verticalHeaderItem(item.row()).text()
                    attr_val_dict['time_period'] = header
                    pk = self.item(item.row(), 1).text()
                    attr_val_dict['pk'] = pk
                    self.change_budget(attr_val_dict)
                except ValueError:
                    print('enter correct budget')
                    input()


    def update_budgets(self, budgets):
        self.itemChanged.disconnect(self.change_slot)
        for i in range(3):
            self.setItem(i, 1, QtWidgets.QTableWidgetItem(str(budgets[i].pk)))
            self.setItem(i, 2, QtWidgets.QTableWidgetItem(str(budgets[i].amount)))
        
        self.initiated = True
        self.itemChanged.connect(self.change_slot)


    def display_expenses(self, expenses):
        self.itemChanged.disconnect(self.change_slot)
        for i, expense in enumerate(expenses):
            self.setItem(i, 0, QtWidgets.QTableWidgetItem(str(expense)))
            flags = self.item(i, 0).flags()
            self.item(i, 0).setFlags(flags & ~Qt.ItemFlag.ItemIsEditable)
        self.itemChanged.connect(self.change_slot)
