###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Custom delegates and views."""

import logging

from silx.gui.qt import QStyledItemDelegate, Qt, QTableView, QTreeView

from crispy.items import ComboItem, DoubleItem, IntItem, Vector3DItem
from crispy.widgets import ComboBox, DoubleLineEdit, IntLineEdit, Vector3DLineEdit

logger = logging.getLogger(__name__)


class Delegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent=parent)

    def createEditor(self, parent, option, index):
        # The method is used only when editing directly in the view, and not when
        # editing is done via a widget.
        EDITORS = {
            IntItem: IntLineEdit,
            DoubleItem: DoubleLineEdit,
            Vector3DItem: Vector3DLineEdit,
            ComboItem: ComboBox,
        }
        # Don't create the editor if data is None.
        if index.data(Qt.EditRole) is None:
            return None

        item = index.internalPointer()
        for itemClass, widget in EDITORS.items():
            if isinstance(item, itemClass):
                editor = widget(parent)
                editor.setAlignment(Qt.AlignRight)
                return editor
        return None

    def setModelData(self, editor, model, index):
        try:
            return editor.setModelData(model, index)
        except ValueError as e:
            logger.info(str(e))
            self.setEditorData(editor, index)

    def setEditorData(self, editor, index):
        editor.setEditorData(index)


class TreeView(QTreeView):
    """Class enabling additional functionality for a QTreeView."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setItemDelegateForColumn(1, Delegate(parent=self))
        self.setItemDelegateForColumn(2, Delegate(parent=self))

    def showEvent(self, event):
        self.resizeAllColumnsToContents()
        super().showEvent(event)

    def resizeAllColumnsToContents(self):
        if self.model() is None:
            return
        for i in range(self.model().columnCount()):
            self.resizeColumnToContents(i)


class TableView(QTableView):
    def __init__(self, parent):
        super().__init__(parent=parent)

    def showEvent(self, event):
        self.hideColumn(1)
        self.hideColumn(2)
        super().showEvent(event)
