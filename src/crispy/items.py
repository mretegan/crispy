###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Items for custom models."""

import copy
import logging
import weakref

import numpy as np
from silx.gui.qt import (
    QAbstractItemModel,
    QLocale,
    QModelIndex,
    QObject,
    Qt,
    pyqtSignal,
)

logger = logging.getLogger(__name__)


class BaseItem(QObject):
    """Base class for the items of the tree model."""

    dataChanged = pyqtSignal(int)

    def __init__(self, parent=None, name=None, value=None):
        super().__init__(parent=parent)
        self._name = name
        self._value = value

        self._model = None
        self._parent = None
        self._children = []
        self._visible = False

        if isinstance(parent, (QAbstractItemModel, RootItem)):
            self._ancestor = None
        else:
            if parent is not None and parent._ancestor is not None:
                self._ancestor = parent._ancestor
            else:
                self._ancestor = None

        self.setParent(parent)
        # This might be overkill, but it is better to be on the safe side.
        try:
            self.dataChanged.disconnect()
        except (TypeError, RuntimeError):
            pass
        self.dataChanged.connect(self._modelDataChanged)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.dataChanged.emit(0)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.dataChanged.emit(1)

    @property
    def ancestor(self):
        return self._ancestor

    def _modelDataChanged(self, column):
        model = self.model()
        if model is None:
            raise TypeError("The model needs to be defined.")
        index = self.model().createIndex(self.childPosition(), column, self)
        self.model().dataChanged.emit(index, index)

    def parent(self):
        return self._parent() if self._parent is not None else None

    def setParent(self, parent):
        # If the parent is the same, return.
        if self.parent() is parent:
            # logger.debug("No need to set the parent again.")
            return

        # If the parent is None, remove the item from the current parent.
        if parent is None:
            if self.parent() is None:
                return
            # Remove it from the parent's children.
            self.parent().removeRow(self)
            self._parent = None
        else:
            # Remove the item from the current parent.
            if self.parent() is not None:
                self.parent().removeRow(self)

            # Assign the new parent to the item.
            self._parent = weakref.ref(parent)

            parent = self.parent()
            model = None
            if isinstance(parent, QAbstractItemModel):
                model = parent
            elif isinstance(parent, BaseItem):
                model = parent.model()

            self._updateModel(model)

            # Insert to the parent's children.
            if isinstance(parent, BaseItem):
                parent.appendRow(self)
        super().setParent(parent)

    def insertRow(self, index, row):
        """Insert a row to the children list at the position specified by the index."""
        model = self.model()

        if model is not None:
            model.beginInsertRows(self.index(), index, index)
        self.children().insert(index, row)
        if model is not None:
            model.endInsertRows()

    def appendRow(self, item):
        self.insertRow(self.rowCount(), item)

    def removeRow(self, row):
        """Remove a row from the children list."""
        model = self.model()
        index = self.children().index(row)

        if model is not None:
            # The parent index corresponds to the parent from which the new
            # rows are removed. Because the rows are removed from the current
            # item, the parent index is self.index().
            model.beginRemoveRows(self.index(), index, index)
        self.children().pop(index)
        if model is not None:
            model.endRemoveRows()

    def model(self):
        model = self._model() if self._model is not None else None
        return model

    def _updateModel(self, model):
        if model != self.model():
            # logger.debug(
            #     "Updating the model for %s from %s to %s.", self, self.model(), model
            # )
            self._model = None if model is None else weakref.ref(model)
            for child in self.children():
                child._updateModel(model)

    def index(self, column=0):
        """Return corresponding index in the model or None if not in a model."""
        parent = self.parent()
        model = self.model()

        if model is None:  # Not in a model
            return None

        if parent is model:  # Root node
            return QModelIndex()

        index = parent.index()
        row = parent.children().index(self)
        return model.index(row, column, index)

    def child(self, index):
        """Return the child at the specified index.

        FIXME: In some cases, when the method was called from the index()
        method of the TreeModel class it raises an IndexError. This is
        happening without apparent reason and it was not easily reproducible.
        So instead of crashing the application we catch the error and log it.
        """
        try:
            return self.children()[index]
        except IndexError as e:
            logger.debug((str(e), self, self.children(), index))

    def children(self):
        return self._children

    def siblings(self):
        """Return the siblings of the item or None if the item has no parent."""
        return self.parent().children() if self.parent() else None

    def childPosition(self):
        """Return the position of a child."""
        parent = self.parent()
        if not isinstance(parent, QAbstractItemModel):
            return parent.children().index(self)
        return 0

    def lastChild(self):
        try:
            return self.children()[-1]
        except IndexError:
            return None

    def findChild(self, name):
        # Yield from an empty list if there are no children.
        if not self.children():
            yield from ()

        for child in self.children():
            if child.name == name:
                yield child
            else:
                if isinstance(child, BaseItem):
                    yield from child.findChild(name)

    def columnCount(self):
        return 2

    def rowCount(self):
        return len(self.children())

    def data(self, column, role=Qt.DisplayRole):
        if role in (Qt.EditRole, Qt.DisplayRole, Qt.UserRole):
            if column == 0:
                return self.name
            if column == 1:
                return self.value
        return None

    def setData(self, column, value, role=Qt.EditRole):
        if role in (Qt.EditRole, Qt.UserRole):
            if column == 0:
                self.name = value
            if column == 1:
                self.value = value
            return True
        return False

    def flags(self, column):
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if column > 0:
            return flags | Qt.ItemIsEditable
        return flags

    def copyFrom(self, item):
        # NOTE: If the values are assigned using the setter, the time it takes
        # to call the function doubles approximately at each call. This is
        # related to the _modelDataChanged() function.
        self._name = copy.deepcopy(item.name)
        self._value = copy.deepcopy(item.value)


