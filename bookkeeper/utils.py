import sys
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QEvent, QObject, Qt, QSize
import random
from presenter import Bookkeeper
from models import budget, category, expense
from repository import sqlite_repository


def greeter(func):
    print('in decor')
    def new_func(*args, **keyargs):
        print('in event')
        return func(*args, **keyargs)
    return new_func


class MyWindow(QtWidgets.QWidget):

    def __init__(self, presenter=None):
        super().__init__()


        treeWidget = QtWidgets.QTreeWidget()
        treeWidget.setColumnCount(0)
        treeWidget.setExpandsOnDoubleClick(False)
        item = QtWidgets.QTreeWidgetItem(treeWidget)
        item.setText(0, 'oslo')
        item2 = QtWidgets.QTreeWidgetItem(item)
        item2.setText(0, 'osaka')
        item2.setFlags(item2.flags() | Qt.ItemIsEditable)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setToolTip(0, 'f2 to edit')
        treeWidget.setHeaderLabel('label 1')
        header = treeWidget.headerItem()
        header.setHidden(True)
        # treeWidget.addTopLevelItem(item)
        self.treeWidget = treeWidget
        treeWidget.mousePressEvent = greeter(treeWidget.mousePressEvent)
        
        signal = treeWidget.itemDoubleClicked
        # signal.connect(self.decorated_expand)
        self.init_ui()



    # def eventFilter(self, watched: QObject, event: QEvent) -> bool:
    #     print(event)
    #     return super().eventFilter(watched, event)
    
    # def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
    #     print('presseed')
    #     return super().mousePressEvent(event)
    
    # def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
    #     print('doubleckick')
    #     return super().mouseDoubleClickEvent(event)
    # def decorated_expand(self, item:QtWidgets.QTreeWidgetItem, column):
    #     if item.isExpanded():
    #          self.treeWidget.collapseItem(item)
    #     else:
    #         self.treeWidget.expandItem(item)



    def init_ui(self):
        self.general_layout = QtWidgets.QVBoxLayout()
        self.add_expenses_table()
        self.add_budget_table()
        self.add_edit_layout()
        self.general_layout.addWidget(self.treeWidget)

        self.setLayout(self.general_layout)


    def add_expenses_table(self):
        self.general_layout.addWidget(QtWidgets.QLabel('Последние расходы'))

        expenses_table = QtWidgets.QTableWidget(4, 20)
        expenses_table.setColumnCount(4)
        expenses_table.setRowCount(20)

        expenses_table.setHorizontalHeaderLabels("Дата Сумма Категория Комментарий".split())
        header = expenses_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)

        expenses_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        expenses_table.verticalHeader().hide()

        self.expenses_table = expenses_table
        self.general_layout.addWidget(expenses_table)


    def add_budget_table(self):
        self.general_layout.addWidget(QtWidgets.QLabel('Бюджет'))

        budget_table = QtWidgets.QTableWidget(4, 20)
        budget_table.setColumnCount(2)
        budget_table.setRowCount(3)

        budget_table.setHorizontalHeaderLabels(('Сумма', 'Бюджет'))
        budget_table.setVerticalHeaderLabels(('День', 'Неделя', 'Месяц'))
        hor_header = budget_table.horizontalHeader()
        hor_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        hor_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        # hor_header.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)
        # hor_header.setLineWidth(1)
        # ver_header = budget_table.verticalHeader()
        # ver_header.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Plain)
        # ver_header.setLineWidth(1)
        # budget_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        budget_table.setFixedHeight(116)

        self.budget_table = budget_table
        self.general_layout.addWidget(budget_table)


    def add_edit_layout(self):
        edit_layout = QtWidgets.QGridLayout()

        edit_layout.addWidget(QtWidgets.QLabel('Сумма'), 0, 0)
        self.sum_line = QtWidgets.QLineEdit()
        edit_layout.addWidget(self.sum_line, 0, 1)

        edit_layout.addWidget(QtWidgets.QLabel('Категория'), 1, 0)
        self.category_box = QtWidgets.QComboBox()
        self.category_box.addItem('Категория')
        edit_layout.addWidget(self.category_box, 1, 1)
        self.edit_category_button = QtWidgets.QPushButton('Редактировать')
        edit_layout.addWidget(self.edit_category_button, 1, 2)

        self.add_entry_button = QtWidgets.QPushButton('Добавить')
        self.add_entry_button.clicked.connect(self.on_clicked)
        edit_layout.addWidget(self.add_entry_button, 2, 1)

        self.edit_layout = edit_layout
        self.general_layout.addLayout(edit_layout)

    
    def on_clicked(self):
        dlg = QtWidgets.QMessageBox()
        dlg.setWindowTitle('modal window')
        dlg.setText("Здесь будет подробный текст вопроса")
        dlg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        dlg.setIcon(QtWidgets.QMessageBox.Question)
        answer = dlg.exec()
        if answer:
            print('yes')
            print(type(answer))
        else:
            print('no')


cat_repo = sqlite_repository.SQLiteRepository('D:\\физтех\\proga\\bookkeeper_project\\tests\\test_db.db', category.Category)
budget_repo = sqlite_repository.SQLiteRepository('D:\\физтех\\proga\\bookkeeper_project\\tests\\test_db.db', budget.Budget)
expense_repo = sqlite_repository.SQLiteRepository('D:\\физтех\\proga\\bookkeeper_project\\tests\\test_db.db', expense.Expense)
app = QtWidgets.QApplication()
window = MyWindow(Bookkeeper(cat_repo, budget_repo, expense_repo))
window.setWindowTitle('The Bookkeeper app')
window.resize(500, 500)


if __name__ == '__main__':
    window.show()
    sys.exit(app.exec())