import os

from PyQt6.QtCore     import Qt
from PyQt6.QtGui      import QFont, QIcon, QAction, QIntValidator
from PyQt6.QtWidgets  import (QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLabel, QPushButton,
                              QCheckBox, QListWidget, QLineEdit,
                              QGroupBox, QSizePolicy, QMenu, QListWidgetItem)

from controller import MainController
import resources_rc


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Rename")
        self.setWindowIcon(QIcon("assets/smartrenameico.ico"))
        self.resize(800, 750)

        self.controller = MainController(self)
        self.rename_history = []

        self.build_ui()
        self.set_layouts()
        self.set_connections()
        self.set_configs()



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
        self.output_inner_layout = QVBoxLayout()
        self.output_layout = QVBoxLayout()
        self.output_button_layout = QHBoxLayout()

            # -- GROUPS --
        self.bottom_group = QGroupBox('Rename Settings:')


        # -- LABELS --
        self.title_label = QLabel('Smart Rename')
        self.files_preview_label = QLabel('Selected Files:')
        self.chars_remove_label = QLabel('Chars to remove:')
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
        self.undo_button = QPushButton('Undo')
        self.apply_button = QPushButton('Apply Changes')
        self.preview_button = QPushButton('Preview Changes')
        self.reset_settings_button = QPushButton('Reset Settings')


        # -- CheckBoxes --
        self.use_files_check = QCheckBox('File Mode')
        self.remove_string_check = QCheckBox('Remove exact string')
        self.remove_spaces_check = QCheckBox('Remove all spaces')
        self.start_check = QCheckBox('Start')
        self.end_check = QCheckBox('End')


        # -- LineEdits --
        self.chars_to_remove = QLineEdit()
        self.remove_string_text = QLineEdit()

    def set_layouts(self):

        # --- TOP LAYOUT ---
        self.inner_upper_layout.addWidget(self.use_files_check)
        self.inner_upper_layout.addWidget(self.open_files_button)
        self.inner_upper_layout.addWidget(self.open_log_button)

        self.top_layout.addWidget(self.title_label)
        self.top_layout.addLayout(self.inner_upper_layout)

        # --- MIDDLE LAYOUT ---
        self.middle_layout.addWidget(self.files_preview_label)
        self.middle_inner_layout.addWidget(self.files_preview)

        # --- OPTIONS LAYOUT (Clear/Remove buttons) ---
        self.options_inner_layout.addWidget(self.clear_files_button)
        self.options_inner_layout.addWidget(self.remove_selected_file)

        # --- BOTTOM GROUP CONTENTS ---
        self.bottom_inner_layout.addWidget(self.chars_remove_label)
        self.bottom_inner_layout.addWidget(self.chars_to_remove)
        self.bottom_inner_layout.addWidget(self.start_end_label)
        self.bottom_inner_layout.addWidget(self.start_check)
        self.bottom_inner_layout.addWidget(self.end_check)

        self.string_layout.addWidget(self.remove_string_check)
        self.string_layout.addWidget(self.remove_string_text)

        self.options_v_layout.addLayout(self.bottom_inner_layout)
        self.options_v_layout.addWidget(self.remove_spaces_check)
        self.options_v_layout.addLayout(self.string_layout)
        self.options_v_layout.addWidget(self.reset_settings_button, alignment=Qt.AlignmentFlag.AlignLeft)

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

        self.open_files_button.clicked.connect(self.controller.OpenFiles)
        self.open_log_button.clicked.connect(self.controller.openLog)

        self.clear_files_button.clicked.connect(self.controller.ClearFiles)
        self.remove_selected_file.clicked.connect(self.controller.ClearFile)

        self.start_check.stateChanged.connect(self.controller.SetEndState)
        self.end_check.stateChanged.connect(self.controller.SetStartState)

        self.remove_string_check.stateChanged.connect(self.controller.UseExactString)
        self.chars_to_remove.inputRejected.connect(self.controller.showInvalidTooltip)

        self.preview_button.clicked.connect(self.controller.OnPreview)
        self.apply_button.clicked.connect(self.controller.OnApply)
        self.reset_settings_button.clicked.connect(self.controller.ResetSettings)
        self.undo_button.clicked.connect(self.controller.Undo)



    def set_configs(self):

        # -- FONTS --
        serifFont = QFont("Times", 28)
        serifFont.setBold(True)
        serifFont.setUnderline(True)
        self.title_label.setFont(serifFont)

        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.top_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.inner_upper_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.files_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.middle_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        self.middle_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.options_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.options_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignCenter)
        self.bottom_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.output_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.output_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.remove_string_text.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
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

        self.bottom_group.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        self.bottom_inner_layout.setSpacing(10)


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
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    fname = os.path.basename(file_path)
                    item = QListWidgetItem(fname)
                    item.setData(Qt.ItemDataRole.UserRole, file_path)
                    self.files_preview.addItem(item)