# coding: utf-8

import collections

from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex


class TreeNode(object):
    """Class implementing a tree node to be used in a tree model."""

    def __init__(self, data, parent=None):
        self._data = data
        self._parent = parent
        self._children = []
        self._state = Qt.Checked

        if parent is not None:
            parent.appendChild(self)

    def appendChild(self, node):
        """Append a child to the parent node."""
        self._children.append(node)

    def getChildren(self):
        return self._children

    def child(self, row):
        """Return the child at a given row (index)."""
        return self._children[row]

    def row(self):
        """Return the row (index) of the child."""
        if self._parent is not None:
            return self._parent._children.index(self)
        else:
            return 0

    def childCount(self):
        return len(self._children)

    def columnCount(self):
        return len(self._data)

    def getItemData(self, column):
        """Return the data for a given column."""
        try:
            return self._data[column]
        except IndexError:
            return str()

    def setItemData(self, column, value):
        """Set the data at a given column."""
        try:
            self._data[column] = value
        except IndexError:
            pass

    def getData(self):
        return self._data

    def parent(self):
        return self._parent

    def checkState(self):
        return self._state

    def setState(self, state):
        self._state = state


class TreeModel(QAbstractItemModel):
    """Class implementing a basic tree model. It subclasses
    QAbstractItemModel and thus implements: index(), parent(),
    rowCount(), columnCount(), and data().

    To enable editing, the class implements setData() and reimplements
    flags() to ensure that an editable item is returned. headerData() is
    also reimplemented to control the way the header is presented.
    """

    def __init__(self, header, data, parent=None):
        super(TreeModel, self).__init__(parent)
        self._header = header
        self._data = data
        self.setModelData(self._data)

    def index(self, row, column, parentIndex=None):
        """Return the index of the item in the model specified by the
        given row, column and parent index.
        """
        if parentIndex is None or not parentIndex.isValid():
            parentNode = self._rootNode
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
        parentNode = childNode.parent()

        if parentNode == self._rootNode:
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
            parentNode = self._rootNode
        else:
            parentNode = self.getNode(parentIndex)

        return parentNode.childCount()

    def columnCount(self, parentIndex):
        """Return the number of columns. The index of the parent is
        required, but not used, as in this implementation it defaults
        for all nodes to the length of the header.
        """
        return len(self._header)

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
                if column > 1:
                    return '{0:8.1f}'.format(value)
                else:
                    return '{0:8.3f}'.format(value)
            except ValueError:
                return value

        if role == Qt.EditRole:
            return str(value)

        if role == Qt.TextAlignmentRole:
            if index.column() > 0:
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

            # This is needed do display data from multiple items.
            self.getModelData()

        return True

    def flags(self, index):
        """Return the active flags for the given index. Add editable
        flag to items in the first colum or greater.
        """
        activeFlags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

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
            return self._header[section]

    def getNode(self, index):
        if not index.isValid():
            return self._rootNode

        return index.internalPointer()

    def setModelData(self, data, parentNode=None):
        if parentNode is None:
            self._data = data
            self._rootNode = TreeNode(self._header)
            parentNode = self._rootNode

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
                else:
                    print('Invalid data sent to the model: {0}'.format(value))

    def _getModelData(self, data, parentNode=None):
        """Return the data contained in the model."""
        if parentNode is None:
            parentNode = self._rootNode

        for node in parentNode.getChildren():
            key = node.getItemData(0)
            if node.childCount():
                data[key] = collections.OrderedDict()
                self._getModelData(data[key], node)
            else:
                if node.getItemData(2):
                    data[key] = [node.getItemData(1), node.getItemData(2)]
                else:
                    data[key] = node.getItemData(1)

    def getModelData(self):
        data = collections.OrderedDict()
        self._getModelData(data)
        self._data = data
        return self._data

    def getNodesState(self, parentNode=None):
        """Return the state (disabled, tristate, enable) of all nodes
        belonging to a parent.
        """
        if parentNode is None:
            parentNode = self._rootNode

        data = dict()
        for node in parentNode.getChildren():
            data[node._data[0]] = node.checkState()

        return data
