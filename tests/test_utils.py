import sys
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import random

class MyWindow(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.label = QtWidgets.QLabel('label')
        self.general_layout = QtWidgets.QVBoxLayout()
        self.add_edit_layout()
        self.add_radio_layout()
        self.add_stacked_layout()
        self.general_layout.addLayout(self.edit_layout)
        self.general_layout.addLayout(self.radio_layout)
        self.general_layout.addWidget(QtWidgets.QCheckBox())
        self.general_layout.addWidget(QtWidgets.QCheckBox())
        self.general_layout.addWidget(QtWidgets.QScrollBar())

        self.button = QtWidgets.QPushButton('Нажми меня!')
        self.button.setToolTip('Не жми')
        self.button.clicked.connect(self.on_click)
        self.general_layout.addLayout(self.stacked)
        self.general_layout.addWidget(self.button)

        self.setLayout(self.general_layout)

    def on_click(self):   
        self.stacked.setCurrentIndex(random.randint(0, 2))

    def add_edit_layout(self):
        self.edit_layout = QtWidgets.QGridLayout()
        self.edit_layout.addWidget(QtWidgets.QLabel('qline edit'), 1, 1)
        self.edit_layout.addWidget(QtWidgets.QLabel('qtext edit'), 2, 1)
        self.lineedit = QtWidgets.QLineEdit('initial text, i guess')
        self.textedit = QtWidgets.QTextEdit()
        self.edit_layout.addWidget(self.lineedit, 1, 2)
        self.edit_layout.addWidget(self.textedit, 2, 2)

    def add_radio_layout(self):
        self.radio_layout = QtWidgets.QGridLayout()
        self.radio_layout.addWidget(QtWidgets.QRadioButton(), 1, 1)
        self.radio_layout.addWidget(QtWidgets.QRadioButton(), 2, 1)
        self.radio_layout.addWidget(QtWidgets.QLabel('radio 1'), 1, 2)
        self.radio_layout.addWidget(QtWidgets.QLabel('radio 2'), 2, 2)

    def add_stacked_layout(self):
        self.stacked = QtWidgets.QStackedLayout()
        self.widget_list = []
        for i in range(3):
            self.widget_list.append(QtWidgets.QLabel(f'widget no {i}'))
            self.stacked.addWidget(self.widget_list[i])
            self.widget_list[i].setAlignment(Qt.AlignmentFlag.AlignCenter)


app = QtWidgets.QApplication(sys.argv)
window = MyWindow()
window.setWindowTitle('random')
window.resize(300, 100)
window.show()
sys.exit(app.exec())