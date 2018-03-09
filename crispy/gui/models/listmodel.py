# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

from __future__ import absolute_import, division, unicode_literals

__authors__ = ['Marius Retegan']
__license__ = 'MIT'
__date__ = '09/03/2018'


from PyQt5.QtCore import Qt, QAbstractListModel, QModelIndex


class ListModel(QAbstractListModel):
    """Class implementing a simple list model. It subclasses
    QAbstractListModel and implements the required rowCount() and
    data(). It also adds methods to insert, append, and remove items,
    and to get data stored at a given index.
    """

    def __init__(self, parent=None, modelData=list()):
        super(ListModel, self).__init__(parent)
        self.modelData = modelData

    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows in the model."""
        length = len(self.modelData)
        return length

    def data(self, index, role):
        """Return role specific data for the item referred by the
        index."""
        if not index.isValid():
            return
        row = index.row()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            label = self.modelData[row].label
            return label

    def setData(self, index, value, role):
        """Set the role data for the item at index to value."""
        if not index.isValid():
            return
        row = index.row()
        if role == Qt.EditRole:
            self.modelData[row].label = value
        self.dataChanged.emit(index, index)
        return True

    def getData(self):
        return self.modelData

    def flags(self, index):
        """Return the active flags for the given index"""
        activeFlags = (
            Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
        return activeFlags

    def insertItems(self, position, items, parent=QModelIndex()):
        """Insert items at a given position in the model."""
        first = position
        last = position + len(items) - 1
        self.beginInsertRows(QModelIndex(), first, last)
        for item in items:
            self.modelData.insert(position, item)
        self.endInsertRows()
        return True

    def removeItems(self, indexes, parent=QModelIndex()):
        """Remove items from the model."""
        rows = [index.row() for index in indexes]
        first = min(rows)
        last = max(rows)
        self.beginRemoveRows(QModelIndex(), first, last)
        for row in sorted(rows, reverse=True):
            del self.modelData[row]
        self.endRemoveRows()
        return True

    def appendItems(self, items):
        """Insert items at the end of model."""
        position = self.rowCount()
        firstIndex = self.index(position)
        lastIndex = self.index(position + len(items) - 1)
        self.insertItems(position, items)
        self.dataChanged.emit(firstIndex, lastIndex)

    def replaceItem(self, index, item):
        row = index.row()
        self.modelData[row] = item
        self.dataChanged.emit(index, index)

    def getIndexData(self, index):
        """Return the data stored in the model at the given index."""
        if not index.isValid():
            return
        data = self.modelData[index.row()]
        return data

    def reset(self):
        self.beginResetModel()
        self.modelData = list()
        self.endResetModel()
