"""
Describes classes for category view and managment
CategoryDialog
CategoryDialogEdit
CategoryTree
"""


from typing import List
from PySide6 import QtWidgets, QtGui
from models.category import Category


class CategoryItem(QtWidgets.QTreeWidgetItem):
    """Class of items displayed in CategoryTree"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setToolTip(0, 'Нажмите ПКМ для выбора действий')


class CategoryTree(QtWidgets.QTreeWidget):
    """
    Widget that displays categories as tree structure
    Allows to edit and choose category
    """

    def __init__(self, main_window: QtWidgets.QWidget, editable: bool,
                 update_func, change_func, add_func, delete_func) -> None:
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


    def update_categories(self, categories: List[Category]) -> None:
        """
        Renews categories in user interface
        Gets info from categories argument
        """
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


    def contextMenuEvent(self, arg__1: QtGui.QContextMenuEvent) -> None:
        """
        Displays options, availbale to user, when category item is clicked
        Connects options to functions
        """
        print(type(self.itemAt(arg__1.pos())))
        if self.editable:
            self.last_active_item = self.itemAt(arg__1.pos())
            if isinstance(self.itemAt(arg__1.pos()), CategoryItem):
                menu = QtWidgets.QMenu(self)

                add_action = menu.addAction('Добавить подкатегорию')
                add_action.triggered.connect(self.add_category_slot)

                edit_action = menu.addAction('Редактировать название')
                edit_action.triggered.connect(self.change_category_slot)

                delete_action = menu.addAction('Удалить категорию')
                delete_action.triggered.connect(self.delete_category_slot)

                # add other required actions
                menu.exec(arg__1.globalPos())
                # return super().contextMenuEvent(arg__1)
            else:
                menu = QtWidgets.QMenu(self)
                add_action = menu.addAction('Добавить новую категорию')
                add_action.triggered.connect(self.add_category_slot)
                # add other required actions
                menu.exec(arg__1.globalPos())
                # return super().contextMenuEvent(arg__1)


    def change_category_slot(self):
        """
        Called, when edit option of context menu is chosen
        Opens dialog window that lets user change name
        Updates categories afterwards
        """
        pk = self.last_active_item.text(1)
        print('editing')
        dlg = QtWidgets.QInputDialog(self)
        dlg.resize(200, 50)
        new_name, ok = dlg.getText(self, 'Редактирование', 'Введите новое название категории')
        attr_val_dict = {'pk': pk, 'name': new_name}
        if ok:
            self.change_category_func(attr_val_dict)


    def add_category_slot(self):
        """
        Called, when add option of context menu is chosen
        Opens dialog window that lets user enter name of new category
        Updates categories afterwards
        """
        print('adding')
        if self.last_active_item:
            parent_pk = self.last_active_item.text(1)
        else:
            parent_pk = 0
        dlg = QtWidgets.QInputDialog(self)
        dlg.resize(200, 50)
        new_name, ok = dlg.getText(self, 'Добавление', 'Введите название новой категории')
        attr_val_dict = {'parent': parent_pk, 'name': new_name}
        if ok:
            self.add_category_func(attr_val_dict)


    def delete_category_slot(self):
        """
        Called, when delete option of context menu is chosen
        Opens dialog window that asks user the way of deletion:
        with or withoud transfer of children categories
        Updates categories afterwards
        """
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


class CategoryDialog(QtWidgets.QDialog):
    """
    Dialog window that allows user to
    choose category of new expense or
    edit category of existing expense
    """
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
        """
        Called when accept button is clicked
        Sets active category when creating new expense or
        Accepts choice of category when editing expense
        """
        if getattr(self.my_parent, 'expense_table', None):
            selected_exp_category_pk = self.category_tree.currentItem().text(1)
            self.my_parent.chosen_exp_category_pk = selected_exp_category_pk
        else:
            selected_category_pk = self.category_tree.currentItem().text(1)
            selected_category_name = self.category_tree.currentItem().text(0)
            selected_category_name = '<b>' + selected_category_name + '</b>'
            self.my_parent.chosen_category_pk = selected_category_pk
            self.my_parent.chosen_category_label.setText(selected_category_name)
        self.accept()


    def update_categories(self, categories):
        """Renews categories in widget"""
        self.category_tree.update_categories(categories)


class CategoryDialogEdit(QtWidgets.QDialog):
    """
    Dialog window that allows user to manage categories
    """

    def __init__(self, parent: QtWidgets.QWidget,
                 update_func, change_func, add_func, delete_func) -> None:
        super().__init__(parent)
        self.my_parent = parent

        self.resize(400, 500)
        self.setWindowTitle('Редактирование категорий')
        layout = QtWidgets.QVBoxLayout()

        self.category_tree = CategoryTree(parent, True,
                                          update_func, change_func, add_func, delete_func)
        layout.addWidget(self.category_tree)

        button_layout = QtWidgets.QHBoxLayout()
        end_button = QtWidgets.QPushButton('Закрыть')

        end_button.clicked.connect(self.accept)
        button_layout.addWidget(end_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)


    def update_categories(self, categories):
        """Renews categories in widget"""
        self.category_tree.update_categories(categories)
