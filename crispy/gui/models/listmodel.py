# coding: utf-8

from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex


class ListModel(QAbstractListModel):
    """Class implementing a simple list model. It subclasses
    QAbstractListModel and implements the required rowCount() and
    data(). It also adds methods to insert, append, and remove items,
    and to get data stored at a given index"""

    def __init__(self, parent=None, data=list()):
        super(ListModel, self).__init__(parent)
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows in the model."""
        length = len(self._data)
        return length

    def data(self, index, role):
        """Return role specific data for the item referred by the
        index."""
        if not index.isValid():
            return
        if role == Qt.DisplayRole or role == Qt.EditRole:
            label = self._data[index.row()]['label']
            return label

    def insertItems(self, position, items, parent=QModelIndex()):
        """Insert items at a given position in the model."""
        first = position
        last = position + len(items) - 1
        self.beginInsertRows(QModelIndex(), first, last)
        for item in items:
            self._data.insert(position, item)
        self.endInsertRows()
        return True

    def removeItems(self, indexes, parent=QModelIndex()):
        """Remove items from the model."""
        rows = [index.row() for index in indexes]
        first = min(rows)
        last = max(rows)
        self.beginRemoveRows(QModelIndex(), first, last)
        for index in indexes:
            del self._data[index.row()]
        self.endRemoveRows()
        return True

    def appendItems(self, items):
        """Insert items at the end of model."""
        position = self.rowCount()
        self.insertItems(position, items)

    def getIndexData(self, index):
        """Return the data stored in the model at the given index."""
        if not index.isValid():
            return
        data = self._data[index.row()]
        return data
