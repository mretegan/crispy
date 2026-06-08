"""This module is the entry point to the application."""

import json
import logging
import os
import sys
import warnings
from urllib.error import URLError
from urllib.request import Request, urlopen

import numpy as np
from packaging.version import InvalidVersion, parse
from silx.gui.qt import (
    QAction,
    QApplication,
    QByteArray,
    QDialog,
    QFileDialog,
    QIcon,
    QLocale,
    QMainWindow,
    QPixmap,
    QPlainTextEdit,
    QPoint,
    QProcess,
    QSize,
    Qt,
    QThread,
    pyqtSignal,
)

from crispy import resourceAbsolutePath, version
from crispy.config import Config
from crispy.loggers import StatusBarHandler, setUpLoggers
from crispy.plot import MainPlotWidget  # noqa: F401
from crispy.quanty.main import DockWidget
from crispy.uic import loadUi
from crispy.utils import fixedFont

logger = logging.getLogger("crispy.main")
warnings.filterwarnings("ignore", category=UserWarning)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        uiPath = os.path.join("uis", "main.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.setWindowTitle("Crispy")

        # Set the icon.
        iconPath = os.path.join("icons", "crispy.svg")
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

        menu = self.menuBar().addMenu("Tools")
        self.loadExternalDataAction = QAction(
            "Load External Data", self, triggered=self.loadExternalData
        )
        menu.addAction(self.loadExternalDataAction)

        self.runJupyterLabAction = QAction(
            "Start Jupyter Lab", self, triggered=self.runJupyterLab
        )
        menu.addAction(self.runJupyterLabAction)

        menu = self.menuBar().addMenu("Help")
        self.openAboutDialogAction = QAction(
            "About Crispy", self, triggered=self.openAboutDialog
        )
        menu.addAction(self.openAboutDialogAction)

        # Register a handler to display messages in the status bar.
        logger = logging.getLogger("crispy")
        handler = StatusBarHandler()
        logger.addHandler(handler)
        # If I don't set the level here, the handler will also display debug
        # messages, even though the level is set to INFO in the __init__ method.
        handler.setLevel(logging.INFO)
        handler.bridge.logUpdated.connect(self.updateStatusBar)

    def updateStatusBar(self, message):
        self.statusBar().showMessage(message, 3000)

    def showEvent(self, event):
        self.loadSettings()
        super().showEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)

    def loadSettings(self):
        settings = Config().read()
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
        sizes = [int(size) for size in splitter] if splitter is not None else [6, 1]
        self.splitter.setSizes(sizes)
        settings.endGroup()

    def saveSettings(self):
        settings = Config().read()
        settings.beginGroup("MainWindow")
        settings.setValue("State", self.saveState())
        settings.setValue("Size", self.size())
        settings.setValue("Position", self.pos())
        settings.setValue("Splitter", self.splitter.sizes())
        settings.endGroup()
        settings.sync()

    def openAboutDialog(self):
        self.aboutDialog.exec()

    def loadExternalData(self):
        dialog = QFileDialog()
        path, _ = dialog.getOpenFileName(self, "Select File")

        if path:
            try:
                raw = np.loadtxt(path)
            except ValueError:
                logger.error(f"Failed to load data from {path}")
                return

            name = os.path.splitext(os.path.basename(path))[0]
            self.quantyDockWidget.addExternalData(raw, name)

    def runJupyterLab(self):
        process = QProcess()
        process.setProgram("jupyter-lab")
        process.setArguments([f"--notebook-dir={os.path.expanduser('~')}"])
        process.startDetached()


class CheckUpdateThread(QThread):
    updateAvailable = pyqtSignal()

    @staticmethod
    def _getLatestVersion():
        URL = "https://pypi.org/pypi/crispy/json"

        request = Request(URL)
        request.add_header("Cache-Control", "max-age=0")
        request.add_header("User-Agent", f"crispy/{version}")

        try:
            response = urlopen(request, timeout=5)
        except (TimeoutError, URLError):
            return None

        try:
            data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return None

        return data.get("info", {}).get("version")

    def run(self):
        # Wait a few seconds to avoid too much work at startup.
        self.sleep(1)

        latestVersion = self._getLatestVersion()
        if latestVersion is None:
            logger.info("Could not check for updates.")
            return

        try:
            outdated = parse(version) < parse(latestVersion)
        except InvalidVersion:
            logger.info("Could not check for updates.")
            return

        if outdated:
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

        self._updateThread = None

        uiPath = os.path.join("uis", "about.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.nameLabel.setText(f"Crispy {version}")

        settings = Config().read()

        self.updateCheckBox.stateChanged.connect(self.updateCheckBoxStateChanged)
        self.updateCheckBox.setChecked(settings.value("CheckForUpdates", type=bool))

        iconPath = resourceAbsolutePath(os.path.join("icons", "crispy.svg"))
        self.iconLabel.setPixmap(QPixmap(iconPath))

        if settings.value("CheckForUpdates", type=bool):
            self.runUpdateCheck()

    def updateCheckBoxStateChanged(self):
        updateCheck = self.updateCheckBox.isChecked()
        settings = Config().read()
        settings.setValue("CheckForUpdates", updateCheck)
        settings.sync()
        if updateCheck:
            self.runUpdateCheck()

    def runUpdateCheck(self):
        # Avoid starting a second check while one is already running.
        if self._updateThread is not None and self._updateThread.isRunning():
            return

        thread = CheckUpdateThread(self)
        thread.updateAvailable.connect(self.informAboutAvailableUpdate)
        self._updateThread = thread
        thread.start()

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
    config.prune()

    setUpLoggers()

    logger.info("Starting the application.")
    window = MainWindow()
    window.show()
    logger.info("Ready.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
