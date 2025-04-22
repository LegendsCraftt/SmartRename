import os.path
from os import fdopen
from os.path import dirname

import resources_rc

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, QPoint, QUrl
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QFont, QPalette, QColor, QIntValidator, QValidator, QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar, QHBoxLayout, QSlider, QVBoxLayout, QWidget, QPushButton, QFileDialog, QListWidget, QLineEdit, QSizePolicy,
    QGroupBox, QMessageBox, QToolTip, QListWidgetItem,
)


LOG_PATH = Path.home() / "Documents" / "smart_rename_log.txt"

handler = RotatingFileHandler(str(LOG_PATH), maxBytes=8_000_000, backupCount=3, encoding='utf-8')
formatter = logging.Formatter("%(asctime)s\t%(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

logger = logging.getLogger("SmartRename")
logger.setLevel(logging.INFO)
logger.addHandler(handler)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Rename")
        self.resize(800, 750)



        # -- FONTS --
        serifFont = QFont("Times", 28)
        serifFont.setBold(True)
        serifFont.setUnderline(True)
        self.setWindowIcon(QIcon("assets/smartrenameico.ico"))

        self.rename_history = []

        # -- Create and initialize the window and layout, we will add more layouts to the container

        central_widget = QWidget()
        container = QVBoxLayout()
        central_widget.setLayout(container)
        self.setCentralWidget(central_widget)

        # -- Top Container/layout :Title|FileMode|OpenFilesButton: --


            # -- initialize widgets --
        self.top_layout = QVBoxLayout()
        self.inner_upper_layout = QHBoxLayout()

        self.title_label = QLabel('Smart Rename')
        self.open_files_button = QPushButton('Open Files')
        self.use_files_check = QCheckBox('File Mode')
        self.open_log_button = QPushButton('Open Logs')




            # -- inner upper container --
        self.inner_upper_layout.addWidget(self.use_files_check)
        self.inner_upper_layout.addWidget(self.open_files_button)
        self.inner_upper_layout.addWidget(self.open_log_button)


        self.title_label.setFont(serifFont)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        self.top_layout.addWidget(self.title_label)
        self.top_layout.addLayout(self.inner_upper_layout)
        self.top_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.inner_upper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # -- Connections in top layout --
        self.open_files_button.clicked.connect(self.OpenFiles)
        self.open_log_button.clicked.connect(self.openLog)




        # -- Middle layout :OpenFilePreview|InputText:
        self.middle_layout = QVBoxLayout()
        self.middle_inner_layout = QVBoxLayout()

            # -- Initialize Widgets --
        self.files_preview_label = QLabel('Selected Files:')
        self.files_preview = QListWidget()

            # -- Widget Configs --
        self.files_preview.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.files_preview.setAcceptDrops(False)
        self.files_preview.dragEnterEvent = self.dragEnterEvent
        self.files_preview.dropEvent = self.dropEvent



            # -- middle layout sizing/alignment --
        self.files_preview.setMinimumSize(600, 200)
        self.files_preview.setMaximumHeight(200)
        self.files_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.middle_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.middle_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)





            # -- Add Widgets to middle layouts
        self.middle_layout.addWidget(self.files_preview_label)
        self.middle_layout.addLayout(self.middle_inner_layout)
        self.middle_inner_layout.addWidget(self.files_preview)





        # -- OPTIONS LAYOUT --

        self.options_layout = QVBoxLayout()
        self.options_inner_layout = QHBoxLayout()
        self.options_v_layout = QVBoxLayout()


            # -- Init Widgets --
        self.clear_files_button = QPushButton('Clear Files')
        self.remove_selected_file = QPushButton('Remove Selected')
        self.undo_button = QPushButton('Undo')

            # -- Widget Configs --


            # -- Widget Alignment --
        self.options_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.options_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignCenter)

        self.middle_inner_layout.addLayout(self.options_layout)



            # -- options layouts --
        self.options_inner_layout.addWidget(self.clear_files_button)
        self.options_inner_layout.addWidget(self.remove_selected_file)
        self.options_layout.addLayout(self.options_inner_layout)

            # -- Connections in Options layout --
        self.clear_files_button.clicked.connect(self.ClearFiles)
        self.remove_selected_file.clicked.connect(self.ClearFile)



        # -- Bottom layout --

        self.bottom_inner_layout = QHBoxLayout()
        self.string_layout = QHBoxLayout()
        self.options_v_layout.addLayout(self.bottom_inner_layout)


            # -- Bottom Widgets --
        self.chars_remove_label = QLabel('Chars to remove:')
        self.chars_to_remove = QLineEdit()
        self.chars_to_remove.setFixedSize(100, 30)

        self.remove_string_check = QCheckBox('Remove exact string')
        self.remove_string_text = QLineEdit()
        self.remove_spaces_check = QCheckBox('Remove all spaces')
        self.start_end_label = QLabel('From:')
        self.start_check = QCheckBox('Start')
        self.end_check = QCheckBox('End')
        self.reset_settings_button = QPushButton('Reset Settings')

        self.bottom_group = QGroupBox('Rename Settings:')

            # -- Connections --
        self.start_check.stateChanged.connect(self.SetEndState)
        self.end_check.stateChanged.connect(self.SetStartState)

        self.remove_string_check.stateChanged.connect(self.UseExactString)


            # -- Configs --
        self.chars_to_remove.setValidator(QIntValidator(0, 9999, self))

        self.chars_to_remove.inputRejected.connect(self.showInvalidTooltip)




            # -- Add widgets to layouts --
        self.bottom_inner_layout.addWidget(self.chars_remove_label)
        self.bottom_inner_layout.addWidget(self.chars_to_remove)
        self.bottom_inner_layout.addWidget(self.start_end_label)
        self.bottom_inner_layout.addWidget(self.start_check)
        self.bottom_inner_layout.addWidget(self.end_check)

        self.string_layout.addWidget(self.remove_string_check)
        self.string_layout.addWidget(self.remove_string_text)

        self.options_v_layout.addWidget(self.remove_spaces_check)
        self.options_v_layout.addLayout(self.string_layout)
        self.options_v_layout.addWidget(self.reset_settings_button, alignment=Qt.AlignmentFlag.AlignLeft)




            # -- Layout Alignment --
        self.bottom_group.setLayout(self.options_v_layout)
        self.bottom_group.setMaximumWidth(500)
        self.bottom_group.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)



        self.options_layout.addWidget(self.bottom_group, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bottom_inner_layout.setSpacing(10)
        self.bottom_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)


        # -- Output Layouts --
        self.output_label = QLabel('Output:')
        self.output_view = QListWidget()
        self.output_inner_layout = QVBoxLayout()
        self.output_layout = QVBoxLayout()
        self.output_button_layout = QHBoxLayout()
        self.apply_button = QPushButton('Apply Changes')
        self.preview_button = QPushButton('Preview Changes')



            # -- Widget Configs --
        self.output_view.setMinimumSize(600, 200)
        self.output_view.setMaximumHeight(200)


            # -- Add widgets --
        self.output_inner_layout.addWidget(self.output_label)
        self.output_inner_layout.addWidget(self.output_view)
        self.output_button_layout.addWidget(self.apply_button)
        self.output_button_layout.addWidget(self.preview_button)
        self.output_button_layout.addWidget(self.undo_button)

            # -- Alignment --
        self.output_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.output_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # -- Connections --
        self.preview_button.clicked.connect(self.OnPreview)
        self.apply_button.clicked.connect(self.OnApply)
        self.reset_settings_button.clicked.connect(self.ResetSettings)
        self.undo_button.clicked.connect(self.Undo)





        self.options_layout.addLayout(self.output_inner_layout)
        self.output_inner_layout.addLayout(self.output_button_layout)




        # -- Add layouts to container
        container.addLayout(self.top_layout)
        container.addLayout(self.middle_layout)
        container.addLayout(self.options_layout)
        container.addStretch(1)










        # -- Functions --

    def SetEndState(self, state):
        self.end_check.setEnabled(not state)
        self.remove_string_check.setEnabled(not state)
        self.remove_string_text.setEnabled(not state)


    def SetStartState(self, state):
        self.start_check.setEnabled(not state)
        self.remove_string_check.setEnabled(not state)
        self.remove_string_text.setEnabled(not state)


    def UseExactString(self, state):
        self.chars_to_remove.setEnabled(not state)
        self.start_check.setEnabled(not state)
        self.start_check.setChecked(False)
        self.end_check.setEnabled(not state)
        self.end_check.setChecked(False)
        self.chars_to_remove.clear()


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()


    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    fname = os.path.basename(file_path)
                    item = QListWidgetItem(fname)
                    item.setData(Qt.ItemDataRole.UserRole, file_path)
                    self.files_preview.addItem(item)




    def OpenFiles(self):
        if self.use_files_check.isChecked():
            files, _ = QFileDialog.getOpenFileNames(self, 'Select Files to rename')
            if files:
                self.files_preview.clear()
                for file in files:
                    self.files_preview.addItem(file)

    def openLog(self):
        path = str(LOG_PATH)
        if not Path(path).exists():
            QMessageBox.information(self, "Log not found", f"No log file at:\n{path}")
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(path))


    def ClearFiles(self):
        self.files_preview.clear()
        self.output_view.clear()


    def ClearFile(self):
        item = self.files_preview.currentItem()
        if item is not None:
            row = self.files_preview.row(item)
            self.files_preview.takeItem(row)


    def ResetSettings(self):
        self.start_check.setChecked(False)
        self.end_check.setChecked(False)
        self.remove_spaces_check.setChecked(False)
        self.remove_string_check.setChecked(False)
        self.chars_to_remove.clear()
        self.remove_string_text.clear()


    def Undo(self):
        while self.rename_history:
            old_path, new_path = self.rename_history.pop()
            dirname, fname = os.path.split(old_path)
            ndirname, nfname = os.path.split(new_path)
            try:
                os.rename(new_path, old_path)
                self.output_view.addItem(f'Undo Complete for {nfname} ❯❯❯❯ {fname}')
            except Exception as e:
                self.output_view.addItem(f'Undo failed for {nfname}: {e}')


    def TransformName(self, name: str, chars: int = 0, from_start: bool = False, from_end: bool = False, remove_spaces: bool = False, exact_str: str = '') -> str:
        if chars > 0:
            if from_start:
                name = name[chars:]

            if from_end:
                name = name[:-chars]

        if exact_str:
            name = name.replace(exact_str, '')

        if remove_spaces:
            name = name.replace(' ', '')
        return name


    def OnPreview(self):

        chars = 0

        if not self.remove_string_check.isChecked():
            chars_text = self.chars_to_remove.text().strip()
            if chars_text.isdigit():
                chars = int(chars_text)

        from_start = self.start_check.isChecked()
        from_end = self.end_check.isChecked()
        remove_spaces = self.remove_spaces_check.isChecked()
        exact_string = self.remove_string_text.text() if self.remove_string_check.isChecked() else ''

        for idx in range(self.files_preview.count()):
            item = self.files_preview.item(idx)
            full_path = item.data(Qt.ItemDataRole.UserRole)
            dirname, fname = os.path.split(full_path)
            base, ext = os.path.splitext(fname)

            new_base = self.TransformName(base, chars, from_start, from_end, remove_spaces, exact_string)

            self.output_view.addItem(f'{fname} ❯❯❯❯ {new_base+ext}')


    def OnApply(self):

        self.output_view.clear()

        changes_applied = False

        chars = 0  # default

        if not self.remove_string_check.isChecked():
            chars_text = self.chars_to_remove.text().strip()
            if chars_text.isdigit():
                chars = int(chars_text)

        from_start = self.start_check.isChecked()
        from_end = self.end_check.isChecked()
        remove_spaces = self.remove_spaces_check.isChecked()
        exact_string = self.remove_string_text.text() if self.remove_string_check.isChecked() else ''

        for idx in range(self.files_preview.count()):
            item = self.files_preview.item(idx)
            full_path = item.data(Qt.ItemDataRole.UserRole)
            dirname, fname = os.path.split(full_path)
            base, ext = os.path.splitext(fname)

            new_base = self.TransformName(base, chars, from_start, from_end, remove_spaces, exact_string)
            new_path = os.path.join(dirname, new_base + ext)
            self.rename_history.append((full_path, new_path))

            try:
                os.rename(full_path, new_path)
                logger.info(f'"{full_path}" → "{new_path}"')
                changes_applied = True

            except Exception as e:
                self.output_view.addItem(f'Failed to rename {fname}: Error: {e}')

        if changes_applied:
            self.OnPreview()
            self.output_view.addItem(f'Changes Applied!')


    def showInvalidTooltip(self):
        pos = self.chars_to_remove.mapToGlobal(
            QPoint(0, self.chars_to_remove.height())
        )
        QToolTip.showText(
            pos,
            "Only whole numbers allowed",
            self.chars_to_remove,
            self.chars_to_remove.rect(),
            1325
        )


    # ---------------------------------------------------------------------------


