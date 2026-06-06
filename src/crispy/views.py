"""Custom delegates and views."""

import logging

from silx.gui.qt import (
    QCheckBox,
    QComboBox,
    QDataWidgetMapper,
    QStyledItemDelegate,
    Qt,
    QTableView,
    QTreeView,
)

from crispy.items import ComboItem, DoubleItem, IntItem, Vector3DItem
from crispy.utils import disconnectSignal
from crispy.widgets import ComboBox, DoubleLineEdit, IntLineEdit, Vector3DLineEdit

logger = logging.getLogger(__name__)


def setMappings(mappings):
    """Set the mappings between the model and widgets.
    TODO:
        - Should this be extended to accept other columns?
        - Check if it has a model already.
    """
    column = 1
    mappers = []
    for widget, obj in mappings:
        mapper = QDataWidgetMapper(widget)
        # logger.debug(obj.model())
        mapper.setModel(obj.model())
        mapper.addMapping(widget, column)
        delegate = Delegate(widget)
        mapper.setItemDelegate(delegate)
        mapper.setRootIndex(obj.parent().index())
        mapper.setCurrentModelIndex(obj.index())
        # QDataWidgetMapper needs a focus event to notice a change in the data.
        # To make sure the model is informed about the change, I connected the
        # stateChanged signal of the QCheckBox to the submit slot of the
        # QDataWidgetMapper. The same idea goes for the QComboBox.
        # https://bugreports.qt.io/browse/QTBUG-1818
        if isinstance(widget, QCheckBox):
            signal = widget.stateChanged
            disconnectSignal(signal)
            signal.connect(mapper.submit)
        elif isinstance(widget, QComboBox):
            signal = widget.currentTextChanged
            disconnectSignal(signal)
            signal.connect(mapper.submit)
        mappers.append(mapper)
    return mappers


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
