###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Custom models."""

import logging

from silx.gui.qt import QAbstractItemModel, QModelIndex, Qt

from crispy.items import RootItem

logger = logging.getLogger(__name__)


class TreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._rootItem = RootItem(parent=self)
        self._header = ["Name", "Value", "Scale Factor"]

    def index(self, row, column, parent=QModelIndex()):
        """Return the index of the item in the model specified by row, column, and
        parent index."""
        # If the item has no parent it is the root item. Otherwise, get the parent item
        # from the parent index.
        if not parent.isValid():
            parentItem = self.rootItem()
        else:
            parentItem = self.itemFromIndex(parent)

        # Get the child at the position specified by row.
        childItem = parentItem.child(row)

        # If the child item exists, create an index for it.
        if childItem is not None:
            return self.createIndex(row, column, childItem)
        return QModelIndex()

    def parent(self, index):
        """Return the index of the parent for a child index."""
        # Use the index of the child to get the child item.
        childItem = self.itemFromIndex(index)

        if childItem is self.rootItem():
            return QModelIndex()

        # Call the parent() method of the child to get the parent item.
        parentItem = childItem.parent()

        # If the parent item is the root item, create an index for it.
        if parentItem is self.rootItem():
            return QModelIndex()

        return self.createIndex(parentItem.childPosition(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        item = self.itemFromIndex(parent)
        return item.rowCount()

    def columnCount(self, parent=QModelIndex()):
        return len(self.header())

    def data(self, index, role=Qt.DisplayRole):
        item = self.itemFromIndex(index)
        column = index.column()
        return item.data(column, role)

    def setData(self, index, value, role=Qt.EditRole):
        item = self.itemFromIndex(index)
        column = index.column()
        if item.setData(column, value, role):
            return True
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._header[section]
            if orientation == Qt.Vertical:
                return section + 1
        return None

    def header(self):
        return self._header

    def setHeader(self, value):
        self._header = value

    def flags(self, index):
        item = self.itemFromIndex(index)
        return item.flags(index.column())

    def rootItem(self):
        return self._rootItem

    def itemFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        return self.rootItem()

    def indexFromItem(self, item):
        if item == self.rootItem():
            return QModelIndex()
        return self.createIndex(item.childPosition(), 0, item)

    def lastIndex(self):
        return self.index(self.rowCount() - 1, 0)

    def firstIndex(self):
        return self.index(0, 0)
