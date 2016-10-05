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
            return None

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

        n = parentNode.childCount()
        return n

    def columnCount(self, parentIndex):
        """Return the number of columns. The index of the parent is
        required, but not used, as in this implementation it defaults
        for all nodes to the length of the header.
        """
        n = len(self._header)
        return n

    def data(self, index, role):
        """Return role specific data for the item referred by
        index.column()."""
        if not index.isValid():
            pass

        node = self.getNode(index)

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return node.getItemData(index.column())

        if role == Qt.TextAlignmentRole:
            if index.column() > 0:
                return Qt.AlignRight

    def setData(self, index, value, role):
        """Set the role data for the item at index to value."""
        if index.isValid():
            node = self.getNode(index)
            if role == Qt.DisplayRole or role == Qt.EditRole:
                node.setItemData(index.column(), value)
                self.getModelData()
            elif role == Qt.CheckStateRole:
                if node.checkState() == Qt.Checked:
                    node.setState(Qt.Unchecked)
                else:
                    node.setState(Qt.Checked)
            return True
        else:
            return False

    def flags(self, index):
        """Return the active flags for the given index."""
        activeFlags = (
            Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
        return activeFlags

    def headerData(self, section, orientation, role):
        """Return the data for the given role and section in the header
        with the specified orientation.
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._header[section]

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        else:
            return self._rootNode

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
                    node = TreeNode(
                        [key, '{0:8.4f}'.format(value)], parentNode)
                elif isinstance(value, list):
                    node = TreeNode(
                        [key, '{0:8.4f}'.format(value[0]),
                            '{0:8.2f}'.format(value[1])], parentNode)
                else:
                    print('Invalid data sent to the model: {0}'.format(value))

    def _getModelData(self, data, parentNode=None):
        """Return the data contained in the model."""
        if parentNode is None:
            parentNode = self._rootNode

        for node in parentNode.getChildren():
            key = node.getItemData(0)
            if node.childCount() != 0:
                data[key] = collections.OrderedDict()
                self._getModelData(data[key], node)
            else:
                if node.getItemData(2):
                    data[key] = [
                        float(node.getItemData(1)),
                        float(node.getItemData(2)),
                        ]
                else:
                    data[key] = float(node.getItemData(1))

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
