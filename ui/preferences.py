from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QLineEdit, QPushButton, QHBoxLayout

from data.settings import add_saved_rm_string, remove_saved_rm_string
from assets.resources import resources_rc


class PreferencesDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Saved Strings")
        self.setWindowIcon(QIcon(":/assets/SmartRename_Icon_Window.png"))

        main_layout = QVBoxLayout(self)
        self.list = QListWidget(self)
        self.list.addItems(settings.value("removeStringsSaved", [], type=list))
        self.new_str_input = QLineEdit()

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_item)

        rmv_btn = QPushButton("Remove")
        rmv_btn.clicked.connect(self.remove_item)

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_item)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(rmv_btn)
        btn_layout.addWidget(edit_btn)


        main_layout.addWidget(self.list)
        main_layout.addWidget(self.new_str_input)
        main_layout.addLayout(btn_layout)


    def add_item(self):
        text = self.new_str_input.text()
        if text:
            items = [self.list.item(i).text() for i in range(self.list.count())]
            if text not in items:
                self.list.addItem(text)
                items.append(text)
                add_saved_rm_string(text)
                self.new_str_input.clear()

    def remove_item(self):
        items = self.list.selectedItems()
        if items is not None:
            for item in items:
                row = self.list.row(item)
                self.list.takeItem(row)
                remove_saved_rm_string(item.text())
        self.list.clearSelection()

    def edit_item(self):
        ...
