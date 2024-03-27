import sys
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QEvent, QObject, Qt, QSize, Signal
import random
from presenter import Bookkeeper
from models import budget, category, expense
from repository import sqlite_repository
from datetime import date

class CategoryItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setToolTip(0, 'right click for options')
    


#Хорошо бы здесь все сделать по ключу, а не по имени
class CategoryTree(QtWidgets.QTreeWidget):

    cat_signal = QtCore.Signal(CategoryItem)

    def __init__(self, main_window: 'MyWindow', presenter: Bookkeeper):
        super().__init__()

        self.main_window = main_window
        self.presenter = presenter
        self.setColumnCount(0)
        # self.setExpandsOnDoubleClick(False)
        self.setHeaderLabel('label 1')
        header = self.headerItem()
        header.setHidden(True)
        viewport = self.viewport()
        viewport.installEventFilter(self)
        signal = self.itemDoubleClicked
    

    # def eventFilter(self, obj, event):
    #     if event.type() == QEvent.MouseButtonPress:
    #         button = ""
    #         if event.button() == Qt.LeftButton:
    #             print("Left")
    #         elif event.button() == Qt.RightButton:
    #             print("Right")
    #         elif event.button() == Qt.MiddleButton:
    #             print("Middle")

    #     return super().eventFilter(obj, event)
    

    def contextMenuEvent(self, arg__1: QtGui.QContextMenuEvent) -> None:
        print(type(self.itemAt(arg__1.pos())))
        self.last_active_item = self.itemAt(arg__1.pos())
        if type(self.itemAt(arg__1.pos())) == CategoryItem:
            self.menu = QtWidgets.QMenu(self)

            add_action = self.menu.addAction('add')
            add_action.triggered.connect(self.add_action_slot)

            edit_action = self.menu.addAction('edit')
            edit_action.triggered.connect(self.edit_action_slot)

            delete_action = self.menu.addAction('delete')
            delete_action.triggered.connect(self.delete_action_slot)

            # add other required actions
            self.menu.exec(arg__1.globalPos())
            return super().contextMenuEvent(arg__1)
        else:
            self.menu = QtWidgets.QMenu(self)
            add_action = self.menu.addAction('add')
            add_action.triggered.connect(self.add_action_slot)
            # add other required actions
            self.menu.exec(arg__1.globalPos())
            return super().contextMenuEvent(arg__1)
    

    def edit_action_slot(self):
        old_cat_name = self.last_active_item.text(0)
        print('editing')
        dlg = QtWidgets.QInputDialog(self)
        dlg.resize(200, 50)
        new_name, ok = dlg.getText(self, 'Редактирование', 'Введите новое название категории')
        if ok:
            old_category = self.presenter.cat_repo.get_all({'name': old_cat_name})[0]
            new_category = self.presenter.cat_class.copy(old_category)
            new_category.name = new_name
            print(new_category)
            self.presenter.cat_repo.update(new_category)
            self.main_window.init_cats()
    

    def add_action_slot(self):
        print('adding')
        if self.last_active_item:
            where_name = self.last_active_item.text(0)
        else:
            where_name = None
        dlg = QtWidgets.QInputDialog(self)
        dlg.resize(200, 50)
        new_name, ok = dlg.getText(self, 'Добавление', 'Введите название новой категории')
        if ok:
            if where_name:
                parent_pk = self.presenter.cat_repo.get_all({'name': where_name})[0].pk
            else:
                parent_pk = None
            new_category = self.presenter.cat_class(name=new_name, parent=parent_pk)
            print(new_category)
            self.presenter.cat_repo.add(new_category)
            self.main_window.init_cats()


    def delete_action_slot(self):
        print('deleting')
        where_name = self.last_active_item.text(0)
        cat_obj = self.presenter.cat_repo.get_all({'name': where_name})[0]
        has_children = cat_obj.get_children(self.presenter.cat_repo)

        delete_button = QtWidgets.QMessageBox.StandardButton.Discard
        transfer_button = QtWidgets.QMessageBox.StandardButton.SaveAll
        cancel_button = QtWidgets.QMessageBox.StandardButton.Cancel

        if has_children:
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Удаление")
            dlg.setText("Что делать с подкатегорями?")
            dlg.addButton(delete_button)
            dlg.setButtonText(delete_button, 'Удалить')

            dlg.addButton(transfer_button)
            dlg.setButtonText(transfer_button, 'Наследовать')

            dlg.addButton(cancel_button)
            dlg.setButtonText(cancel_button, 'Отмена')
            dlg.setIcon(QtWidgets.QMessageBox.Question)
        else:
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
            def delete_obj_in_tree(obj, repo):
                children = obj.get_children(repo)
                if children:
                    for child in children:
                        delete_obj_in_tree(child, repo)
                repo.delete(obj.pk)
                
            
            cat_obj = self.presenter.cat_repo.get_all({'name': where_name})[0]
            delete_obj_in_tree(cat_obj, self.presenter.cat_repo)
            self.main_window.init_cats()

            
        if res == transfer_button:

            cat_obj = self.presenter.cat_repo.get_all({'name': where_name})[0]
            parent_pk = cat_obj.parent
            children_list = cat_obj.get_children(self.presenter.cat_repo)
            for child in children_list:
                child.parent = parent_pk
                self.presenter.cat_repo.update(child)
            self.presenter.cat_repo.delete(cat_obj.pk)
            self.main_window.init_cats()
        print(res)


    # def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
    #     if event.button() == Qt.RightButton:
    #         print('right')
    #     return super().mousePressEvent(event)

        
