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
__date__ = '17/01/2017'


import collections

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex, pyqtSignal


class TreeNode(object):
    """Class implementing a tree node to be used in a tree model."""

    def __init__(self, data, parent=None):
        self.data = data
        self.parent = parent
        self.children = []
        self.checkState = None

        if parent is not None:
            parent.appendChild(self)

    def appendChild(self, node):
        """Append a child to the parent node."""
        self.children.append(node)

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
        return len(self.data)

    def getItemData(self, column):
        """Return the data for a given column."""
        try:
            return self.data[column]
        except IndexError:
            return str()

    def setItemData(self, column, value):
        """Set the data at a given column."""
        try:
            self.data[column] = value
        except IndexError:
            pass

    def getCheckState(self):
        return self.checkState

    def setCheckState(self, checkState):
        self.checkState = checkState


class TreeModel(QAbstractItemModel):
    """Class implementing a basic tree model. It subclasses
    QAbstractItemModel and thus implements: index(), parent(),
    rowCount(), columnCount(), and data().

    To enable editing, the class implements setData() and reimplements
    flags() to ensure that an editable item is returned. headerData() is
    also reimplemented to control the way the header is presented.
    """

    nodeCheckStateChanged = pyqtSignal(QModelIndex)

    def __init__(self, header, data, parent=None):
        super(TreeModel, self).__init__(parent)
        self.header = header
        self.data = data
        self.setModelData(self.data)

    def index(self, row, column, parentIndex=None):
        """Return the index of the item in the model specified by the
        given row, column, and parent index.
        """
        if parentIndex is None or not parentIndex.isValid():
            parentNode = self.rootNode
        else:
            parentNode = self.getNode(parentIndex)

        childNode = parentNode.child(row)

        if childNode:
            index = self.createIndex(row, column, childNode)
        else:
            index = QModelIndex()

        return index

    def parent(self, childIndex):
        """Return the index of the parent for a given index of the
        child. Unfortunately, the name of the method has to be parent,
        even though a more verbose name like parentIndex, would avoid
        confusion about what parent actually is - an index or an item.
        """
        childNode = self.getNode(childIndex)
        parentNode = childNode.parent

        if parentNode == self.rootNode:
            parentIndex = QModelIndex()
        else:
            parentIndex = self.createIndex(parentNode.row(), 0, parentNode)

        return parentIndex

    def rowCount(self, parentIndex):
        """Return the number of rows under the given parent. When the
        parentIndex is valid, rowCount() returns the number of children
        of the parent. For this it uses getNode() method to extract the
        parentNode from the parentIndex, and calls the childCount() of
        the node to get number of children.
        """
        if parentIndex.column() > 0:
            return 0

        if not parentIndex.isValid():
            parentNode = self.rootNode
        else:
            parentNode = self.getNode(parentIndex)

        return parentNode.childCount()

    def columnCount(self, parentIndex):
        """Return the number of columns. The index of the parent is
        required, but not used, as in this implementation it defaults
        for all nodes to the length of the header.
        """
        return len(self.header)

    def data(self, index, role):
        """Return role specific data for the item referred by
        index.column()."""
        if not index.isValid():
            pass

        node = self.getNode(index)
        column = index.column()
        value = node.getItemData(column)

        if role == Qt.DisplayRole:
            try:
                if column == 1:
                    return '{0:8.2f}'.format(value)
                else:
                    return '{0:8.2f}'.format(value)
            except ValueError:
                return value

        if role == Qt.EditRole:
            return str(value)

        if role == Qt.CheckStateRole:
            if node.parent == self.rootNode and column == 0:
                return node.getCheckState()

        if role == Qt.TextAlignmentRole:
            if column > 0:
                return Qt.AlignRight

    def setData(self, index, value, role):
        """Set the role data for the item at index to value."""
        if not index.isValid():
            return False

        node = self.getNode(index)
        column = index.column()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column > 0 and not node.childCount():
                try:
                    node.setItemData(column, float(value))
                except ValueError:
                    return False
            else:
                node.setItemData(column, value)

        elif role == Qt.CheckStateRole:
            node.setCheckState(value)
            if value == Qt.Checked:
                self.nodeCheckStateChanged.emit(index)

        self.dataChanged.emit(index, index)

        return True

    def flags(self, index):
        """Return the active flags for the given index. Add editable
        flag to items in the first colum or greater.
        """
        activeFlags = (Qt.ItemIsEnabled | Qt.ItemIsSelectable |
                       Qt.ItemIsUserCheckable)

        node = self.getNode(index)
        column = index.column()

        if column > 0 and not node.childCount():
            activeFlags = activeFlags | Qt.ItemIsEditable

        return activeFlags

    def headerData(self, section, orientation, role):
        """Return the data for the given role and section in the header
        with the specified orientation.
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[section]

    def getNode(self, index):
        if not index.isValid():
            return self.rootNode

        return index.internalPointer()

    def setModelData(self, data, parentNode=None):
        if parentNode is None:
            self.data = data
            self.rootNode = TreeNode(self.header)
            parentNode = self.rootNode

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    node = TreeNode([key], parentNode)
                    self.setModelData(value, node)
                # Not very nice, but works.
                elif isinstance(value, float):
                    node = TreeNode([key, value], parentNode)
                elif isinstance(value, list):
                    node = TreeNode([key, value[0], value[1]], parentNode)
                elif isinstance(value, tuple):
                    node = TreeNode([key, value[0], value[1]], parentNode)
                else:
                    return

    def _getModelData(self, data, parentNode=None):
        """Return the data contained in the model."""
        if parentNode is None:
            parentNode = self.rootNode

        for node in parentNode.getChildren():
            key = node.getItemData(0)
            if node.childCount():
                data[key] = collections.OrderedDict()
                self._getModelData(data[key], node)
            else:
                if isinstance(node.getItemData(2), float):
                    data[key] = [node.getItemData(1), node.getItemData(2)]
                else:
                    data[key] = node.getItemData(1)

    def getModelData(self):
        data = collections.OrderedDict()
        self._getModelData(data)
        self.data = data
        return self.data

    def setNodesCheckState(self, data, parentNode=None):
        if parentNode is None:
            parentNode = self.rootNode

        children = parentNode.getChildren()

        for child in children:
            childName = child.data[0]
            try:
                child.setCheckState(data[childName])
            except KeyError:
                pass

    def getNodesCheckState(self, parentNode=None):
        """Return the check state (disabled, tristate, enable) of all nodes
        belonging to a parent.
        """
        if parentNode is None:
            parentNode = self.rootNode

        data = collections.OrderedDict()
        children = parentNode.getChildren()

        for child in children:
            data[child.data[0]] = child.getCheckState()

        return data
