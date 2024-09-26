###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Quanty calculation details dialog."""

import os

from silx.gui.qt import QDialog, QPoint, QSize, QWidget

from crispy import resourceAbsolutePath
from crispy.config import Config
from crispy.uic import loadUi
from crispy.utils import fixedFont, setMappings
from crispy.quanty.external import ExternalData

settings = Config().read()


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

    def populate(self, result):
        self.clear()

        if isinstance(result, ExternalData):
            self.spectraView.setModel(result.model())
            index = result.model().indexFromItem(result)
            self.spectraView.setRootIndex(index)
            return

        if result is None:
            return

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

        self.inputText.setPlainText(result.input)
        self.outputText.setPlainText(result.output)
        # self.summaryText.setPlainText(result.summary)

        if result.value is not None:
            title = f"Details for {result.value}"
            self.setWindowTitle(title)

    def showEvent(self, event):
        self.loadSettings()
        super().showEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)

    def loadSettings(self):
        settings.beginGroup("DetailsDialog")

        size = settings.value("Size")
        if size is not None:
            self.resize(QSize(size))

        pos = settings.value("Position")
        if pos is not None:
            self.move(QPoint(pos))

        settings.endGroup()

    def saveSettings(self):
        settings.beginGroup("DetailsDialog")
        settings.setValue("Size", self.size())
        settings.setValue("Position", self.pos())
        settings.endGroup()

        settings.sync()
