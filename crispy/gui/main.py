# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2019 European Synchrotron Radiation Facility
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
__date__ = '14/01/2019'


import os
import json
try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, Request, URLError
import sys
import socket

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QByteArray, QSize, QPoint
from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit, QDialog
from PyQt5.QtGui import QFontDatabase
from PyQt5.uic import loadUi
from silx.resources import resource_filename as resourceFileName

from .config import Config
from .quanty import QuantyDockWidget, QuantyPreferencesDialog
from ..version import version


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        uiPath = resourceFileName('uis:main.ui')
        loadUi(uiPath, baseinstance=self, package='crispy.gui')

        # Main window.
        self.statusbar.showMessage('Ready')

        # Logger widget.
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        if sys.platform == 'darwin':
            font.setPointSize(font.pointSize() + 1)
        self.loggerWidget.setFont(font)
        self.loggerWidget.setLineWrapMode(QPlainTextEdit.NoWrap)

        # About dialog.
        self.aboutDialog = AboutDialog(parent=self)
        self.openAboutDialogAction.triggered.connect(self.openAboutDialog)

        # Quanty module.
        self.quantyModuleInit()

    def showEvent(self, event):
        self.loadSettings()
        super(MainWindow, self).showEvent(event)

    def closeEvent(self, event):
        self.plotWidget.closeProfileWindow()
        self.saveSettings()
        super(MainWindow, self).closeEvent(event)

    def loadSettings(self):
        config = Config()
        self.settings = config.read()

        if self.settings is None:
            return

        currentPath = self.settings.value('CurrentPath')
        if currentPath is None:
            path = os.path.expanduser('~')
        else:
            path = currentPath
        self.currentPath = path

        self.settings.beginGroup('MainWindow')

        state = self.settings.value('State')
        if state is not None:
            self.restoreState(QByteArray(state))

        size = self.settings.value('Size')
        if size is not None:
            self.resize(QSize(size))

        pos = self.settings.value('Position')
        if pos is not None:
            self.move(QPoint(pos))

        splitter = self.settings.value('Splitter')
        if splitter is not None:
            sizes = [int(size) for size in splitter]
        else:
            sizes = [6, 1]
        self.splitter.setSizes(sizes)
        self.settings.endGroup()

    def saveSettings(self):
        self.settings.setValue('Version', version)

        self.settings.beginGroup('MainWindow')
        self.settings.setValue('State', self.saveState())
        self.settings.setValue('Size', self.size())
        self.settings.setValue('Position', self.pos())
        self.settings.setValue('Splitter', self.splitter.sizes())
        self.settings.endGroup()

        self.settings.sync()

    def quantyModuleInit(self):
        # Load components related to the Quanty module.
        self.quantyDockWidget = QuantyDockWidget(parent=self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.quantyDockWidget)
        self.quantyDockWidget.setVisible(True)

        # Menu.
        self.quantyOpenPreferencesDialogAction.triggered.connect(
            self.quantyOpenPreferencesDialog)

        self.quantySaveInputAction.triggered.connect(
            self.quantyDockWidget.saveInput)
        self.quantySaveInputAsAction.triggered.connect(
            self.quantyDockWidget.saveInputAs)

        self.quantyRunCalculationAction.triggered.connect(
            self.quantyDockWidget.runCalculation)

        self.quantyModuleShowAction.triggered.connect(self.quantyModuleShow)
        self.quantyModuleHideAction.triggered.connect(self.quantyModuleHide)

        self.loadExperimentalDataAction.triggered.connect(
            self.quantyDockWidget.loadExperimentalData)

        # Preferences dialog.
        self.preferencesDialog = QuantyPreferencesDialog(parent=self)

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


class CheckUpdateThread(QThread):

    updateAvailable = pyqtSignal()

    def __init__(self, parent):
        super(CheckUpdateThread, self).__init__(parent)

    def _getSiteVersion(self):
        URL = 'http://www.esrf.eu/computing/scientific/crispy/version.json'

        request = Request(URL)
        request.add_header('Cache-Control', 'max-age=0')

        try:
            response = urlopen(request, timeout=5)
        except (URLError, socket.timeout):
            return None

        try:
            data = json.loads(response.read().decode('utf-8'))
        # Use bare except to make sure we catch all possible errors.
        # We do not want to fail here.
        except: # noqa
            return None

        version = data['version']

        return version

    def run(self):
        seconds = 5
        self.sleep(seconds)
        siteVersion = self._getSiteVersion()
        if siteVersion is not None and version < siteVersion:
            self.updateAvailable.emit()


class UpdateAvailableDialog(QDialog):

    def __init__(self, parent):
        super(UpdateAvailableDialog, self).__init__(parent)

        path = resourceFileName('uis:update.ui')
        loadUi(path, baseinstance=self, package='crispy.gui')


class AboutDialog(QDialog):

    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)

        config = Config()
        self.settings = config.read()

        path = resourceFileName('uis:about.ui')
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.nameLabel.setText('Crispy {}'.format(version))

        if self.settings:
            updateCheck = self.settings.value('CheckForUpdates')
            if updateCheck is None:
                updateCheck = 1
            self.updateCheckBox.setChecked(int(updateCheck))
            self.updateCheckBox.stateChanged.connect(
                self.updateCheckBoxStateChanged)
            self.settings.setValue('CheckForUpdates', updateCheck)
            self.settings.sync()
            self.runUpdateCheck()

    def updateCheckBoxStateChanged(self):
        updateCheck = int(self.updateCheckBox.isChecked())
        if self.settings:
            self.settings.setValue('CheckForUpdates', updateCheck)
        self.runUpdateCheck()

    def runUpdateCheck(self):
        if self.updateCheckBox.isChecked():
            thread = CheckUpdateThread(self)
            thread.start()
            thread.updateAvailable.connect(self.informAboutAvailableUpdate)

    def informAboutAvailableUpdate(self):
        updateAvailableDialog = UpdateAvailableDialog(self.parent())
        updateAvailableDialog.show()
