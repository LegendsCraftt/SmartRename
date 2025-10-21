from PyQt6.QtWidgets import QApplication


from ui.main_window import MainWindow
from assets.resources.style import styles

from custom_widgets.resource_loader import qss, stream


def main():
    app = QApplication([])
    app.setStyleSheet(stream)

    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()