class BudgetTable(QtWidgets.QTableWidget):

    def __init__(self, parent: QtWidgets.QWidget, presenter: Bookkeeper):
        super().__init__(parent)
        self.presenter = presenter
        self.initiated = False

        self.setColumnCount(2)
        self.setRowCount(3)
        self.setHorizontalHeaderLabels(('Сумма', 'Бюджет'))
        self.setVerticalHeaderLabels(('День', 'Неделя', 'Месяц'))
        hor_header = self.horizontalHeader()
        hor_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        hor_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.setFixedHeight(116)

        self.setItem(0, 1, QtWidgets.QTableWidgetItem(str(self.presenter.bud_repo.get_all({'time_period': 'День'})[0].amount)))
        self.setItem(1, 1, QtWidgets.QTableWidgetItem(str(self.presenter.bud_repo.get_all({'time_period': 'Неделя'})[0].amount)))
        self.setItem(2, 1, QtWidgets.QTableWidgetItem(str(self.presenter.bud_repo.get_all({'time_period': 'Месяц'})[0].amount)))
        self.itemChanged.connect(self.edit_slot)
     

    def edit_slot(self, item: QtWidgets.QTableWidgetItem):
        if item.column() == 1:
            if self.initiated:
                try:
                    new_amount = item.text()
                    print('editing budget')
                    header = self.verticalHeaderItem(item.row()).text()
                    print(header)
                    old_obj = self.presenter.bud_repo.get_all({'time_period': header})[0]
                    old_obj.amount = int(new_amount)
                    self.presenter.bud_repo.update(old_obj)
                except ValueError:
                    print('enter correct budget')
                    input()
                    self.update_table()
        if item.column() == 0:
            pass


    def update_table(self):
        self.item(0, 1).setText(str(self.presenter.bud_repo.get_all({'time_period': 'День'})[0].amount))
        self.item(1, 1).setText(str(self.presenter.bud_repo.get_all({'time_period': 'Неделя'})[0].amount))
        self.item(2, 1).setText(str(self.presenter.bud_repo.get_all({'time_period': 'Месяц'})[0].amount))

    def count_expenses(self):
        pass


class ExpenseTable(QtWidgets.QTableWidget):
    def __init__(self, parent: QtWidgets.QWidget, presenter: Bookkeeper):
        super().__init__(parent)

        self.presenter = presenter

        self.setColumnCount(5)
        self.setRowCount(0)

        self.setHorizontalHeaderLabels("pk Дата Сумма Категория Комментарий".split())
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        # self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.hideColumn(0)

        self.verticalHeader().hide()
        self.cols = ['pk', 'expense_date', 'amount', 'category', 'comment']

        self.tranlator = {i:j for i, j in zip("pk Дата Сумма Категория Комментарий".split(), self.cols)}

        self.itemChanged.connect(self.change_slot)
        self.update_table()


    def update_table(self):
        self.itemChanged.disconnect(self.change_slot)
        self.clearContents()
        expenses = self.presenter.exp_repo.get_all()
        for expense in expenses:
            self.insertRow(0)
            for i, attr in enumerate(self.cols):
                text = str(getattr(expense, attr))
                if text != 'None':
                    if attr == 'category':
                        cat = self.presenter.cat_repo.get(int(text))
                        text = str(cat.name)
                    self.setItem(0, i, QtWidgets.QTableWidgetItem(text))
                else:
                    self.setItem(0, i, QtWidgets.QTableWidgetItem(''))

        self.sortByColumn(1, QtCore.Qt.SortOrder.DescendingOrder)
        print(self.parent())
        self.itemChanged.connect(self.change_slot)

    def change_slot(self, item: QtWidgets.QTableWidgetItem):
        row = item.row()
        pk = int(self.item(row, 0).text())
        old_obj = self.presenter.exp_repo.get(pk)
        attr_name = self.cols[item.column()]
        attr_type = old_obj.__annotations__[attr_name]

        if attr_name == 'expense_date':
            old_obj.expense_date = date.fromisoformat(item.text())
        elif attr_name == 'amount':
            old_obj.amount = int(item.text())
        elif attr_name == 'category':
            cat_obj = self.presenter.cat_repo.get_all({'name': item.text()})[0]
            old_obj.category = cat_obj.pk
        elif attr_name == 'comment':
            old_obj.comment = item.text()

        print('changing')
        print(old_obj)
        self.presenter.exp_repo.update(old_obj)
        self.update_table()


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
            self.itemChanged.disconnect(self.change_slot)
            self.delete_process = True
            row = self.last_active_item.row()
            pk = int(self.item(row, 0).text())
            print(pk)
            self.presenter.exp_repo.delete(pk)
            self.itemChanged.connect(self.change_slot)
            self.update_table()
        

    def add_entry(self, obj):
        print(obj)

