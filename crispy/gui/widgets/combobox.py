# coding: utf-8

from PyQt5.QtWidgets import QComboBox


class ComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super(ComboBox, self).__init__(*args, **kwargs)

    def updateItems(self, items):
        currentText = self.currentText()
        self.blockSignals(True)
        self.clear()
        self.addItems(items)
        try:
            self.setCurrentText(currentText)
        except ValueError:
            self.setCurrentIndex(0)
        self.blockSignals(False)

def main():
    pass

if __name__ == '__main__':
    main()
