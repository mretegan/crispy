# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
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
__date__ = '06/05/2018'


import errno
import json
import os
import sys

from PyQt5.QtCore import Qt, QStandardPaths
from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit, QDialog, QFileDialog
from PyQt5.QtGui import QFontDatabase, QIcon
from PyQt5.uic import loadUi
from silx.resources import resource_filename as resourceFileName

from .quanty import QuantyDockWidget
from ..version import version
from ..utils.odict import odict


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Load the settings from file or use defaults if this is not available.
        self.loadSettings()

        uiPath = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'main.ui'))
        loadUi(uiPath, baseinstance=self, package='crispy.gui')

        # Main window default elements.
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
        self.aboutDialog = AboutDialog()
        self.openAboutDialogAction.triggered.connect(self.openAboutDialog)

        # Quanty module.
        self.quantyModuleInit()

    def quantyModuleInit(self):
        # Load components related to the Quanty module.
        self.quantyDockWidget = QuantyDockWidget(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.quantyDockWidget)
        self.quantyDockWidget.setVisible(True)

        # Menu.
        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'cog.svg')))
        self.quantyOpenPreferencesDialogAction.setIcon(icon)
        self.quantyOpenPreferencesDialogAction.triggered.connect(
            self.quantyOpenPreferencesDialog)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'save.svg')))
        self.quantySaveInputAction.setIcon(icon)
        self.quantySaveInputAction.triggered.connect(
            self.quantyDockWidget.saveInput)
        self.quantySaveInputAsAction.triggered.connect(
            self.quantyDockWidget.saveInputAs)

        self.quantySaveCalculationsAsAction.setIcon(icon)
        self.quantySaveCalculationsAsAction.triggered.connect(
            self.quantyDockWidget.saveCalculationsAs)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'trash.svg')))
        self.quantyRemoveCalculationsAction.setIcon(icon)
        self.quantyRemoveCalculationsAction.triggered.connect(
            self.quantyDockWidget.removeCalculations)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'folder-open.svg')))
        self.quantyLoadCalculationsAction.setIcon(icon)
        self.quantyLoadCalculationsAction.triggered.connect(
            self.quantyDockWidget.loadCalculations)

        self.quantyRunCalculationAction.triggered.connect(
            self.quantyDockWidget.runCalculation)

        self.quantyMenuUpdate(False)

        self.quantyModuleShowAction.triggered.connect(self.quantyModuleShow)
        self.quantyModuleHideAction.triggered.connect(self.quantyModuleHide)

        # Preferences dialog.
        # TODO: Add buttons?
        self.preferencesDialog = QuantyPreferencesDialog()
        self.preferencesDialog.setModal(True)
        self.preferencesDialog.pathLineEdit.setText(
            self.settings['quanty.path'])
        self.preferencesDialog.verbosityLineEdit.setText(
            self.settings['quanty.verbosity'])
        self.preferencesDialog.pathBrowsePushButton.clicked.connect(
            self.quantySetPath)

    def quantyMenuUpdate(self, flag=True):
        self.quantySaveCalculationsAsAction.setEnabled(flag)
        self.quantyRemoveCalculationsAction.setEnabled(flag)

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

    def quantySetPath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Select File', os.path.expanduser('~'))

        if path:
            path = os.path.dirname(path)
            self.updateSettings('quanty.path', path)
            self.preferencesDialog.pathLineEdit.setText(path)

    def quantyGetPath(self):
        if sys.platform in 'win32':
            executable = 'Quanty.exe'
        else:
            executable = 'Quanty'

        envPath = QStandardPaths.findExecutable(executable)
        localPath = QStandardPaths.findExecutable(
            executable, [resourceFileName(
                'crispy:' + os.path.join('modules', 'quanty', 'bin'))])

        # Check if Quanty is in the paths defined in the $PATH.
        if envPath:
            path = os.path.dirname(envPath)
        # Check if Quanty is bundled with Crispy.
        elif localPath:
            path = os.path.dirname(localPath)
        else:
            path = None

        return path, executable

    def openAboutDialog(self):
        self.aboutDialog.show()

    def getConfigLocation(self):
        configLocation = QStandardPaths.GenericConfigLocation
        root = QStandardPaths.standardLocations(configLocation)[0]

        if sys.platform in ('win32', 'darwin'):
            path = os.path.join(root, 'Crispy')
        else:
            path = os.path.join(root, 'crispy')

        return path

    def saveSettings(self):
        if not hasattr(self, 'settings'):
            return

        path = self.getConfigLocation()

        try:
            os.makedirs(path, mode=0o755)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        settingsPath = os.path.join(path, 'settings.json')

        with open(settingsPath, 'w') as p:
            json.dump(self.settings, p)

    def updateSettings(self, setting, value):
        self.settings[setting] = value
        self.saveSettings()

    def loadSettings(self, defaults=False):
        if defaults:
            self.settings = odict()
            path, executable = self.quantyGetPath()
            self.settings['quanty.path'] = path
            self.settings['quanty.executable'] = executable
            self.settings['quanty.verbosity'] = '0x0000'
            self.settings['currentPath'] = os.path.expanduser('~')
            self.settings['version'] = version
            self.saveSettings()
            return

        settingsPath = os.path.join(
            self.getConfigLocation(), 'settings.json')

        try:
            with open(settingsPath, 'r') as p:
                self.settings = json.loads(
                    p.read(), object_pairs_hook=odict)
        except IOError as e:
            self.loadSettings(defaults=True)

        # Overwrite settings file written by previous versions of Crispy.
        if 'version' not in self.settings:
            self.loadSettings(defaults=True)


class QuantyPreferencesDialog(QDialog):

    def __init__(self, parent=None):
        super(QuantyPreferencesDialog, self).__init__()

        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'quanty', 'preferences.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')


class AboutDialog(QDialog):

    def __init__(self, parent=None):
        super(AboutDialog, self).__init__()

        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'about.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.nameLabel.setText('Crispy {}'.format(version))
