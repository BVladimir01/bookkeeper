from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import QEvent, QObject, Qt, QSize, Signal


class CategoryItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setToolTip(0, 'right click for options')


class CategoryTree(QtWidgets.QTreeWidget):

    cat_signal = QtCore.Signal(CategoryItem)

    def __init__(self, main_window: QtWidgets.QWidget, editable: bool, update_func, change_func, add_func, delete_func):
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
        if getattr(self.my_parent, 'expense_table', None):
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
