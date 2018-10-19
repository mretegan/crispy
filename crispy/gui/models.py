# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2018 European Synchrotron Radiation Facility
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
__date__ = '19/10/2018'

from collections import OrderedDict as odict
import copy

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class SpectraModel(QStandardItemModel):

    checkStateChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super(SpectraModel, self).__init__(parent=parent)

    def setData(self, index, value, role):
        if not index.isValid():
            return
        row = index.row()
        item = self.item(row)
        if role == Qt.CheckStateRole:
            item.setCheckState(value)
            # Emit a signal with the checked items.
            checkedItems = list()
            for item in self.items():
                if item.checkState() == Qt.Checked:
                    checkedItems.append(item.text())
            self.checkStateChanged.emit(checkedItems)
        return True

    def items(self):
        rows = self.rowCount()
        for row in range(rows):
            yield self.item(row)

    def setModelData(self, items, checkedItems):
        self.clear()
        for item in items:
            modelItem = QStandardItem(item)
            if item in checkedItems:
                modelItem.setCheckState(Qt.Checked)
            else:
                modelItem.setCheckState(Qt.Unchecked)
            self.appendRow(modelItem)

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable


class ResultsModel(QAbstractItemModel):

    itemNameChanged = pyqtSignal(str)
    itemCheckStateChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(ResultsModel, self).__init__(parent=parent)
        self.header = ['Name']
        self.modelData = list()

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column)

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()):
        return len(self.modelData)

    def columnCount(self, parent=QModelIndex()):
        return len(self.header)

    def data(self, index, role):
        if not index.isValid():
            return
        row = index.row()
        item = self.modelData[row]
        if role == Qt.DisplayRole:
            return item.baseName
        elif role == Qt.EditRole:
            return item.baseName
        elif role == Qt.CheckStateRole:
            if item.isChecked:
                return Qt.Checked
            else:
                return Qt.Unchecked

    def setData(self, index, value, role):
        if not index.isValid():
            return
        row = index.row()
        item = self.modelData[row]
        if role == Qt.EditRole:
            item.baseName = value
            self.itemNameChanged.emit(value)
        elif role == Qt.CheckStateRole:
            if value == Qt.Unchecked:
                item.isChecked = False
            elif value == Qt.Checked:
                item.isChecked = True
            self.itemCheckStateChanged.emit()
        return True

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.header[section]
            if orientation == Qt.Vertical:
                return section + 1

    def flags(self, index):
        if not index.isValid():
            return
        activeFlags = (
            Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable |
            Qt.ItemIsUserCheckable)
        return activeFlags

    def insertRows(self, row, items, parent=QModelIndex()):
        first = row
        last = row + len(items) - 1
        self.beginInsertRows(QModelIndex(), first, last)
        for item in items:
            self.modelData.insert(row, item)
        self.endInsertRows()
        index = self.index(last, 0)
        self.dataChanged.emit(index, index)
        return True

    def appendItems(self, items):
        if not isinstance(items, list):
            items = [items]
        row = self.rowCount()
        self.insertRows(row, items)

    def updateItem(self, index, item):
        row = index.row()
        self.modelData[row] = copy.deepcopy(item)
        self.dataChanged.emit(index, index)

    def getItem(self, index):
        row = index.row()
        item = self.modelData[row]
        return copy.deepcopy(item)

    def getAllItems(self):
        items = list()
        rows = range(self.rowCount())
        for row in rows:
            item = self.modelData[row]
            item.index = row + 1
            items.append(item)
        return copy.deepcopy(items)

    def getCheckedItems(self):
        items = list()
        rows = range(self.rowCount())
        for row in rows:
            item = self.modelData[row]
            item.index = row + 1
            if item.isChecked:
                items.append(item)
        return copy.deepcopy(items)

    def getSelectedItems(self, indexes=None):
        if indexes is None:
            return None
        rows = {index.row() for index in indexes}
        items = list()
        for row in rows:
            item = self.modelData[row]
            item.index = row + 1
            items.append(item)
        return copy.deepcopy(items)

    def uncheckAllItems(self):
        rows = range(self.rowCount())
        for row in rows:
            item = self.modelData[row]
            item.isChecked = False

    def removeItems(self, indexes):
        rows = {index.row() for index in indexes}
        for row in sorted(rows, reverse=True):
            self.beginRemoveRows(QModelIndex(), row, row)
            try:
                del self.modelData[row]
            except IndexError:
                pass
            self.endRemoveRows()
        row = len(self.modelData) - 1
        index = self.index(row, 0)
        self.dataChanged.emit(index, index)
        return True

    def reset(self):
        self.beginResetModel()
        self.modelData = list()
        self.endResetModel()


