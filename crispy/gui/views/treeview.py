# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from PyQt5.QtWidgets import QTreeView


class TreeView(QTreeView):
    """Class enabling additional functionality in QTreeView."""
    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)

    def resizeAllColumnsToContents(self):
        for i in range(self.model().columnCount(0)):
            self.resizeColumnToContents(i)
