# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def main():
    import sys

    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication

    from .gui.main import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
