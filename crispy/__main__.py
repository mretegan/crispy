# coding: utf-8

def main():
    import sys

    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication

    from .gui.main import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('Crispy')
    window.show()

    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
