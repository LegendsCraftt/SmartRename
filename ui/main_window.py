import os

from PyQt6.QtCore     import Qt
from PyQt6.QtGui import QFont, QIcon, QAction, QIntValidator, QPainter, QLinearGradient, QColor, QImage
from PyQt6.QtWidgets  import (QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QPushButton,
                              QCheckBox, QListWidget, QLineEdit,
                              QGroupBox, QSizePolicy, QMenu, QListWidgetItem)

import numpy as np

from controller.controller import MainController
from custom_widgets.toast import Toast
from data.settings import settings
from ui.help import HelpPanel
from ui.menu import SlideOverPanel
from ui.preferences import PreferencesDialog
from ui.shortcuts import Shortcuts


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Rename")
        self.setWindowIcon(QIcon(":/assets/SmartRename_Icon_Window.png"))
        self.resize(800, 790)

        self.controller = MainController(self)
        self.rename_history: dict = {'undo': [],
                                     'redo': []}

        self.build_ui()
        self.set_layouts()
        self.set_connections()
        self.set_configs()
        self.set_object_names()
        self.set_shortcuts()

        self.settings = settings
        self.toasts = Toast(self)

        self.rolling_history = False # add option to menu later to toggle this.



    def build_ui(self):

        # -- Create and initialize the window and layout
        central_widget = QWidget()
        self.container = QVBoxLayout()
        central_widget.setLayout(self.container)
        self.setCentralWidget(central_widget)


        # -- LAYOUTS --
            # -- TOP LAYOUTS --
        self.top_layout = QVBoxLayout()
        self.inner_upper_layout = QHBoxLayout()

            # -- MIDDLE LAYOUTS --
        self.middle_layout = QVBoxLayout()
        self.middle_inner_layout = QVBoxLayout()

            # -- OPTIONS LAYOUT --
        self.options_layout = QVBoxLayout()
        self.options_inner_layout = QHBoxLayout()
        self.options_v_layout = QVBoxLayout()

            # -- BOTTOM LAYOUTS --
        self.bottom_inner_layout = QHBoxLayout()
        self.string_layout = QHBoxLayout()
        self.replace_layout = QHBoxLayout()
        self.output_inner_layout = QVBoxLayout()
        self.output_layout = QVBoxLayout()
        self.output_button_layout = QHBoxLayout()
        self.rename_reset_menu_container = QHBoxLayout()

            # -- GROUPS --
        self.bottom_group = QGroupBox('Rename Settings')


        # -- LABELS --
        self.title_label = QLabel('Smart Rename')
        self.files_preview_label = QLabel('Selected Files:')
        self.chars_remove_label = QLabel('Characters to Trim:')
        self.start_end_label = QLabel('From:')
        self.output_label = QLabel('Output:')


        # -- List Widgets --
        self.files_preview = QListWidget()
        self.output_view = QListWidget()


        # -- Buttons --
        self.open_files_button = QPushButton('Open Files')
        self.open_log_button = QPushButton('Open Logs')
        self.clear_files_button = QPushButton('Clear Files')
        self.remove_selected_file = QPushButton('Remove Selected')
        self.stack_files_check = QCheckBox('Stack Files')

        self.undo_button = QPushButton('Undo')
        self.apply_button = QPushButton('Apply Changes')
        self.preview_button = QPushButton('Preview Changes')
        self.reset_settings_button = QPushButton('Reset')
        self.rename_settings_menu_button = QPushButton('☰ Menu')


        # -- CheckBoxes --

        self.start_check = QCheckBox('Start')
        self.end_check = QCheckBox('End')

        self.remove_spaces_check = QCheckBox('Remove all spaces')
        self.remove_string_check = QCheckBox('Remove Specific Text')

        self.replace_string_check = QCheckBox('Replace Specific Text ')


        self.menu = SlideOverPanel(self, width=200)
        self.help_menu = HelpPanel(self, width=200)


        # -- LineEdits --
        self.chars_to_remove = QLineEdit()
        self.remove_string_text = QLineEdit()

        self.replace_string_text = QLineEdit()
        self.replace_string_replace_text = QLineEdit()

    def set_layouts(self):

        # --- TOP LAYOUT ---
        self.inner_upper_layout.addWidget(self.open_files_button)
        self.inner_upper_layout.addWidget(self.open_log_button)

        self.top_layout.addWidget(self.title_label)
        self.top_layout.addLayout(self.inner_upper_layout)

        # --- MIDDLE LAYOUT ---
        self.middle_layout.addWidget(self.files_preview_label)
        self.middle_inner_layout.addWidget(self.files_preview)

        # --- OPTIONS LAYOUT (Clear/Remove buttons) ---
        self.options_inner_layout.addSpacing(290)
        self.options_inner_layout.addWidget(self.clear_files_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.options_inner_layout.addWidget(self.remove_selected_file, alignment=Qt.AlignmentFlag.AlignCenter)
        self.options_inner_layout.addStretch()
        self.options_inner_layout.addWidget(self.stack_files_check, alignment=Qt.AlignmentFlag.AlignRight)
        self.options_inner_layout.addSpacing(10)

        # --- BOTTOM GROUP CONTENTS ---
        self.bottom_inner_layout.addWidget(self.chars_remove_label)
        self.bottom_inner_layout.addWidget(self.chars_to_remove)
        self.bottom_inner_layout.addWidget(self.start_end_label)
        self.bottom_inner_layout.addWidget(self.start_check)
        self.bottom_inner_layout.addWidget(self.end_check)

        self.string_layout.addWidget(self.remove_string_check, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.string_layout.addWidget(self.remove_string_text, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.replace_layout.addWidget(self.replace_string_check, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.replace_layout.addWidget(self.replace_string_text, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.replace_layout.addWidget(self.replace_string_replace_text, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.rename_reset_menu_container.addWidget(self.reset_settings_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.rename_reset_menu_container.addWidget(self.rename_settings_menu_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.options_v_layout.addLayout(self.bottom_inner_layout)
        self.options_v_layout.addWidget(self.remove_spaces_check)
        self.options_v_layout.addLayout(self.string_layout)
        self.options_v_layout.addLayout(self.replace_layout)
        self.options_v_layout.addSpacing(8)
        self.options_v_layout.addLayout(self.rename_reset_menu_container)

        self.bottom_group.setLayout(self.options_v_layout)
        self.options_layout.addLayout(self.options_inner_layout)
        self.options_layout.addWidget(self.bottom_group, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- OUTPUT SECTION ---
        self.output_inner_layout.addWidget(self.output_label)
        self.output_inner_layout.addWidget(self.output_view)
        self.output_button_layout.addWidget(self.apply_button)
        self.output_button_layout.addWidget(self.preview_button)
        self.output_button_layout.addWidget(self.undo_button)
        self.output_inner_layout.addLayout(self.output_button_layout)

        # --- Nesting Order ---
        self.options_layout.addLayout(self.output_inner_layout)
        self.middle_inner_layout.addLayout(self.options_layout)
        self.middle_layout.addLayout(self.middle_inner_layout)

        # --- Container Assembly ---
        self.container.addLayout(self.top_layout)
        self.container.addLayout(self.middle_layout)
        self.container.addLayout(self.options_layout)
        self.container.addStretch(1)

    def set_connections(self):

        self.open_files_button.clicked.connect(self.controller.open_files)
        self.open_log_button.clicked.connect(self.controller.open_log)

        self.clear_files_button.clicked.connect(self.controller.clear_files)
        self.remove_selected_file.clicked.connect(self.controller.clear_file)

        self.start_check.stateChanged.connect(self.controller.set_end_state)
        self.end_check.stateChanged.connect(self.controller.set_start_state)

        self.remove_string_check.stateChanged.connect(self.controller.use_exact_string)
        self.chars_to_remove.inputRejected.connect(lambda: self.controller.validate_chars_input(self.chars_to_remove.text()))
        self.replace_string_check.stateChanged.connect(self.controller.replace_string)


        self.preview_button.clicked.connect(lambda: self.controller.on_preview(self.rolling_history, is_preview=True))
        self.apply_button.clicked.connect(self.controller.on_apply)
        self.reset_settings_button.clicked.connect(self.controller.reset_settings)
        self.undo_button.clicked.connect(self.controller.undo)

        self.remove_string_text.customContextMenuRequested.connect(self.controller.show_rm_str_context_menu)

        self.rename_settings_menu_button.clicked.connect(self.menu.toggle)
        self.menu.preferences_button.clicked.connect(lambda: PreferencesDialog(self.settings, self).exec())
        self.menu.help_button.clicked.connect(self.controller.help)

        self.help_menu.shortcuts_button.clicked.connect(self.controller.shortcuts)
        self.help_menu.about_button.clicked.connect(self.controller.about)



    def set_object_names(self):
        # --- Window ---
        self.setObjectName("MainWindow")
        self.bottom_group.setObjectName("bottomGroup")

        self.rename_reset_menu_container.setObjectName("renameResetMenuContainer")

        # --- Labels ---
        self.title_label.setObjectName("titleLabel")
        self.files_preview_label.setObjectName("filesPreviewLabel")
        self.chars_remove_label.setObjectName("charsRemoveLabel")
        self.start_end_label.setObjectName("startEndLabel")
        self.output_label.setObjectName("outputLabel")

        # --- List Widgets ---
        self.files_preview.setObjectName("filesPreview")
        self.output_view.setObjectName("outputView")

        # --- Buttons ---
        self.open_files_button.setObjectName("openFilesButton")
        self.open_log_button.setObjectName("openLogButton")
        self.clear_files_button.setObjectName("clearFilesButton")
        self.remove_selected_file.setObjectName("removeSelectedFileButton")
        self.stack_files_check.setObjectName("stackFilesCheck")
        self.undo_button.setObjectName("undoButton")
        self.apply_button.setObjectName("applyButton")
        self.preview_button.setObjectName("previewButton")
        self.reset_settings_button.setObjectName("resetSettingsButton")
        self.rename_settings_menu_button.setObjectName("renameSettingsMenuButton")


        # --- CheckBoxes ---
        self.remove_string_check.setObjectName("removeStringCheck")
        self.remove_spaces_check.setObjectName("removeSpacesCheck")
        self.start_check.setObjectName("startCheck")
        self.end_check.setObjectName("endCheck")


        # --- LineEdits ---
        self.chars_to_remove.setObjectName("charsToRemove")
        self.remove_string_text.setObjectName("removeStringText")
        self.replace_string_text.setObjectName("replaceStringText")
        self.replace_string_replace_text.setObjectName("replaceStringReplaceText")

    def set_configs(self):

        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.top_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.inner_upper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.files_preview_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.middle_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.middle_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.options_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.options_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignCenter)
        self.bottom_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.output_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.output_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.remove_string_text.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.remove_string_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.remove_string_text.setPlaceholderText('Text to remove..')
        self.remove_string_text.setTextMargins(4, 2, 4, 2)

        self.chars_to_remove.setTextMargins(4, 2, 4, 2)
        self.replace_string_text.setTextMargins(4, 2, 4, 2)
        self.replace_string_replace_text.setTextMargins(4, 2, 4, 2)


        self.replace_string_text.setPlaceholderText('Text to replace..')
        self.replace_string_replace_text.setPlaceholderText('With..')

        self.chars_to_remove.setValidator(QIntValidator(0, 9999, self))

        self.files_preview.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.files_preview.setAcceptDrops(False)
        self.files_preview.dragEnterEvent = self.dragEnterEvent
        self.files_preview.dropEvent = self.dropEvent

        self.files_preview.setMinimumSize(600, 200)
        self.files_preview.setMaximumHeight(200)
        self.chars_to_remove.setFixedSize(100, 30)
        self.bottom_group.setMaximumWidth(500)
        self.output_view.setMinimumSize(600, 200)
        self.output_view.setMaximumHeight(200)
        self.output_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.bottom_group.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        self.bottom_inner_layout.setSpacing(10)

    def set_shortcuts(self):
        self.keyPressEvent = self.keyPressEvent


    def build_menu(self):
        menu: QMenu = self.remove_string_text.createStandardContextMenu()
        menu.addSeparator()
        recents_action = QAction('Recents')
        menu.addAction(recents_action)
        return menu

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.controller.drop_event(event)

    def keyPressEvent(self, event):
        key = event.key()
        mods = event.modifiers()

        if key == Qt.Key.Key_Return and mods == Qt.KeyboardModifier.ControlModifier:
            self.controller.on_apply()
            return

        elif key == Qt.Key.Key_Return:
            self.controller.on_preview(self.rolling_history, is_preview=True)
            return

        elif key == Qt.Key.Key_Tab and mods == Qt.KeyboardModifier.ControlModifier:
            self.remove_string_check.toggle()
            self.remove_string_text.setFocus()
            return

        elif key == Qt.Key.Key_S and mods == Qt.KeyboardModifier.ControlModifier:
            self.remove_spaces_check.toggle()
            return

        elif key == Qt.Key.Key_T and mods == Qt.KeyboardModifier.ControlModifier:
            self.chars_to_remove.setFocus()
            return

        elif key == Qt.Key.Key_O and mods == Qt.KeyboardModifier.ControlModifier:
            self.controller.open_files()
            return

        elif key == Qt.Key.Key_L and mods == Qt.KeyboardModifier.ControlModifier:
            self.controller.open_log()
            return

        elif key == Qt.Key.Key_R and mods == Qt.KeyboardModifier.ControlModifier:
            self.controller.reset_settings()
            return

        elif key == Qt.Key.Key_M and mods == Qt.KeyboardModifier.ControlModifier:
            self.menu.toggle()
            self.menu.preferences_button.setFocus()
            return

        super().keyPressEvent(event)

        #
        # self.preview_button.clicked.connect(lambda: self.controller.on_preview(self.rolling_history, is_preview=True))
        # self.apply_button.clicked.connect(self.controller.on_apply)