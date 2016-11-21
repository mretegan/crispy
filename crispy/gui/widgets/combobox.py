# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from PyQt5.QtWidgets import QComboBox


class ComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super(ComboBox, self).__init__(*args, **kwargs)

    def setItems(self, items, currentItem):
        self.blockSignals(True)
        self.clear()
        self.addItems(items)
        self.setCurrentText(currentItem)
        self.blockSignals(False)
