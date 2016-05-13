# coding: utf-8

from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex, QVariant


class ListModel(QAbstractListModel):
    """Class implementing a simple list model. It subclasses QAbstractListModel
    and implements the required rowCount() and data(). It also adds methods to
    insert and append items, and to get model's data at an index.
    """

    def __init__(self, data, parent=None):
        super(ListModel, self).__init__(parent)
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows in the model.

        Returns
        -------
        n : int
            Number of items in the model.
        """
        return len(self._data)

    def data(self, index, role):
        """Return role specific data for the item referred by index.column().

        Parameters
        ----------
        index : QModelIndex
            Index of the item for which data is requested.

        role : int
            Qt display role used by the view to indicate to the model
            which type of data it needs

        Returns
        -------
        data : QVariant
            Role specific data at the given index.
        """
        if not index.isValid():
            return QVariant

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return QVariant(self._data[index.row()][0])

    def insertItem(self, position, item, parent=QModelIndex()):
        """Insert an item at the specified position in the model's data.

        Parameters
        ----------
        position : int
            List index where the item should be added.

        item : list
            Item to be added at the specified position.
        """
        self.beginInsertRows(parent, position, position)

        self._data.insert(position, item)

        self.endInsertRows()

        return True

    def appendItem(self, item):
        """Append an item at the end of the model's data.

        Parameters
        ----------
        item : list
            Item to be appended.
        """
        position = self.rowCount()
        self.insertItem(position, item)

    def getIndexData(self, index):
        """Return model's data at the given index.

        Parameters
        ----------
        index : QModelIndex
            Index of the item to be retrieved.

        Returns
        -------
        data : list
            Data at the given index.

        """
        if index.isValid():
            data = self._data[index.row()]
            return data
