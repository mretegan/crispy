###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Quanty preferences dialog."""

import logging
import os

from silx.gui.qt import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QPoint,
    QSize,
    pyqtSignal,
)

from crispy import resourceAbsolutePath
from crispy.config import Config
from crispy.uic import loadUi

logger = logging.getLogger(__name__)
settings = Config().read()


class PreferencesDialog(QDialog):
    settingsChanged = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        uiPath = os.path.join("quanty", "uis", "preferences.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.pathBrowsePushButton.clicked.connect(self.setExecutablePath)

        ok = self.buttonBox.button(QDialogButtonBox.Ok)
        ok.clicked.connect(self.acceptSettings)

        cancel = self.buttonBox.button(QDialogButtonBox.Cancel)
        cancel.clicked.connect(self.rejectSettings)

    def showEvent(self, event):
        self.loadSettings()
        super().showEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        self.settingsChanged.emit()
        super().closeEvent(event)

    def loadSettings(self):
        settings.beginGroup("Quanty")

        size = settings.value("Size")
        if size is not None:
            self.resize(QSize(size))

        pos = settings.value("Position")
        if pos is not None:
            self.move(QPoint(pos))

        path = settings.value("Path")
        self.pathLineEdit.setText(path)
        self.pathLineEdit.setCursorPosition(0)

        verbosity = settings.value("Verbosity")
        self.verbosityLineEdit.setText(verbosity)

        denseBorder = settings.value("DenseBorder")
        self.denseBorderLineEdit.setText(denseBorder)

        shiftSpectra = settings.value("ShiftSpectra", type=bool)
        self.shiftSpectraCheckBox.setChecked(shiftSpectra)

        removeFiles = settings.value("RemoveFiles", type=bool)
        self.removeFilesCheckBox.setChecked(removeFiles)

        settings.endGroup()

    def saveSettings(self):
        settings.beginGroup("Quanty")
        settings.setValue("Path", self.pathLineEdit.text())
        settings.setValue("Verbosity", self.verbosityLineEdit.text())
        settings.setValue("DenseBorder", self.denseBorderLineEdit.text())
        settings.setValue("ShiftSpectra", self.shiftSpectraCheckBox.isChecked())
        settings.setValue("RemoveFiles", self.removeFilesCheckBox.isChecked())
        settings.setValue("Size", self.size())
        settings.setValue("Position", self.pos())
        settings.endGroup()
        settings.sync()

    def acceptSettings(self):
        self.saveSettings()
        self.close()

    def rejectSettings(self):
        self.loadSettings()
        self.close()

    def setExecutablePath(self):
        home = os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(self, "Select File", home)

        if path:
            self.pathLineEdit.setText(path)
            self.pathLineEdit.setCursorPosition(0)
