# coding: utf-8

import collections
import json
import numpy as np
import os
import sys
import subprocess

from PyQt5.QtCore import QItemSelectionModel, QEvent, Qt
from PyQt5.QtWidgets import (
    QAbstractItemView, QDoubleSpinBox, QLabel,
    QMainWindow, QGroupBox, QHBoxLayout, QTabWidget)
from PyQt5 import uic

from .models.treemodel import TreeModel
from .models.listmodel import ListModel
from .widgets.plotwidget import PlotWidget
from ..resources import resource_filename


class MainWindow(QMainWindow):

    _defaults = {'baseName': 'quanty',
                 'element': 'Ni',
                 'charge': '2+',
                 'symmetry': 'Oh',
                 'theoreticalModel': 'Crystal field (CF)',
                 'experiment': 'XAS',
                 'edge': 'L2,3 (2p)',
                 'temperature': 1.0,
                 'magneticField': [0.0, 0.0, 0.0],
                 'broadenings': [0.5, 0.5]}

    def __init__(self):
        super(MainWindow, self).__init__()
        self.__dict__.update(self._defaults)
        uic.loadUi(resource_filename('gui/main.ui'), baseinstance=self,
                   package='crispy.gui')

        self.loadUiParameters()
        self.populateUi()
        self.activateUi()

        self.loadHamiltonianParameters()
        self.updateHamiltonian()

        self.statusBar().showMessage('Ready')

    def loadHamiltonianParameters(self):
        with open(resource_filename('modules/quanty/hamiltonian.json')) as fp:
            self.hamiltonianParameters = json.loads(
                fp.read(), object_pairs_hook=collections.OrderedDict)

    def loadUiParameters(self):
        # Load the parameters used to populate some of the UI elements.
        with open(resource_filename('modules/quanty/ui.json')) as fp:
            self.uiParameters = json.loads(
                fp.read(), object_pairs_hook=collections.OrderedDict)

    def populateUi(self):
        self.elementComboBox.addItems(self.uiParameters)
        self.elementComboBox.setCurrentText(self.element)

        self.chargeComboBox.addItems(self.uiParameters[self.element])
        self.chargeComboBox.setCurrentText(self.charge)

        self.symmetryComboBox.addItems(
                self.uiParameters[self.element][self.charge])
        self.symmetryComboBox.setCurrentText(self.symmetry)

        self.theoreticalModelComboBox.addItems(
                self.uiParameters[self.element][self.charge][self.symmetry])
        self.theoreticalModelComboBox.setCurrentText(self.theoreticalModel)

        self.experimentComboBox.addItems(
                self.uiParameters[self.element][self.charge][self.symmetry]
                [self.theoreticalModel])
        self.experimentComboBox.setCurrentText(self.experiment)

        self.edgeComboBox.addItems(
                self.uiParameters[self.element][self.charge][self.symmetry]
                [self.theoreticalModel][self.experiment])
        self.edgeComboBox.setCurrentText(self.edge)

        self.broadeningGaussianDoubleSpinBox.setValue(self.broadenings[0])
        self.broadeningLorentzianDoubleSpinBox.setValue(self.broadenings[1])

        self.temperatureDoubleSpinBox.setValue(self.temperature)

        self.magneticFieldXDoubleSpinBox.setValue(self.magneticField[0])
        self.magneticFieldYDoubleSpinBox.setValue(self.magneticField[1])
        self.magneticFieldZDoubleSpinBox.setValue(self.magneticField[2])

        self.resultsModel = ListModel(list())
        self.resultsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.resultsView.setModel(self.resultsModel)
        self.resultsView.selectionModel().selectionChanged.connect(
            self.selectedResultsChanged)
        self.resultsView.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.resultsView.viewport().installEventFilter(self)

    def activateUi(self):
        # Activate the combo boxes.
        self.elementComboBox.currentTextChanged.connect(self.updateUi)
        self.chargeComboBox.currentTextChanged.connect(self.updateUi)
        self.symmetryComboBox.currentTextChanged.connect(self.updateUi)

        self.theoreticalModelComboBox.currentTextChanged.connect(self.updateUi)

        self.experimentComboBox.currentTextChanged.connect(self.updateUi)
        self.edgeComboBox.currentTextChanged.connect(self.updateUi)

        # Activate the buttons.
        self.savePushButton.clicked.connect(self.saveInput)
        self.runPushButton.clicked.connect(self.runCalculation)

        # Activate the menubar.
        self.actionSave.triggered.connect(self.saveInput)
        self.actionRun.triggered.connect(self.runCalculation)

    def updateUi(self):
        self.element = self.elementComboBox.currentText()

        self.chargeComboBox.updateItems(self.uiParameters[self.element])
        self.charge = self.chargeComboBox.currentText()

        self.symmetryComboBox.updateItems(
                self.uiParameters[self.element][self.charge])
        self.symmetry = self.symmetryComboBox.currentText()

        self.theoreticalModelComboBox.updateItems(
                self.uiParameters[self.element][self.charge][self.symmetry])
        self.theoreticalModel = self.theoreticalModelComboBox.currentText()

        self.experimentComboBox.updateItems(
                self.uiParameters[self.element][self.charge][self.symmetry]
                [self.theoreticalModel])
        self.experiment = self.experimentComboBox.currentText()

        self.edgeComboBox.updateItems(
                self.uiParameters[self.element][self.charge][self.symmetry]
                [self.theoreticalModel][self.experiment])
        self.edge = self.edgeComboBox.currentText()

        self.updateHamiltonian()

    def updateHamiltonian(self):
        data = self.hamiltonianParameters[self.element][self.charge]

        configurations = (self.uiParameters[self.element][self.charge]
                          [self.symmetry][self.theoreticalModel]
                          [self.experiment][self.edge]['configurations'])

        hamiltonian = collections.OrderedDict()

        for hamiltonianTerm in data:
            if 'field' not in hamiltonianTerm:
                parameters = data[hamiltonianTerm]
            else:
                hamiltonianTerm = self.theoreticalModel
                parameters = data[hamiltonianTerm][self.symmetry]

            hamiltonian[hamiltonianTerm] = collections.OrderedDict()

            for configuration in configurations:
                label = '{0} ({1})'.format(
                    configuration.capitalize(), configurations[configuration])

                hamiltonian[hamiltonianTerm][label] = (
                    parameters[configurations[configuration]])

        # Create the Hamiltonian model.
        self.hamiltonianModel = TreeModel(
            header=['parameter', 'value', 'min', 'max'],
            data=hamiltonian)

        # Assign the Hamiltonian model to the Hamiltonian view.
        self.hamiltonianTermsView.setModel(self.hamiltonianModel)
        self.hamiltonianTermsView.selectionModel().setCurrentIndex(
            self.hamiltonianModel.index(0, 0), QItemSelectionModel.Select)
        index = self.hamiltonianTermsView.selectionModel().currentIndex()
        self.hamiltonianTermsView.selectionModel().selectionChanged.connect(
            self.selectedHamiltonianTermChanged)
        self.hamiltonianTermsView.setAttribute(
                Qt.WA_MacShowFocusRect, False)

        # Assign the Hamiltonian model to the Hamiltonian parameters view, and
        # set some properties.
        self.hamiltonianParametersView.setModel(self.hamiltonianModel)
        self.hamiltonianParametersView.expandAll()
        self.hamiltonianParametersView.resizeColumnToContents(0)
        self.hamiltonianParametersView.resizeColumnToContents(1)
        self.hamiltonianParametersView.setRootIndex(index)
        self.hamiltonianParametersView.setAttribute(
                Qt.WA_MacShowFocusRect, False)
        self.hamiltonianParametersView.viewport().installEventFilter(self)

    def selectedHamiltonianTermChanged(self):
        index = self.hamiltonianTermsView.selectionModel().currentIndex()
        self.hamiltonianParametersView.setRootIndex(index)

    def selectedResultsChanged(self):
        self.plotWidget.clear()
        selectedIndexes = self.resultsView.selectionModel().selectedIndexes()
        for index in selectedIndexes:
            label, spectrum = self.resultsModel.getIndexData(index)
            self.plotWidget.plot(spectrum[:, 0], -spectrum[:, 2], label[:3])

    def eventFilter(self, source, event):
        if (event.type() == QEvent.MouseButtonPress and
            event.button() == Qt.RightButton and
            (source is self.hamiltonianParametersView.viewport() or
                source is self.resultsView.viewport())):
            return True
        else:
            return super(MainWindow, self).eventFilter(source, event)

    def saveInput(self):
        # Load the template file specific to the requested calculation.
        templateFileName = (self.uiParameters[self.element][self.charge]
                            [self.symmetry][self.theoreticalModel]
                            [self.experiment][self.edge]['template'])

        templateFile = resource_filename(
            os.path.join('modules', 'quanty', 'templates',
                         '{0:s}.lua'.format(templateFileName)))

        with open(templateFile) as fp:
            inputFile = fp.read()

        shells = (self.uiParameters[self.element][self.charge]
                  [self.symmetry][self.theoreticalModel][self.experiment]
                  [self.edge]['shells'])

        for shell in shells:
            inputFile = inputFile.replace(
                    '$NElectrons_{0:s}'.format(shell), str(shells[shell]))

        inputFile = inputFile.replace(
                '$BroadeningGaussian', '{0:8.2f}'.format(
                    self.broadeningGaussianDoubleSpinBox.value()))
        inputFile = inputFile.replace(
                '$BroadeningLorentzian', '{0:8.2f}'.format(
                    self.broadeningLorentzianDoubleSpinBox.value()))

        inputFile = inputFile.replace(
                '$T', '{0:8.3f}'.format(
                    self.temperatureDoubleSpinBox.value()))

        inputFile = inputFile.replace(
                '$Bx', '{0:8.3f}'.format(
                    self.magneticFieldXDoubleSpinBox.value()))
        inputFile = inputFile.replace(
                '$By', '{0:8.3f}'.format(
                    self.magneticFieldYDoubleSpinBox.value()))
        inputFile = inputFile.replace(
                '$Bz', '{0:8.3f}'.format(
                    self.magneticFieldZDoubleSpinBox.value()))

        # Get the most recent Hamiltonian data from the model.
        hamiltonian = self.hamiltonianModel.getModelData()

        for hamiltonianTerm in hamiltonian:
            configurations = hamiltonian[hamiltonianTerm]
            for configuration in configurations:
                if 'Ground state' in configuration:
                    suffix = 'gs'
                elif 'Intermediate state' in configuration:
                    suffix = 'is'
                elif 'Final state' in configuration:
                    suffix = 'fs'
                else:
                    suffix = str()
                parameters = configurations[configuration]
                for parameter in parameters:
                    inputFile = inputFile.replace(
                        '${0:s}_{1:s}'.format(parameter, suffix),
                        '{0:8.4f}'.format(float(parameters[parameter])))

        for hamiltonianTerm, hamiltonianTermState in (
                self.hamiltonianModel.getNodesState().items()):
            if 'Coulomb' in hamiltonianTerm:
                termName = 'H_coulomb'
            elif 'Spin-orbit coupling' in hamiltonianTerm:
                termName = 'H_soc'
            elif 'Crystal field' in hamiltonianTerm:
                termName = 'H_cf'
            elif 'Ligand field' in hamiltonianTerm:
                termName = 'H_lf'

            # Check the state of the Hamiltonian term.
            if hamiltonianTermState == 0:
                termState = 0
            else:
                termState = 1

            inputFile = inputFile.replace(
                    '${0:s}'.format(termName), '{0:2.1f}'.format(termState))

        with open('{0:s}.lua'.format(self.baseName), 'w') as fp:
            fp.write(inputFile)

    def runCalculation(self):
        # Write the input file to disk.
        self.saveInput()

        output = subprocess.check_output(
                ['Quanty', '{0:s}.lua'.format(self.baseName)])

        data = np.loadtxt('{0:s}.spec'.format(self.baseName), skiprows=5)

        # Load the data to be plotted.
        id = len(self.resultsModel._data) + 1
        label = '#{:d} - {:s}{:s} | {:s} | {:s} | {:s} | {:s}'.format(
            id, self.element, self.charge, self.symmetry,
            self.theoreticalModel, self.experiment, self.edge)

        # Plot the spectrum.
        self.plotWidget.clear()
        self.plotWidget.plot(data[:, 0], -data[:, 2], label[:3])

        # Store the simulation details.
        self.resultsModel.appendItem((label, data))

        # Update the selected item in the results view.
        self.resultsView.selectionModel().clearSelection()
        index = self.resultsModel.index(self.resultsModel.rowCount()-1)
        self.resultsView.selectionModel().select(
                index, QItemSelectionModel.Select)


def main():
    import os
    import sys

    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('Crispy')
    window.show()

    # app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
