# coding: utf-8

from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant


class ListModel(QAbstractListModel):
    """Class implementing a simple list model. It subclasses QAbstractListModel
    and implements the required rowCount() and data(). It also adds methods to
    insert and append items, and to get model's data at an index."""

    def __init__(self, data, parent=None):
        super(ListModel, self).__init__(parent)
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role):
        if not index.isValid():
            return QVariant

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return QVariant(self._data[index.row()][0])

    def insertItem(self, position, item, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position)

        self._data.insert(position, item)

        self.endInsertRows()

        return True

    def appendItem(self, item):
        position = self.rowCount()
        self.insertItem(position, item)

    def getIndexData(self, index):
        if index.isValid():
            return self._data[index.row()]
