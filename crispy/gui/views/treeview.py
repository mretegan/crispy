# coding: utf-8

import collections

from PyQt5.QtWidgets import QTreeView


class TreeView(QTreeView):
    """Class enabling additional functionality in QTreeView."""
    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)

    def resizeAllColumns(self):
        for i in range(self.model().columnCount(0)):
            self.resizeColumnToContents(i)

def main():
    pass

if __name__ == '__main__':
    main()