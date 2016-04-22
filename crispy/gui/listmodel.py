# coding: utf-8

from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant


class ListModel(QAbstractListModel):
    """Class implementing a list model. It subclasses QAbstractListModel and
    implements rowCount() and data().

    In addition it implements setData() and flags() methods to make the model
    editable, and the insertRows() and removeRows() methods insure that the
    model allows for resizable list-like data structures."""

    def __init__(self, data, parent=None):
        super(ListModel, self).__init__(parent)
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role):
        if index.isValid() and role == Qt.DisplayRole:
            return QVariant(self._data[index.row()])
        else:
            return QVariant()

    def flags(self, index):
        activeFlags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return activeFlags

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            if role == Qt.EditRole:
                self._data[index.row()] = value
                self.dataChanged.emit(index, index)
            return True
        else:
            return False

    def insertRows(self, position, rows=1, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)

        for i in range(rows):
            self._data.insert(position + i, str())

        self.endInsertRows()

        return True

    def removeRows(self, position, rows, parent=QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)

        for i in range(rows):
            value = self._data[position]
            self._data.remove(value)

        self.endRemoveRows()

        return True

    def insertItem(self, position, item, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position)

        self._data.insert(position, item)

        self.endInsertRows()

        return True

