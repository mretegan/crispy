# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDockWidget
from PyQt5.QtGui import QFontDatabase
from PyQt5.uic import loadUi

from .widgets.plotwidget import PlotWidget
from .quanty import QuantyDockWidget
from ..resources import resourceFileName


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        uiPath = resourceFileName('gui/uis/main.ui')
        loadUi(uiPath, baseinstance=self, package='crispy.gui')

        self.splitter.setSizes((600, 0))

        self.statusbar.showMessage('Ready')

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(font.pointSize() + 1)
        self.loggerWidget.setFont(font)

        # Quanty
        self.quantyDockWidget = QuantyDockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, self.quantyDockWidget)
        self.quantyDockWidget.setVisible(True)
        self.quantyRunCalculationAction.triggered.connect(
            self.quantyDockWidget.runCalculation)
        self.quantySaveInputAction.triggered.connect(
            self.quantyDockWidget.saveInput)
        self.quantySaveAsInputAction.triggered.connect(
            self.quantyDockWidget.saveAsInput)

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