def greeter(func):
    print('in decor')
    def new_func(*args, **keyargs):
        print('in event')
        return func(*args, **keyargs)
    return new_func


class MyWindow(QtWidgets.QWidget):

    cat_add_button_signal = Signal(int, str)

    def __init__(self, presenter: Bookkeeper = None):
        super().__init__()

        self.presenter = presenter
        self.treeWidget = CategoryTree(self, presenter)
        self.budget_table = BudgetTable(self, presenter)
        self.expenses_table = ExpenseTable(self, presenter)
        self.init_ui()
        self.init_cats()
        self.budget_table.initiated = True


    def init_cats(self):
        self.treeWidget.clear()
        cat_list = self.presenter.cat_repo.get_all()
        root_cats = [cat for cat in cat_list if cat.parent == 0]
        added = []
        translator = {}
        for cat in root_cats:
            item = CategoryItem(self.treeWidget)
            item.setText(0, cat.name)
            added.append(cat.pk)
            cat_list.remove(cat)
            translator[cat.pk] = item

        while True:
            for cat in cat_list:
                if cat.parent in added:
                    item = CategoryItem(translator[cat.parent])
                    item.setText(0, cat.name)
                    added.append(cat.pk)
                    cat_list.remove(cat)
                    translator[cat.pk] = item
            if cat_list == []:
                break
        self.presenter.cat_item_dic = translator

        
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

        self.general_layout.addWidget(QtWidgets.QLabel('Записи'))
        self.general_layout.addWidget(self.expenses_table)

        self.general_layout.addWidget(QtWidgets.QLabel('Бюджет'))
        self.general_layout.addWidget(self.budget_table)

        self.add_edit_layout()

        self.general_layout.addWidget(self.treeWidget)
        self.setLayout(self.general_layout)


    def add_edit_layout(self):
        edit_layout = QtWidgets.QGridLayout()

        edit_layout.addWidget(QtWidgets.QLabel('Дата расхода'), 0, 0)
        self.edit_date_line = QtWidgets.QLineEdit()
        edit_layout.addWidget(self.edit_date_line, 0, 1)

        edit_layout.addWidget(QtWidgets.QLabel('Сумма'), 1, 0)
        self.edit_sum_line = QtWidgets.QLineEdit()
        edit_layout.addWidget(self.edit_sum_line, 1, 1)

        edit_layout.addWidget(QtWidgets.QLabel('Категория'), 2, 0)
        self.choose_category_button = QtWidgets.QPushButton('Выбрать категорию')
        edit_layout.addWidget(self.choose_category_button, 2, 1)

        edit_layout.addWidget(QtWidgets.QLabel('Комментарий'), 3, 0)
        self.edit_comment_line = QtWidgets.QTextEdit()
        edit_layout.addWidget(self.edit_comment_line, 3, 1)

        self.add_entry_button = QtWidgets.QPushButton('Добавить')
        self.add_entry_button.clicked.connect(self.on_clicked)
        edit_layout.addWidget(self.add_entry_button, 4, 1)

        self.edit_layout = edit_layout
        self.general_layout.addLayout(edit_layout)

    
    def on_clicked(self):
        expense_date = self.presenter.exp_class.MyDate(self.edit_date_line.text())
        amount = int(self.edit_sum_line.text())
        comment = self.edit_comment_line.toPlainText()
        obj = self.presenter.exp_class(expense_date=expense_date,
                                       amount=amount,
                                       comment=comment)
        self.expenses_table.add_entry(obj)


cat_repo = sqlite_repository.SQLiteRepository('D:\\физтех\\proga\\bookkeeper_project\\tests\\test_db.db', category.Category)
budget_repo = sqlite_repository.SQLiteRepository('D:\\физтех\\proga\\bookkeeper_project\\tests\\test_db.db', budget.Budget)
expense_repo = sqlite_repository.SQLiteRepository('D:\\физтех\\proga\\bookkeeper_project\\tests\\test_db.db', expense.Expense)
app = QtWidgets.QApplication()
window = MyWindow(Bookkeeper(cat_repo, budget_repo, expense_repo, category.Category, budget.Budget, expense.Expense))
window.setWindowTitle('The Bookkeeper app')
window.resize(600, 800)


if __name__ == '__main__':
    window.show()
    sys.exit(app.exec())