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
__date__ = '18/05/2018'


import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QPlainTextEdit, QDialog, QFileDialog,
                             QDialogButtonBox)
from PyQt5.QtGui import QFontDatabase, QIcon
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
        self.preferencesDialog = QuantyPreferencesDialog(self)

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
        path = config.getSetting('quanty.path')
        verbosity = config.getSetting('quanty.verbosity')
        self.pathLineEdit.setText(path)
        self.verbosityLineEdit.setText(verbosity)

    def acceptSettings(self):
        config = Config()
        path = self.pathLineEdit.text()
        verbosity = self.verbosityLineEdit.text()
        config.setSetting('quanty.path', path)
        config.setSetting('quanty.verbosity', verbosity)
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


class AboutDialog(QDialog):

    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)

        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'about.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.nameLabel.setText('Crispy {}'.format(version))
