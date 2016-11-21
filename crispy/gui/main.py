# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit
from PyQt5.QtGui import QFontDatabase
from PyQt5.uic import loadUi

from .quanty import QuantyDockWidget
from ..resources import resourceFileName


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        uiPath = resourceFileName(os.path.join('gui', 'uis', 'main.ui'))
        loadUi(uiPath, baseinstance=self, package='crispy.gui')

        self.setWindowTitle('Crispy - untitled.lua')

        self.splitter.setSizes((600, 0))

        self.statusbar.showMessage('Ready')

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(font.pointSize() + 1)
        self.loggerWidget.setFont(font)
        self.loggerWidget.setLineWrapMode(QPlainTextEdit.NoWrap)

        # Quanty
        self.quantyDockWidget = QuantyDockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, self.quantyDockWidget)
        self.quantyDockWidget.setVisible(True)
        self.quantyRunCalculationAction.triggered.connect(
            self.quantyDockWidget.runCalculation)
        self.quantySaveInputAction.triggered.connect(
            self.quantyDockWidget.saveInput)
        self.quantySaveAsInputAction.triggered.connect(
            self.quantyDockWidget.saveInputAs)
        self.quantyLoadCalculations.triggered.connect(
                self.quantyDockWidget.loadCalculations)
        self.quantyRemoveAllCalculations.triggered.connect(
                self.quantyDockWidget.removeAllCalculations)

        self.quantyModuleShowAction.triggered.connect(self.quantyModuleShow)
        self.quantyModuleHideAction.triggered.connect(self.quantyModuleHide)

        # ORCA
        # self.orcaDockWidget = QDockWidget()
        # self.addDockWidget(Qt.RightDockWidgetArea, self.orcaDockWidget)
        # self.orcaDockWidget.setVisible(False)

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


def main():
    pass

if __name__ == '__main__':
    main
