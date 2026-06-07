"""Quanty calculation details dialog."""

import os
from itertools import pairwise

from silx.gui.qt import (
    QDialog,
    QPoint,
    QSize,
    QTextBlockFormat,
    QTextCursor,
    QWidget,
)

from crispy import resourceAbsolutePath
from crispy.config import Config
from crispy.items import SelectableItem
from crispy.quanty.external import ExternalData
from crispy.uic import loadUi
from crispy.utils import fixedFont
from crispy.views import setMappings


def nodeLabel(item):
    """Build the single-line label of an item for the Hamiltonian tree."""
    name = item.data(0)
    text = "" if name is None else str(name)

    value = item.data(1)
    if value is not None and value != "":
        text = f"{text}: {value}"

    # Only Hamiltonian parameters carry a scale factor in column 2.
    scaleFactor = item.data(2)
    if scaleFactor is not None and scaleFactor != "":
        text = f"{text} (×{scaleFactor})"  # noqa: RUF001

    # Show whether a checkable term is included in the calculation.
    if isinstance(item, SelectableItem):
        mark = "x" if item.isEnabled() else " "
        text = f"[{mark}] {text}"

    return text


def hamiltonianAsText(hamiltonian):
    """Render the Hamiltonian item subtree as `tree`-style text."""

    def appendBranch(item, prefix, lines):
        children = item.children()
        for index, child in enumerate(children):
            isLast = index == len(children) - 1
            connector = "└── " if isLast else "├── "
            lines.append(f"{prefix}{connector}{nodeLabel(child)}")
            extension = "    " if isLast else "│   "
            appendBranch(child, prefix + extension, lines)

    lines = [nodeLabel(hamiltonian)]
    appendBranch(hamiltonian, "", lines)
    return "\n".join(lines)


class AxisWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        uiPath = os.path.join("quanty", "uis", "details", "axis.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.mappers = []

    def clear(self):
        if self.mappers:
            for mapper in self.mappers:
                mapper.clearMapping()

        self.shiftLineEdit.clear()
        self.gaussianLineEdit.clear()
        self.lorentzianLineEdit.clear()

    def populate(self, axis):
        self.clear()

        MAPPINGS = (
            (self.shiftLineEdit, axis.shift),
            (self.lorentzianLineEdit, axis.lorentzian),
            (self.gaussianLineEdit, axis.gaussian),
        )

        self.mappers = setMappings(MAPPINGS)


class DetailsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        uiPath = os.path.join("quanty", "uis", "details", "main.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        font = fixedFont()
        self.inputText.setFont(font)
        self.outputText.setFont(font)
        self.hamiltonianText.setFont(font)
        # self.summaryText.setFont(font)

        self.xAxis = AxisWidget()
        self.yAxis = AxisWidget()
        self.axesTabWidget.addTab(self.xAxis, None)

        self.mappers = []

        # This avoids closing the window after changing the value in a line
        # edit and then pressing return.
        self.closePushButton.setAutoDefault(False)
        self.closePushButton.clicked.connect(self.close)

    def clear(self):
        self.setWindowTitle("Details")

        if self.mappers:
            for mapper in self.mappers:
                mapper.clearMapping()

        self.scaleLineEdit.clear()
        self.normalizationComboBox.clear()

        self.xAxis.clear()
        self.yAxis.clear()

        self.inputText.clear()
        self.outputText.clear()
        # self.summaryText.clear()

        self.hamiltonianText.clear()

    def populate(self, result):
        self.clear()

        # The Hamiltonian tab is only meaningful for calculations.
        hamiltonianTabIndex = self.tabWidget.indexOf(self.hamiltonianTabWidget)

        if isinstance(result, ExternalData):
            self.tabWidget.setTabEnabled(hamiltonianTabIndex, False)
            self.spectraView.setModel(result.model())
            index = result.model().indexFromItem(result)
            self.spectraView.setRootIndex(index)
            return

        if result is None:
            self.tabWidget.setTabEnabled(hamiltonianTabIndex, False)
            return

        self.tabWidget.setTabEnabled(hamiltonianTabIndex, True)

        MAPPINGS = (
            (self.scaleLineEdit, result.axes.scale),
            (self.normalizationComboBox, result.axes.normalization),
        )
        self.mappers = setMappings(MAPPINGS)

        self.xAxis.populate(result.axes.xaxis)
        self.axesTabWidget.setTabText(0, result.axes.xaxis.label)

        if result.experiment.isTwoDimensional:
            self.axesTabWidget.addTab(self.yAxis, None)
            self.axesTabWidget.setTabText(1, result.axes.yaxis.label)
            self.yAxis.populate(result.axes.yaxis)
        else:
            self.axesTabWidget.removeTab(1)

        model = result.model()
        self.spectraView.setModel(model)
        index = model.indexFromItem(result.spectra.toPlot)
        self.spectraView.setRootIndex(index)

        # Display the whole Hamiltonian subtree (terms, sub-Hamiltonians, and
        # their parameters) as a `tree`-style text representation.
        self.hamiltonianText.setPlainText(hamiltonianAsText(result.hamiltonian))
        self.setLineSpacing(self.hamiltonianText, 130)

        self.inputText.setPlainText(result.input)
        self.outputText.setPlainText(result.output)
        # self.summaryText.setPlainText(result.summary)

        if result.value is not None:
            title = f"Details for {result.value}"
            self.setWindowTitle(title)

        self.updateTabOrder(twoDimensional=result.experiment.isTwoDimensional)

    def updateTabOrder(self, twoDimensional=False):
        """Chain the focusable widgets in visual order."""
        chain = [self.spectraView, self.scaleLineEdit, self.normalizationComboBox]
        axes = [self.xAxis, self.yAxis] if twoDimensional else [self.xAxis]
        for axis in axes:
            chain.append(axis.shiftLineEdit)
            chain.append(axis.lorentzianLineEdit)
            chain.append(axis.gaussianLineEdit)
        chain.append(self.closePushButton)

        # Link only widgets that can take focus, so a hidden or disabled field (such
        # as the disabled Lorentzian broadening) does not sit between two real fields
        # and break the chain on the native macOS style.
        chain = [w for w in chain if w.isEnabled() and not w.isHidden()]
        for earlier, later in pairwise(chain):
            self.setTabOrder(earlier, later)

    @staticmethod
    def setLineSpacing(widget, percent):
        """Set the line spacing of a text edit as a percentage of the line height."""
        cursor = widget.textCursor()
        cursor.select(QTextCursor.Document)
        blockFormat = QTextBlockFormat()
        blockFormat.setLineHeight(percent, QTextBlockFormat.ProportionalHeight.value)
        cursor.mergeBlockFormat(blockFormat)

    def showEvent(self, event):
        self.loadSettings()
        super().showEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)

    def loadSettings(self):
        settings = Config().read()
        settings.beginGroup("DetailsDialog")

        size = settings.value("Size")
        if size is not None:
            self.resize(QSize(size))

        pos = settings.value("Position")
        if pos is not None:
            self.move(QPoint(pos))

        settings.endGroup()

    def saveSettings(self):
        settings = Config().read()
        settings.beginGroup("DetailsDialog")
        settings.setValue("Size", self.size())
        settings.setValue("Position", self.pos())
        settings.endGroup()
        settings.sync()