class SelectableItem(BaseItem):
    def __init__(self, parent=None, name=None, value=None):
        super().__init__(parent=parent, name=name, value=value)
        self.disable()

    def data(self, column, role=Qt.DisplayRole):
        if role == Qt.CheckStateRole:
            return self.checkState
        return super().data(column, role)

    def setData(self, column, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole:
            self.checkState = value
            return True
        return super().setData(column, value, role=role)

    @property
    def checkState(self):
        return self._checkState

    @checkState.setter
    def checkState(self, value):
        self._checkState = Qt.CheckState(value)
        self.dataChanged.emit(0)

    def enable(self):
        self.checkState = Qt.CheckState.Checked

    def disable(self):
        self.checkState = Qt.CheckState.Unchecked

    def isEnabled(self):
        return self.checkState == Qt.CheckState.Checked

    def flags(self, column):
        flags = super().flags(column)
        if column == 0:
            return flags | Qt.ItemIsUserCheckable
        return flags

    def copyFrom(self, item):
        super().copyFrom(item)
        self._checkState = copy.deepcopy(item.checkState)


class RootItem(BaseItem):
    def __init__(self, parent=None):
        super().__init__(parent=parent, name="Root")


class IntItem(BaseItem):
    def data(self, column, role=Qt.DisplayRole):
        if role in (Qt.EditRole, Qt.DisplayRole):
            if column == 1:
                try:
                    return QLocale().toString(self.value)
                except TypeError:
                    return self.value
        elif role in (Qt.UserRole,):
            if column == 1:
                return self.value
        return super().data(column, role)

    def setData(self, column, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            if column == 1:
                value, ok = QLocale().toInt(value)
                if ok:
                    self.value = value
            return True
        return super().setData(column, value, role)


class DoubleItem(BaseItem):
    def data(self, column, role=Qt.DisplayRole):
        if role in (Qt.EditRole, Qt.DisplayRole):
            if column == 1:
                try:
                    return QLocale().toString(self._value)
                except TypeError:
                    return self._value
        return super().data(column, role)

    def setData(self, column, value, role=Qt.EditRole):
        if column == 1:
            if role == Qt.EditRole:
                value, ok = QLocale().toDouble(value)
                if ok:
                    self.value = value
            return True
        return super().setData(column, value, role)


class Vector3DItem(BaseItem):
    def data(self, column, role=Qt.DisplayRole):
        # Qt.EditRole is needed to properly show the Numpy array in the
        # VectorLineEdit. Because of this the delegates must rely on the Qt.UserRole
        # to identify the type editor needed for the data.
        if role in (Qt.DisplayRole, Qt.EditRole):
            # Qt doesn't know how to represent a Numpy array, so we create a digestible
            # representation for it.
            if column == 1:
                return f"({self.value[0]}, {self.value[1]}, {self.value[2]})"
        return super().data(column, role)

    def setData(self, column, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            if column == 1:
                # Convert the value to a Numpy array.
                self.value = np.fromstring(value[1:-1], dtype=int, sep=",")
            return True
        return super().setData(column, value, role)


class BoolItem(BaseItem):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def data(self, column, role=Qt.DisplayRole):
        # Disable editing for this type of item.
        if role in (Qt.EditRole,):
            if column == 1:
                return None
        elif role in (Qt.DisplayRole, Qt.UserRole):
            if column == 1:
                return self.value
        return super().data(column, role)

    def setData(self, column, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            if column == 1:
                self.value = value
            return True
        return super().setData(column, value, role)


class ComboItem(BaseItem):
    def __init__(self, parent=None, name=None, value=None):
        super().__init__(parent=parent, name=name, value=value)
        self._items = None

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, values):
        self._items = values

    @property
    def currentItem(self):
        return self.value

    def copyFrom(self, item):
        super().copyFrom(item)
        self._items = copy.deepcopy(item.items)
