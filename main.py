from PyQt6.QtWidgets import QApplication


from main_window import MainWindow
from style import styles


def main():
    app = QApplication([])
    app.setStyleSheet(styles)


    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()