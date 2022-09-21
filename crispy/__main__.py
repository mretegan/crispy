# coding: utf-8
###################################################################
# Copyright (c) 2016-2022 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This module is the entry point to the application."""

import json
import logging
import os
import socket
import sys
import warnings
from urllib.error import URLError
from urllib.request import Request, urlopen

from PyQt5.QtCore import QByteArray, QLocale, QPoint, QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QDialog, QMainWindow, QPlainTextEdit
from PyQt5.uic import loadUi

from crispy import resourceAbsolutePath, version
from crispy.config import Config
from crispy.loggers import OutputHandler, StatusBarHandler, setUpLoggers

# pylint: disable=unused-import
from crispy.plot import MainPlotWidget
from crispy.quanty.main import DockWidget
from crispy.utils import fixedFont

logger = logging.getLogger("crispy.main")
warnings.filterwarnings("ignore", category=UserWarning)

settings = Config().read()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        uiPath = os.path.join("uis", "main.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.setWindowTitle("Crispy")

        # Set the icon.
        iconPath = os.path.join("crispy.png")
        self.setWindowIcon(QIcon(resourceAbsolutePath(iconPath)))

        # Setup the logger widget.
        self.loggerWidget.setFont(fixedFont())
        self.loggerWidget.setLineWrapMode(QPlainTextEdit.NoWrap)

        # Setup the about dialog.
        self.aboutDialog = AboutDialog(parent=self)

        # Instantiate the Quanty dock widget.
        self.quantyDockWidget = DockWidget(parent=self)
        self.quantyDockWidget.setVisible(True)
        self.addDockWidget(Qt.RightDockWidgetArea, self.quantyDockWidget)

        # Compose the menu.
        menu = self.menuBar().addMenu("Quanty")
        menu.addAction(self.quantyDockWidget.preferencesAction)
        menu.addSeparator()
        menu.addAction(self.quantyDockWidget.saveInputAction)
        menu.addAction(self.quantyDockWidget.saveInputAsAction)
        menu.addSeparator()
        menu.addAction(self.quantyDockWidget.showHideAction)

        menu = self.menuBar().addMenu("Help")
        self.openAboutDialogAction = QAction(
            "About Crispy", self, triggered=self.openAboutDialog
        )
        menu.addAction(self.openAboutDialogAction)

        # Register a handler to display messages in the status bar.
        l = logging.getLogger("crispy")
        handler = StatusBarHandler()
        l.addHandler(handler)
        handler.logUpdated.connect(self.updateStatusBar)

        handler = OutputHandler()
        l.addHandler(handler)

    def updateStatusBar(self, message):
        self.statusBar().showMessage(message, 3000)

    def showEvent(self, event):
        self.loadSettings()
        super().showEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)

    def loadSettings(self):
        settings.beginGroup("MainWindow")

        state = settings.value("State")
        if state is not None:
            self.restoreState(QByteArray(state))

        size = settings.value("Size")
        if size is not None:
            self.resize(QSize(size))

        pos = settings.value("Position")
        if pos is not None:
            self.move(QPoint(pos))

        splitter = settings.value("Splitter")
        if splitter is not None:
            sizes = [int(size) for size in splitter]
        else:
            sizes = [6, 1]
        self.splitter.setSizes(sizes)
        settings.endGroup()

    def saveSettings(self):
        settings.beginGroup("MainWindow")
        settings.setValue("State", self.saveState())
        settings.setValue("Size", self.size())
        settings.setValue("Position", self.pos())
        settings.setValue("Splitter", self.splitter.sizes())
        settings.endGroup()

        settings.sync()

    def openAboutDialog(self):
        self.aboutDialog.exec_()


class CheckUpdateThread(QThread):

    updateAvailable = pyqtSignal()

    @staticmethod
    def _getSiteVersion():
        URL = "http://www.esrf.eu/computing/scientific/crispy/version.json"

        request = Request(URL)
        request.add_header("Cache-Control", "max-age=0")

        try:
            response = urlopen(request, timeout=5)
        except (URLError, socket.timeout):
            return None

        try:
            data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return None

        return data["version"]

    def run(self):
        # TODO: The implementation is not ideal. The run() method of the parent
        # class is not called.
        # Wait a few seconds to avoid too much work at startup.
        seconds = 1
        self.sleep(seconds)
        siteVersion = self._getSiteVersion()

        if siteVersion is not None and version < siteVersion:
            self.updateAvailable.emit()
        else:
            logger.info("There are no updates.")


class UpdateAvailableDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        uiPath = os.path.join("uis", "update.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)


class AboutDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        uiPath = os.path.join("uis", "about.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.nameLabel.setText(f"Crispy {version}")

        self.updateCheckBox.stateChanged.connect(self.updateCheckBoxStateChanged)
        self.updateCheckBox.setChecked(settings.value("CheckForUpdates", type=bool))

        if settings.value("CheckForUpdates", type=bool):
            self.runUpdateCheck()

    def updateCheckBoxStateChanged(self):
        updateCheck = self.updateCheckBox.isChecked()
        settings.setValue("CheckForUpdates", updateCheck)
        if updateCheck:
            self.runUpdateCheck()

    def runUpdateCheck(self):
        thread = CheckUpdateThread(self)
        thread.start()
        thread.updateAvailable.connect(self.informAboutAvailableUpdate)

    def informAboutAvailableUpdate(self):
        updateAvailableDialog = UpdateAvailableDialog(self.parent())
        updateAvailableDialog.show()


def main():
    app = QApplication([])

    # This must be done after the application is instantiated.
    locale = QLocale(QLocale.C)
    locale.setNumberOptions(QLocale.OmitGroupSeparator)
    QLocale.setDefault(locale)

    config = Config()
    config.removeOldFiles()

    setUpLoggers()

    logger.info("Starting the application.")
    window = MainWindow()
    window.show()
    logger.info("Ready.")

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
