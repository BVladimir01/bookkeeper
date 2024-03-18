import sys
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import random

class MyWindow(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.label = QtWidgets.QLabel('label')
        self.general_layout = QtWidgets.QVBoxLayout()
        self.add_expenses_table()
        self.add_budget_table()
        self.add_edit_layout()
    #     self.general_layout.addWidget(QtWidgets.QCheckBox())
    #     self.general_layout.addWidget(QtWidgets.QCheckBox())
    #     self.general_layout.addWidget(QtWidgets.QScrollBar())

    #     self.button = QtWidgets.QPushButton('Нажми меня!')
    #     self.button.setToolTip('Не жми')
    #     self.button.clicked.connect(self.on_click)
    #     self.general_layout.addWidget(self.button)

        self.setLayout(self.general_layout)

    # def on_click(self):   
    #     self.stacked.setCurrentIndex(random.randint(0, 2))

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
        header = budget_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        # budget_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
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
        edit_layout.addWidget(self.add_entry_button, 2, 1)

        self.edit_layout = edit_layout
        self.general_layout.addLayout(edit_layout)



app = QtWidgets.QApplication(sys.argv)
window = MyWindow()
window.setWindowTitle('The Bookkeeper app')
window.resize(500, 500)
window.show()
sys.exit(app.exec())