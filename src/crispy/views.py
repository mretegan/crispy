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
from crispy.widgets import (
    ComboBox,
    DoubleLineEdit,
    IntLineEdit,
    Vector3DLineEdit,
)

logger = logging.getLogger(__name__)


def setMappings(mappings, *, column=1):
    """Connect widgets to fields of items in a tree model.

    Each pair gets a mapper that reads the selected item column into the widget
    and submits widget edits to that column. Checkbox and combo-box changes
    submit immediately. Other signal connections on the widgets remain active.
    Log the widget name, item name, and column at DEBUG level.

    Args:
        mappings: Iterable of (widget, item) pairs. Items must belong to a model.
            Widgets must implement setEditorData(index) and
            setModelData(model, index).
        column: Zero-based item column shared by all pairs. The default is 1
            (value). Column 0 contains names. Hamiltonian parameters use column 2
            for scale factors.

    Returns:
        A list of QDataWidgetMapper objects, one per pair in input order.
        Pass this list to clearMappings before mapping the widgets again.

    Raises:
        ValueError: An item has no model or the column is outside its column range.
    """
    mappers = []
    for widget, obj in mappings:
        model = obj.model()
        if model is None:
            raise ValueError("Cannot map an item without a model.")
        if not 0 <= column < obj.columnCount():
            raise ValueError(
                f"Cannot map column {column}: the item has {obj.columnCount()} columns."
            )
        mapper = QDataWidgetMapper(widget)
        mapper.setModel(model)
        mapper.addMapping(widget, column)
        delegate = Delegate(mapper)
        mapper.setItemDelegate(delegate)
        mapper.setRootIndex(obj.parent().index())
        mapper.setCurrentModelIndex(obj.index())
        # Submit checkbox and combo-box changes without waiting for focus events.
        # https://bugreports.qt.io/browse/QTBUG-1818
        if isinstance(widget, QCheckBox):
            widget.stateChanged.connect(mapper.submit)
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(mapper.submit)
        mappers.append(mapper)
        logger.debug(
            "Mapped widget %r to item %r in column %d.",
            widget.objectName(),
            obj.name,
            column,
        )
    return mappers


def clearMappings(mappers):
    """Clear mappings and schedule deletion of the mappers and their delegates.

    Args:
        mappers: The list returned by setMappings. This function empties the list.
    """
    for mapper in mappers:
        widget = mapper.parent()
        mapper.clearMapping()
        if isinstance(widget, QCheckBox):
            widget.stateChanged.disconnect(mapper.submit)
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.disconnect(mapper.submit)
        mapper.deleteLater()
    mappers.clear()


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