app = QApplication([])


# -- GLOBAL Styles --
app.setStyleSheet("""
    
 QWidget {
    background-color: #1e1e1e;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    color: #f0f0f0;
}

QPushButton {
    padding: 6px 14px;
    font-size: 13px;
    background-color: #2d2d2d;
    border: 1px solid #444;
    border-radius: 8px;
    color: white;
    transition: all 0.3s ease;
}

QPushButton:hover {
    background-color: #3c3c3c;
    border: 1px solid #5a5a5a;
    box-shadow: 0 0 4px 1px rgba(0, 120, 215, 0.5);
}

QPushButton:pressed {
    background-color: #0078d7;
    border: 1px solid #005a9e;
}

QListWidget {
    background-color: #2b2b2b;
    color: #f0f0f0;
    font-family: Consolas, monospace;
    font-size: 13px;
    border: 1px solid #444;
    border-radius: 8px;
    padding: 6px;
}

QListWidget::item:selected {
    background-color: #3a75c4;
    color: white;
    border-radius: 4px;
}

QListWidget::item:hover {
    background-color: #333;
    border-radius: 4px;
}

QGroupBox {
    border: 1px solid #444;
    border-radius: 10px;
    margin-top: 10px;
    padding: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
    font-weight: bold;
    color: #dddddd;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border-radius: 3px;
    border: 1px solid #888;
    background-color: #48574e;
}

QCheckBox::indicator:checked {
    background-color: #383837;
    border: 1px solid #789483;
    image: url(:/assets/icons-check.png);
}

QCheckBox:disabled {
    color: #777777;
}

QCheckBox::indicator:disabled {
    image: url(:/assets/check-disabled.png);
    width: 15px;
    height: 15px;
    border: 1px solid #555555;
    background-color: #2a2a2a;
    border-radius: 3px;
}

QCheckBox::indicator:checked:disabled {

    background-color: #444444;
    border: 1px solid #666666;
}

QCheckBox::indicator:disabled:hover,
QCheckBox::indicator:disabled:pressed {
    background-color: #2a2a2a;
    border: 1px solid #555555;
}

QToolTip {

    background-color: #2b2b2b;
    border: 2px solid #c8c8c8;
    border-radius: 8px;
    padding: 4px;
    font-size: 12px;
    font-family: "Segoe UI", sans-serif, white;
    color: white;
    margin: -1px;
}

QLineEdit {
    background: #2b2b2b;
    border: none;
    border-radius: 8px;
    border-bottom: 1px solid #444;
    padding: 3px;
    color: #f0f0f0;
    min-height: 22px;
    max-height: 22px;
    selection-background-color: #0078d7;
    selection-color: white;     
}

QLineEdit:disabled {
    border-bottom: 2px solid #b05a6c; 
    
}


QLineEdit:focus {
    border-bottom: 1.5px solid #dbc98c;
}


QLineEdit:hover {
    border-bottom: 1.5px solid #5a5a5a;
}

QLineEdit:focus:hover {
    border-bottom: 2px solid #cfc186;
    background: #32353b;
}





""")


window = MainWindow()
window.show()
app.exec()