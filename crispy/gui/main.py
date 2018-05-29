# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2018 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

from __future__ import absolute_import, division, unicode_literals

__authors__ = ['Marius Retegan']
__license__ = 'MIT'
__date__ = '29/05/2018'


import os
import json
try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, Request, URLError

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QMainWindow, QPlainTextEdit, QDialog, QFileDialog,
                             QDialogButtonBox)
from PyQt5.QtGui import QFontDatabase
from PyQt5.uic import loadUi
from silx.resources import resource_filename as resourceFileName

from .config import Config
from .quanty import QuantyDockWidget
from ..version import version


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        uiPath = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'main.ui'))
        loadUi(uiPath, baseinstance=self, package='crispy.gui')

        # Default elements of the main window.
        self.setWindowTitle('Crispy - untitled.lua')
        self.statusbar.showMessage('Ready')

        # Splitter.
        upperPanelHeight = 500
        lowerPanelHeight = 600 - upperPanelHeight
        self.splitter.setSizes((upperPanelHeight, lowerPanelHeight))

        # Logger widget.
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(font.pointSize() + 1)
        self.loggerWidget.setFont(font)
        self.loggerWidget.setLineWrapMode(QPlainTextEdit.NoWrap)

        # About dialog.
        self.aboutDialog = AboutDialog(self)
        self.openAboutDialogAction.triggered.connect(self.openAboutDialog)

        # Quanty module.
        self.quantyModuleInit()

    def quantyModuleInit(self):
        # Load components related to the Quanty module.
        self.quantyDockWidget = QuantyDockWidget(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.quantyDockWidget)
        self.quantyDockWidget.setVisible(True)

        # Menu.
        self.quantyOpenPreferencesDialogAction.triggered.connect(
            self.quantyOpenPreferencesDialog)

        self.quantySaveInputAction.triggered.connect(
            self.quantyDockWidget.saveInput)
        self.quantySaveInputAsAction.triggered.connect(
            self.quantyDockWidget.saveInputAs)

        self.quantySaveAllCalculationsAsAction.triggered.connect(
            self.quantyDockWidget.saveAllCalculationsAs)

        self.quantyRemoveAllCalculationsAction.triggered.connect(
            self.quantyDockWidget.removeAllCalculations)

        self.quantyLoadCalculationsAction.triggered.connect(
            self.quantyDockWidget.loadCalculations)

        self.quantyRunCalculationAction.triggered.connect(
            self.quantyDockWidget.runCalculation)

        self.quantyMenuUpdate(False)

        self.quantyModuleShowAction.triggered.connect(self.quantyModuleShow)
        self.quantyModuleHideAction.triggered.connect(self.quantyModuleHide)

        # Preferences dialog.
        self.preferencesDialog = QuantyPreferencesDialog(self)

    def quantyMenuUpdate(self, flag=True):
        self.quantySaveAllCalculationsAsAction.setEnabled(flag)
        self.quantyRemoveAllCalculationsAction.setEnabled(flag)

    def quantyModuleShow(self):
        self.quantyDockWidget.setVisible(True)
        self.menuModulesQuanty.insertAction(
            self.quantyModuleShowAction, self.quantyModuleHideAction)
        self.menuModulesQuanty.removeAction(self.quantyModuleShowAction)

    def quantyModuleHide(self):
        self.quantyDockWidget.setVisible(False)
        self.menuModulesQuanty.insertAction(
            self.quantyModuleHideAction, self.quantyModuleShowAction)
        self.menuModulesQuanty.removeAction(self.quantyModuleHideAction)

    def quantyOpenPreferencesDialog(self):
        self.preferencesDialog.show()

    def openAboutDialog(self):
        self.aboutDialog.show()


class QuantyPreferencesDialog(QDialog):

    def __init__(self, parent):
        super(QuantyPreferencesDialog, self).__init__(parent)

        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'quanty', 'preferences.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.updateWidgetWithConfigSettings()

        self.pathBrowsePushButton.clicked.connect(self.setExecutablePath)

        ok = self.buttonBox.button(QDialogButtonBox.Ok)
        ok.clicked.connect(self.acceptSettings)

        cancel = self.buttonBox.button(QDialogButtonBox.Cancel)
        cancel.clicked.connect(self.rejectSettings)

    def updateWidgetWithConfigSettings(self):
        config = Config()
        path = config.getSetting('quantyPath')
        verbosity = config.getSetting('quantyVerbosity')
        self.pathLineEdit.setText(path)
        self.verbosityLineEdit.setText(verbosity)

    def acceptSettings(self):
        config = Config()
        path = self.pathLineEdit.text()
        verbosity = self.verbosityLineEdit.text()
        config.setSetting('quantyPath', path)
        config.setSetting('quantyVerbosity', verbosity)
        config.saveSettings()
        self.close()

    def rejectSettings(self):
        self.updateWidgetWithConfigSettings()
        self.close()

    def setExecutablePath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Select File', os.path.expanduser('~'))

        if path:
            path = os.path.dirname(path)
            self.pathLineEdit.setText(path)


class CheckUpdateThread(QThread):

    updateAvailable = pyqtSignal()

    def __init__(self, parent):
        super(CheckUpdateThread, self).__init__(parent)

    def _getSiteVersion(self):
        url = 'http://www.esrf.eu/computing/scientific/crispy/version.json'

        request = Request(url)
        request.add_header('Cache-Control', 'max-age=0')

        try:
            response = urlopen(request, timeout=5)
        except URLError:
            return

        data = json.loads(response.read().decode('utf-8'))
        version = data['version']

        return version

    def run(self):
        seconds = 5
        self.sleep(seconds)
        siteVersion = self._getSiteVersion()
        if siteVersion and version < siteVersion:
            self.updateAvailable.emit()


class UpdateAvailableDialog(QDialog):

    def __init__(self, parent):
        super(UpdateAvailableDialog, self).__init__(parent)

        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'update.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')


class AboutDialog(QDialog):

    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)

        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'about.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.nameLabel.setText('Crispy {}'.format(version))

        self.config = Config()
        updateCheck = self.config.getSetting('updateCheck')
        self.updateCheckBox.setChecked(updateCheck)
        self.updateCheckBox.stateChanged.connect(
            self.updateCheckBoxStateChanged)

        # Check for updates if requested.
        self.runUpdateCheck()

    def updateCheckBoxStateChanged(self):
        updateCheck = self.updateCheckBox.isChecked()
        self.config.setSetting('updateCheck', updateCheck)
        self.config.saveSettings()
        self.runUpdateCheck()

    def runUpdateCheck(self):
        if self.updateCheckBox.isChecked():
            thread = CheckUpdateThread(self)
            thread.start()
            thread.updateAvailable.connect(self.informAboutAvailableUpdate)

    def informAboutAvailableUpdate(self):
        updateAvailableDialog = UpdateAvailableDialog(self.parent())
        updateAvailableDialog.show()
