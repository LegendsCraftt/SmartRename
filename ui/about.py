from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class About(QDialog):
    def __init__(self, style: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Rename | About")
        self.setMinimumWidth(500)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("About")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel(
            "Smart Rename — Batch File Renaming Utility\n"
            "Version 1.1.0\n\n"
            "Developed by Tyler Emery\n"
            "Email: tylere@metalsfab.com\n\n"
            "Smart Rename helps streamline batch file renaming with live previews, undo support, and user friendly experience\n\n"
            
            "Usage:\n"
            "▶  Choose or drag and drop files to begin.\n"
            "▶  Enter a word to remove from the batch of files, or a number of characters\n    to remove from the start/end.\n"
            "▶  Check whether or not to remove all spaces from the file names.\n"
            "▶  Click 'Preview' to see the results of your changes.\n"
            "▶  Click 'Apply' to apply the changes to the files.\n\n"
            
            "Tips:\n"
            "▶  Use the preview window to confirm results before applying.\n"
            "▶  Undo/Redo actions are supported after applying changes.\n"
            "▶  See Shortcuts for more information on keyboard shortcuts."
        )

        desc.setWordWrap(True)
        desc.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(desc)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)

        if style == 'dark':
            self.setStyleSheet("""

                QDialog {
                    background-color: #1E1E1E;
                }

                QLabel {
                    font-size: 14px;
                    color: #fff;
                }
                QPushButton {
                    padding: 6px 16px;
                    background-color: #444;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
            """)

        if style == 'light':
            self.setStyleSheet("""

                      QDialog {
                          background-color: #FAFAFA;
                      }

                      QLabel {
                          font-size: 14px;
                          color: #000;
                      }
                      QPushButton {
                          padding: 6px 16px;
                          background-color: rgba(0,0,0,0.1);
                          border-radius: 6px;
                      }
                      QPushButton:hover {
                          background-color: rgba(0,0,0,0.08);
                      }
                  """)

