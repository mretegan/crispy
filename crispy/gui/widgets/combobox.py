# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from PyQt5.QtWidgets import QComboBox


class ComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super(ComboBox, self).__init__(*args, **kwargs)

    def updateItems(self, items, currentText):
        # currentText = self.currentText()
        self.blockSignals(True)
        self.clear()
        self.addItems(items)
        try:
            self.setCurrentText(currentText)
        except ValueError:
            self.setCurrentIndex(0)
        self.blockSignals(False)
        return self.currentText()
