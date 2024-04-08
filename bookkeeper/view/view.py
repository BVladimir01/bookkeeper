import sys
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QEvent, QObject, Qt, QSize, Signal
from datetime import date

class ExpenseTable(QtWidgets.QTableWidget):
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
        self.tranlator = {i:j for i, j in zip("pk Дата Сумма category Комментарий".split(), self.attr_headers)}


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


class CategoryItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setToolTip(0, 'right click for options')


class CategoryTree(QtWidgets.QTreeWidget):

    cat_signal = QtCore.Signal(CategoryItem)

    def __init__(self, main_window: 'MyWindow' | QtWidgets.QWidget, editable: bool, update_func, change_func, add_func, delete_func):
        super().__init__()

        self.editable = editable
        self.main_window = main_window
        self.setColumnCount(2)
        # self.setExpandsOnDoubleClick(False)
        self.setHeaderLabel('label 1')
        header = self.headerItem()
        header.setHidden(True)
        viewport = self.viewport()
        viewport.installEventFilter(self)
        self.update_func = update_func
        self.change_category_func = change_func
        self.add_category_func = add_func
        self.delete_category_func = delete_func

    def update_categories(self, categories):
        self.clear()
        cat_list = categories
        root_cats = [cat for cat in cat_list if cat.parent == 0]
        added = []
        translator = {}
        for cat in root_cats:
            item = CategoryItem(self)
            item.setText(0, cat.name)
            item.setText(1, str(cat.pk))
            added.append(cat.pk)
            cat_list.remove(cat)
            translator[cat.pk] = item

        while True:
            for cat in cat_list:
                if cat.parent in added:
                    item = CategoryItem(translator[cat.parent])
                    item.setText(0, cat.name)
                    item.setText(1, str(cat.pk))
                    added.append(cat.pk)
                    cat_list.remove(cat)
                    translator[cat.pk] = item
            if cat_list == []:
                break

        self.cat_item_dic = translator


    def contextMenuEvent(self, arg__1: QtGui.QContextMenuEvent) -> None:
        print(type(self.itemAt(arg__1.pos())))
        if self.editable:
            self.last_active_item = self.itemAt(arg__1.pos())
            if type(self.itemAt(arg__1.pos())) == CategoryItem:
                self.menu = QtWidgets.QMenu(self)

                add_action = self.menu.addAction('add')
                add_action.triggered.connect(self.add_category_slot)

                edit_action = self.menu.addAction('edit')
                edit_action.triggered.connect(self.change_category_slot)

                delete_action = self.menu.addAction('delete')
                delete_action.triggered.connect(self.delete_category_slot)

                # add other required actions
                self.menu.exec(arg__1.globalPos())
                return super().contextMenuEvent(arg__1)
            else:
                self.menu = QtWidgets.QMenu(self)
                add_action = self.menu.addAction('add')
                add_action.triggered.connect(self.add_category_slot)
                # add other required actions
                self.menu.exec(arg__1.globalPos())
                return super().contextMenuEvent(arg__1)
    

    def change_category_slot(self):
        pk = self.last_active_item.text(1)
        print('editing')
        dlg = QtWidgets.QInputDialog(self)
        dlg.resize(200, 50)
        new_name, ok = dlg.getText(self, 'Редактирование', 'Введите новое название категории')
        attr_val_dict = {'pk': pk, 'name': new_name}
        if ok: self.change_category_func(attr_val_dict)
    

    def add_category_slot(self):
        print('adding')
        if self.last_active_item:
            parent_pk = self.last_active_item.text(1)
        else:
            parent_pk = 0
        dlg = QtWidgets.QInputDialog(self)
        dlg.resize(200, 50)
        new_name, ok = dlg.getText(self, 'Добавление', 'Введите название новой категории')
        attr_val_dict = {'parent': parent_pk, 'name': new_name}
        self.add_category_func(attr_val_dict)


    def delete_category_slot(self):
        print('deleting')
        deleting_pk = int(self.last_active_item.text(1))
        children_count = self.last_active_item.childCount()

        delete_button = QtWidgets.QMessageBox.StandardButton.Discard
        transfer_button = QtWidgets.QMessageBox.StandardButton.SaveAll
        cancel_button = QtWidgets.QMessageBox.StandardButton.Cancel

        if children_count:
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
            self.delete_category_func(deleting_pk, False)
        elif res == transfer_button:
            self.delete_category_func(deleting_pk, True)
        


        # if res == delete_button:
        #     def delete_obj_in_tree(pk):
        #         children = self.get_children(pk)
        #         if children:
        #             for child in children:
        #                 delete_obj_in_tree(child.pk)
        #         self.delete_category_func(pk)
                
            
        #     delete_obj_in_tree(deleting_pk)
            
        # if res == transfer_button:
        #     children = self.get_children(deleting_pk)
        #     parent_pk = self.get_parent(deleting_pk)
        #     for child in children:
        #         new_name = child.name
        #         new_pk = child.pk
        #         attr_val_dict = {'pk' : new_pk, 'name' : new_name, 'parent' : parent_pk }
        #         self.change_category_func(attr_val_dict)
        #     self.delete_category_func(deleting_pk)


class CategoryDialog(QtWidgets.QDialog):

            
    def __init__(self, parent: QtWidgets.QWidget | None, update_func) -> None:
        super().__init__(parent)
        self.my_parent = parent

        self.resize(400, 500)
        self.setWindowTitle('Выбор категории')
        layout = QtWidgets.QVBoxLayout()

        self.category_tree = CategoryTree(self, False, update_func, None, None, None)
        layout.addWidget(self.category_tree)

        button_layout = QtWidgets.QHBoxLayout()
        accept_button = QtWidgets.QPushButton('Выбрать')
        accept_button.clicked.connect(self.accept_slot)
        reject_button = QtWidgets.QPushButton('Отмена')
        reject_button.clicked.connect(self.reject)
        button_layout.addWidget(accept_button)
        button_layout.addWidget(reject_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)


    def accept_slot(self):
        if type(self.my_parent) == ExpenseTable:
            selected_exp_category_pk = self.category_tree.currentItem().text(1)
            self.my_parent.chosen_exp_category_pk = selected_exp_category_pk
        else:
            selected_category_pk = self.category_tree.currentItem().text(1)
            selected_category_name = self.category_tree.currentItem().text(0)
            self.my_parent.chosen_category_pk = selected_category_pk
            self.my_parent.chosen_category_label.setText(selected_category_name)
        self.accept()


    def update_categories(self, categories):
        self.category_tree.update_categories(categories)


class CategoryDialogEdit(QtWidgets.QDialog):
            
    def __init__(self, parent: QtWidgets.QWidget, update_func, change_func, add_func, delete_func) -> None:
        super().__init__(parent)
        self.my_parent = parent

        self.resize(400, 500)
        self.setWindowTitle('Редактирование категорий')
        layout = QtWidgets.QVBoxLayout()

        self.category_tree = CategoryTree(parent, True, update_func, change_func, add_func, delete_func)
        layout.addWidget(self.category_tree)

        button_layout = QtWidgets.QHBoxLayout()
        end_button = QtWidgets.QPushButton('Закрыть')
        
        end_button.clicked.connect(self.accept)
        button_layout.addWidget(end_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    
    def update_categories(self, categories):
        self.category_tree.update_categories(categories)


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