class HamiltonianItem(object):
    """Class implementing a tree item to be used in a tree model."""

    def __init__(self, parent=None, itemData=None):
        self.parent = parent
        self.itemData = itemData
        self.children = []
        self.checkState = None

        if parent is not None:
            parent.appendChild(self)

    def appendChild(self, item):
        """Append a child to the parent item."""
        self.children.append(item)

    def getChildren(self):
        return self.children

    def child(self, row):
        """Return the child at a given row."""
        return self.children[row]

    def row(self):
        """Return the row of the child."""
        if self.parent is not None:
            children = self.parent.getChildren()
            # The index method of the list object.
            return children.index(self)
        else:
            return 0

    def childCount(self):
        return len(self.children)

    def columnCount(self):
        return len(self.itemData)

    def getItemData(self, column):
        """Return the data for a given column."""
        try:
            return self.itemData[column]
        except IndexError:
            return str()

    def setItemData(self, column, value):
        """Set the data at a given column."""
        try:
            self.itemData[column] = value
        except IndexError:
            pass

    def getCheckState(self):
        return self.checkState

    def setCheckState(self, checkState):
        self.checkState = checkState


class HamiltonianModel(QAbstractItemModel):
    """Class implementing the Hamiltonian tree model. It subclasses
    QAbstractItemModel and thus implements: index(), parent(),
    rowCount(), columnCount(), and data().

    To enable editing, the class implements setData() and reimplements
    flags() to ensure that an editable item is returned. headerData() is
    also reimplemented to control the way the header is presented.
    """

    itemCheckStateChanged = pyqtSignal(QModelIndex, Qt.CheckState)

    def __init__(self, parent=None):
        super(HamiltonianModel, self).__init__(parent)
        self.header = ['Parameter', 'Value', 'Scale Factor']
        self.modelData = odict()

    def index(self, row, column, parent=QModelIndex()):
        """Return the index of the item in the model specified by the
        given row, column, and parent index.
        """
        if parent is not None and not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = self.item(parent)

        childItem = parentItem.child(row)

        if childItem:
            index = self.createIndex(row, column, childItem)
        else:
            index = QModelIndex()

        return index

    def parent(self, index):
        """Return the index of the parent for a given index of the
        child. Unfortunately, the name of the method has to be parent,
        even though a more verbose name like parentIndex, would avoid
        confusion about what parent actually is - an index or an item.
        """
        childItem = self.item(index)
        parentItem = childItem.parent

        if parentItem == self.rootItem:
            parentIndex = QModelIndex()
        else:
            parentIndex = self.createIndex(parentItem.row(), 0, parentItem)

        return parentIndex

    def siblings(self, index):
        item = self.item(index)

        parentIndex = self.parent(index)
        parentItem = self.item(parentIndex)

        siblingIndices = list()
        for child in parentItem.children:
            if child is item:
                continue
            else:
                row = child.row()
                siblingIndex = self.index(row, 0, parentIndex)
                siblingIndices.append(siblingIndex)

        return siblingIndices

    def rowCount(self, parentIndex):
        """Return the number of rows under the given parent. When the
        parentIndex is valid, rowCount() returns the number of children
        of the parent. For this it uses item() method to extract the
        parentItem from the parentIndex, and calls the childCount() of
        the item to get number of children.
        """
        if parentIndex.column() > 0:
            return 0

        if not parentIndex.isValid():
            parentItem = self.rootItem
        else:
            parentItem = self.item(parentIndex)

        return parentItem.childCount()

    def columnCount(self, parentIndex):
        """Return the number of columns. The index of the parent is
        required, but not used, as in this implementation it defaults
        for all items to the length of the header.
        """
        return len(self.header)

    def data(self, index, role):
        """Return role specific data for the item referred by
        index.column()."""
        if not index.isValid():
            return

        item = self.item(index)
        column = index.column()
        value = item.getItemData(column)

        if role == Qt.DisplayRole:
            try:
                if column == 1:
                    # Display small values using scientific notation.
                    if abs(float(value)) < 1e-3 and float(value) != 0.0:
                        return '{0:8.1e}'.format(value)
                    else:
                        return '{0:8.3f}'.format(value)
                else:
                    return '{0:8.2f}'.format(value)
            except ValueError:
                return value
        elif role == Qt.EditRole:
            try:
                value = float(value)
                if abs(value) < 1e-3 and value != 0.0:
                    return str('{0:8.1e}'.format(value))
                else:
                    return str('{0:8.3f}'.format(value))
            except ValueError:
                return str(value)
        elif role == Qt.CheckStateRole:
            if item.parent == self.rootItem and column == 0:
                return item.getCheckState()
        elif role == Qt.TextAlignmentRole:
            if column > 0:
                return Qt.AlignRight

    def setData(self, index, value, role):
        """Set the role data for the item at index to value."""
        if not index.isValid():
            return False

        item = self.item(index)
        column = index.column()

        if role == Qt.EditRole:
            items = list()
            items.append(item)

            if self.sync:
                parentIndex = self.parent(index)
                # Iterate over the siblings of the parent index.
                for sibling in self.siblings(parentIndex):
                    siblingNode = self.item(sibling)
                    for child in siblingNode.children:
                        if child.getItemData(0) == item.getItemData(0):
                            items.append(child)

            for item in items:
                columnData = str(item.getItemData(column))
                if columnData and columnData != value:
                    try:
                        item.setItemData(column, float(value))
                    except ValueError:
                        return False
                else:
                    return False

        elif role == Qt.CheckStateRole:
            item.setCheckState(value)
            if value == Qt.Unchecked or value == Qt.Checked:
                state = value
                self.itemCheckStateChanged.emit(index, state)

        self.dataChanged.emit(index, index)

        return True

    def setSyncState(self, flag):
        self.sync = flag

    def flags(self, index):
        """Return the active flags for the given index. Add editable
        flag to items other than the first column.
        """
        activeFlags = (Qt.ItemIsEnabled | Qt.ItemIsSelectable |
                       Qt.ItemIsUserCheckable)

        item = self.item(index)
        column = index.column()

        if column > 0 and not item.childCount():
            activeFlags = activeFlags | Qt.ItemIsEditable

        return activeFlags

    def headerData(self, section, orientation, role):
        """Return the data for the given role and section in the header
        with the specified orientation.
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]

    def item(self, index):
        if index is None or not index.isValid():
            return self.rootItem
        return index.internalPointer()

    def setModelData(self, modelData, parentItem=None):
        if parentItem is None:
            self.rootItem = HamiltonianItem(None, self.header)
            parentItem = self.rootItem

        if isinstance(modelData, dict):
            for key, value in modelData.items():
                if isinstance(value, dict):
                    item = HamiltonianItem(parentItem, [key])
                    self.setModelData(value, item)
                elif isinstance(value, float):
                    item = HamiltonianItem(parentItem, [key, value])
                elif isinstance(value, list):
                    item = HamiltonianItem(
                        parentItem, [key, value[0], value[1]])
                else:
                    raise TypeError

    def setHeaderData(self, header):
        self.header = header

    def updateModelData(self, modelData, parentIndex=None):
        parentItem = self.item(parentIndex)

        if parentItem.childCount():
            for child in parentItem.children:
                key = child.itemData[0]
                childData = modelData[key]
                childIndex = self.index(child.row(), 0, parentIndex)
                self.updateModelData(childData, childIndex)
        else:
            if isinstance(modelData, float):
                parentItem.setItemData(1, modelData)
            elif isinstance(modelData, list):
                value, scaling = modelData
                parentItem.setItemData(1, value)
                parentItem.setItemData(2, scaling)
            else:
                raise TypeError
            self.dataChanged.emit(parentIndex, parentIndex)
            return True

    def _getModelData(self, modelData, parentItem=None):
        """Return the data contained in the model."""
        if parentItem is None:
            parentItem = self.rootItem

        for item in parentItem.getChildren():
            key = item.getItemData(0)
            if item.childCount():
                modelData[key] = odict()
                self._getModelData(modelData[key], item)
            else:
                if isinstance(item.getItemData(2), float):
                    modelData[key] = [item.getItemData(1), item.getItemData(2)]
                else:
                    modelData[key] = item.getItemData(1)

    def getModelData(self):
        modelData = odict()
        self._getModelData(modelData)
        return modelData

    def setNodesCheckState(self, checkState, parentItem=None):
        if parentItem is None:
            parentItem = self.rootItem

        children = parentItem.getChildren()

        for child in children:
            childName = child.itemData[0]
            try:
                child.setCheckState(checkState[childName])
            except KeyError:
                pass

    def getNodesCheckState(self, parentItem=None):
        """Return the check state (disabled, tristate, enable) of all items
        belonging to a parent.
        """
        if parentItem is None:
            parentItem = self.rootItem

        checkStates = odict()
        children = parentItem.getChildren()

        for child in children:
            checkStates[child.itemData[0]] = child.getCheckState()

        return checkStates

    def reset(self):
        self.beginResetModel()
        self.rootItem = None
        self.endResetModel()
