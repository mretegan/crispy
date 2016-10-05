# coding: utf-8

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDockWidget
from PyQt5.uic import loadUi

from ..resources import resourceFileName
from .quanty import QuantyDockWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uiPath = resourceFileName('gui/uis/main.ui')
        loadUi(uiPath, baseinstance=self, package='crispy.gui')

        self.statusBar().showMessage('Ready')

        # Quanty
        self.quantyDockWidget = QuantyDockWidget()
        self.addDockWidget(Qt.RightDockWidgetArea, self.quantyDockWidget)
        self.quantyDockWidget.setVisible(True)
        self.quantyRunCalculationAction.triggered.connect(print)
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
