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
__date__ = '17/07/2018'


import os
import json
try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, Request, URLError
import sys

from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QByteArray, QSize, QPoint, QStandardPaths)
from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit, QDialog
from PyQt5.QtGui import QFontDatabase
from PyQt5.uic import loadUi
from silx.resources import resource_filename as resourceFileName

from .quanty import QuantyDockWidget, QuantyPreferencesDialog
from ..version import version


class MainWindow(QMainWindow):

    def __init__(self, settings=None):
        super(MainWindow, self).__init__()

        self.settings = settings

        uiPath = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'main.ui'))
        loadUi(uiPath, baseinstance=self, package='crispy.gui')

        # Default elements of the main window.
        self.setWindowTitle('Crispy - untitled.lua')
        self.statusbar.showMessage('Ready')

        # Logger widget.
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        if sys.platform == 'darwin':
            font.setPointSize(font.pointSize() + 1)
        self.loggerWidget.setFont(font)
        self.loggerWidget.setLineWrapMode(QPlainTextEdit.NoWrap)

        # About dialog.
        self.aboutDialog = AboutDialog(parent=self, settings=self.settings)
        self.openAboutDialogAction.triggered.connect(self.openAboutDialog)

        # Quanty module.
        self.quantyModuleInit()

        # Remove the old config file.
        self._removeConfig()

        # Restore the settings from file.
        self.restoreSettings()
        self.saveSettings()

    def _removeConfig(self):
        configLocation = QStandardPaths.GenericConfigLocation
        root = QStandardPaths.standardLocations(configLocation)[0]

        if sys.platform in ('win32', 'darwin'):
            path = os.path.join(root, 'Crispy')
        else:
            path = os.path.join(root, 'crispy')

        if version < '0.7.0':
            try:
                os.remove(os.path.join(path, 'settings.json'))
                os.rmdir(path)
            except (IOError, OSError) as e:
                pass

    def restoreSettings(self):
        settings = self.settings
        if settings is None:
            return

        currentPath = settings.value('CurrentPath')
        if currentPath is None:
            path = os.path.expanduser('~')
        else:
            path = settings.value('CurrentPath')
        self.currentPath = path

        settings.beginGroup('MainWindow')

        state = settings.value('State')
        if state is not None:
            self.restoreState(QByteArray(state))

        size = settings.value('Size')
        if size is not None:
            self.resize(QSize(size))

        pos = settings.value('Position')
        if pos is not None:
            self.move(QPoint(pos))

        splitter = settings.value('Splitter')
        if splitter is not None:
            sizes = [int(size) for size in splitter]
        else:
            sizes = [6, 1]
        self.splitter.setSizes(sizes)
        settings.endGroup()

    def saveSettings(self):
        settings = self.settings
        if settings is None:
            return

        settings.setValue('Version', version)
        settings.setValue('CurrentPath', self.currentPath)

        settings.beginGroup('MainWindow')
        settings.setValue('State', self.saveState())
        settings.setValue('Size', self.size())
        settings.setValue('Position', self.pos())
        settings.setValue('Splitter', self.splitter.sizes())
        settings.endGroup()

        settings.sync()

    def closeEvent(self, event):
        self.saveSettings()
        event.accept()

    def quantyModuleInit(self):
        # Load components related to the Quanty module.
        self.quantyDockWidget = QuantyDockWidget(
            parent=self, settings=self.settings)
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
        self.preferencesDialog = QuantyPreferencesDialog(
            parent=self, settings=self.settings)

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

    def __init__(self, parent, settings=None):
        super(AboutDialog, self).__init__(parent)

        self.settings = settings

        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'about.ui'))
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
