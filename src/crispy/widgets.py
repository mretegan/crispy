###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Custom widgets."""

import logging

from silx.gui.qt import (
    QCheckBox,
    QColor,
    QComboBox,
    QDoubleValidator,
    QEvent,
    QIntValidator,
    QLineEdit,
    QPalette,
    QRegularExpression,
    QRegularExpressionValidator,
    Qt,
)

logger = logging.getLogger(__name__)


class ComboBox(QComboBox):
    def setItems(self, items, currentItem):
        logger.debug("Number of items in combo box: %s", self.count())
        self.blockSignals(True)
        # FIXME: The crash happens here.
        # for _ in range(self.count()):
        #     self.removeItem(0)
        #     logger.debug("Remaining items: %s", self.count())
        self.clear()
        logger.debug("Adding items to combo box: %s", items)
        self.addItems(items)
        logger.debug("Setting current item: %s", currentItem)
        self.setCurrentText(currentItem)
        self.blockSignals(False)

    def setModelData(self, model, index):
        value = self.currentText()
        if value == model.data(index, role=Qt.EditRole):
            return
        model.setData(index, value, Qt.EditRole)

    def setEditorData(self, index):
        item = index.internalPointer()
        self.setItems(item.items, item.currentItem)


# Initially the line edits were implemented to return the types specified in
# their names, i.e. the IntLineEdit would return an int, etc. In the end I found it
# better to delegate the conversion to the items in the model. The validators take care
# of having the proper format.


class LineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = None
        self.currentText = None

        palette = self.palette()
        self.defaulBakgroundColor = palette.color(QPalette.ColorRole.Base)
        self.alternateBackgroundColor = palette.color(QPalette.ColorRole.AlternateBase)

        self.textEdited.connect(self.updateBackgroundColor)
        self.installEventFilter(self)

    def focusInEvent(self, event):
        self.currentText = self.text()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setBackgroundColor(self.defaulBakgroundColor)
        if not self.text():
            self.setText(self.currentText)
        super().focusOutEvent(event)

    def setBackgroundColor(self, color):
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor(color))
        self.setPalette(palette)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.setBackgroundColor(self.defaulBakgroundColor)
        return super().eventFilter(source, event)

    def updateBackgroundColor(self):
        self.setBackgroundColor(self.alternateBackgroundColor)

    def setModelData(self, model, index):
        value = self.text()
        # Don't update the model's data if it did not change.
        if value == model.data(index, role=Qt.EditRole):
            return
        model.setData(index, value, Qt.EditRole)
        self.currentText = value

    def setEditorData(self, index):
        value = index.data()
        self.setText(value)


class IntLineEdit(LineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = QIntValidator()
        self.setValidator(self.validator)


class DoubleLineEdit(LineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = QDoubleValidator()
        self.setValidator(self.validator)


class Vector3DLineEdit(LineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex = QRegularExpression()
        # Regex that matches the vectors input format, e.g. (1, 0, 1), (-1,0,1)
        # + and - are allowed and any number of spaces after comma. The regex has
        # groups that can be captured.
        self.regex.setPattern("\\(([+-]?\d?),\s*([+-]?\d?),\s*([+-]?\d?)\\)")
        self.validator = QRegularExpressionValidator(self.regex, self)
        self.setValidator(self.validator)


class CheckBox(QCheckBox):
    def setModelData(self, model, index):
        value = self.isChecked()
        if value == model.data(index, role=Qt.UserRole):
            return
        model.setData(index, value, Qt.EditRole)

    def setEditorData(self, index):
        value = index.data(Qt.UserRole)
        self.setChecked(value)
