# coding: utf-8

import collections
import json
import numpy as np
import os
import sys

from PyQt5.QtCore import QItemSelectionModel, Qt
from PyQt5.QtWidgets import (
    QAbstractItemView, QDoubleSpinBox, QLabel,
    QMainWindow, QGroupBox, QHBoxLayout, QTabWidget)
from PyQt5 import uic

from .models.treemodel import TreeModel
from .models.listmodel import ListModel
from ..backends import Quanty


class MainWindow(QMainWindow):

    _defaults = {'element': 'Ni',
                 'charge': '2+',
                 'symmetry': 'Oh',
                 'experiment': 'XAS',
                 'edge': 'L2,3',
                 'polarization': 'iso',
                 'temperature': 1.0,
                 'magneticFieldX': 0.0,
                 'magneticFieldY': 0.0,
                 'magneticFieldZ': 0.0,
                 'broadeningGaussian': 0.4,
                 'broadeningLorentzian': 0.4,
                 'backend': 'Quanty',
                 'hamiltonianModelData': collections.OrderedDict()}

    def __init__(self):
        super(MainWindow, self).__init__()
        self.__dict__.update(self._defaults)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),
            'canvas.ui'), self)

        self.root = os.getenv('CRISPY_ROOT')

        self.loadParameters()
        self.updateHamiltonianModelData()

        self.populateCanvas()
        self.activateToolBoxActions()
        self.statusBar().showMessage('Ready')

        self.setBackend()

    def loadParameters(self):
        with open(os.path.join(self.root, 'data', 'parameters.json')) as f:
            self.parameters = json.loads(
                f.read(), object_pairs_hook=collections.OrderedDict)

    def populateCanvas(self):
        elements = self.parameters
        self.elementComboBox.addItems(elements)
        self.elementComboBox.setCurrentText(self.element)
        self.elementComboBox.currentTextChanged.connect(self.updateElement)

        charges = self.parameters[self.element]
        self.chargeComboBox.addItems(charges)
        self.chargeComboBox.setCurrentText(self.charge)
        self.chargeComboBox.currentTextChanged.connect(self.updateCharge)

        symmetries = ['Oh']
        self.symmetryComboBox.addItems(symmetries)
        self.symmetryComboBox.setCurrentText(self.symmetry)
        self.symmetryComboBox.currentTextChanged.connect(self.updateSymmetry)

        experiments = (self.parameters[self.element][self.charge]
                                      ['experiments'])
        self.experimentComboBox.addItems(experiments)
        self.experimentComboBox.setCurrentText(self.experiment)
        self.experimentComboBox.currentTextChanged.connect(
            self.updateExperiment)

        edges = (self.parameters[self.element][self.charge]
                                ['experiments'][self.experiment])
        self.edgeComboBox.addItems(edges)
        self.edgeComboBox.setCurrentText(self.edge)
        self.edgeComboBox.currentTextChanged.connect(self.updateEdge)

        polarizations = ['iso']
        self.polarizationComboBox.addItems(polarizations)
        self.polarizationComboBox.setCurrentText(self.polarization)
        self.polarizationComboBox.currentTextChanged.connect(
                self.updatePolarization)

        self.temperatureDoubleSpinBox.setValue(self.temperature)

        self.magneticFieldXDoubleSpinBox.setValue(self.magneticFieldX)
        self.magneticFieldYDoubleSpinBox.setValue(self.magneticFieldY)
        self.magneticFieldZDoubleSpinBox.setValue(self.magneticFieldZ)

        self.broadeningGaussianDoubleSpinBox.setValue(self.broadeningGaussian)
        self.broadeningLorentzianDoubleSpinBox.setValue(
                self.broadeningLorentzian)

        self.resultsModel = ListModel(list())
        self.resultsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.resultsView.setModel(self.resultsModel)
        self.resultsView.selectionModel().selectionChanged.connect(
            self.selectedResultsChanged)
        self.resultsView.setAttribute(Qt.WA_MacShowFocusRect, False)

    def activateToolBoxActions(self):
        self.actionSave.triggered.connect(self.createBackendInput)
        self.actionRun.triggered.connect(self.runBackendCalculation)

    def setBackend(self):
        if 'Quanty' in self.backend:
            self.backendInput = None
            self.backendInputFile = 'quanty.lua'
            self.backendSpecFile = 'quanty.spec'
            self.backendRun = Quanty.run

    def createBackendInput(self):
        # Load the template file specific to the requested calculation.
        templateFileName = (self.parameters[self.element][self.charge]
                ['experiments'][self.experiment][self.edge]
                ['template']['Crystal field'])

        templateFile = os.path.join(self.root, 'backends', self.backend,
                'templates', '{0:s}.lua'.format(templateFileName))

        try:
            self.backendInput = open(templateFile, 'r').read()
        except FileNotFoundError:
            print('Template not available for the requested calculation.')
            return

        self.shells = (self.parameters[self.element][self.charge]
                                 ['experiments'][self.experiment]
                                 [self.edge]['shells'])

        for shell in self.shells:
            self.backendInput = self.backendInput.replace(
                    '$NElectrons_{0:s}'.format(shell), str(self.shells[shell]))

        # Get the most recent Hamiltonian data from the model.
        self.hamiltonianModelData = self.hamiltonianModel.getModelData()

        hamiltonians = self.hamiltonianModelData
        for hamiltonian in hamiltonians:
            configurations = hamiltonians[hamiltonian]
            for configuration in configurations:
                if 'ground state' in configuration.lower():
                    suffix = 'gs'
                elif 'intermediate state' in configuration.lower():
                    suffix = 'is'
                elif 'final state' in configuration.lower():
                    suffix = 'fs'
                else:
                    suffix = str()
                parameters = configurations[configuration]
                for parameter in parameters:
                    self.backendInput = self.backendInput.replace(
                        '${0:s}_{1:s}'.format(parameter, suffix),
                        '{0:8.4f}'.format(float(parameters[parameter])))

        self.backendInput = self.backendInput.replace(
                '$T', '{0:8.3f}'.format(
                    self.temperatureDoubleSpinBox.value()))
        self.backendInput = self.backendInput.replace(
                '$Bx', '{0:8.3f}'.format(
                    self.magneticFieldXDoubleSpinBox.value()))
        self.backendInput = self.backendInput.replace(
                '$By', '{0:8.3f}'.format(
                    self.magneticFieldYDoubleSpinBox.value()))
        self.backendInput = self.backendInput.replace(
                '$Bz', '{0:8.3f}'.format(
                    self.magneticFieldZDoubleSpinBox.value()))
        self.backendInput = self.backendInput.replace(
                '$BroadeningGaussian', '{0:8.2f}'.format(
                    self.broadeningGaussianDoubleSpinBox.value()))
        self.backendInput = self.backendInput.replace(
                '$BroadeningLorentzian', '{0:8.2f}'.format(
                    self.broadeningLorentzianDoubleSpinBox.value()))

        with open(self.backendInputFile, 'w') as f:
            f.write(self.backendInput)

    def runBackendCalculation(self):
        self.createBackendInput()

        self.backendRun(self.backendInputFile)
        backendSpec = np.loadtxt(self.backendSpecFile, skiprows=5)

        # Load the data to be plotted.
        id = len(self.resultsModel._data) + 1
        label = '#{:d} - {:s}{:s} | {:s} | {:s} | {:s}'.format(
            id, self.element, self.charge, self.symmetry,
            self.experiment, self.edge)

        # Plot the spectrum.
        self.plotWidget.clear()
        self.plotWidget.plot(backendSpec[:, 0], -backendSpec[:, 2], label[:3])

        # Store the simulation details.
        self.resultsModel.appendItem((label, backendSpec))

        # Remove generated files.
        os.remove(self.backendInputFile)
        os.remove(self.backendSpecFile)

    def selectedHamiltonianTermChanged(self):
        currentIndex = self.hamiltonianView.selectionModel().currentIndex()
        self.hamiltonianParametersView.setRootIndex(currentIndex)

    def selectedResultsChanged(self):
        selectedIndexes = self.resultsView.selectionModel().selectedIndexes()
        self.plotWidget.clear()
        for index in selectedIndexes:
            label, spectrum = self.resultsModel.getIndexData(index)
            self.plotWidget.plot(spectrum[:, 0], -spectrum[:, 2], label[:3])

    def updateElement(self):
        self.element = self.elementComboBox.currentText()
        self.updateCharge()

    def updateCharge(self):
        charges = self.parameters[self.element]
        self.chargeComboBox.updateItems(charges)
        self.charge = self.chargeComboBox.currentText()
        self.updateExperiment()

    def updateSymmetry(self):
        symmetries = ['Oh']
        self.symmetryComboBox.updateItems(symmetries)
        self.symmetry = self.symmetryComboBox.currentText()
        self.updateHamiltonianModelData()

    def updateExperiment(self):
        experiments = (self.parameters[self.element][self.charge]
                                      ['experiments'])
        self.experimentComboBox.updateItems(experiments)
        self.experiment = self.experimentComboBox.currentText()
        self.updateEdge()

    def updateEdge(self):
        edges = (self.parameters[self.element][self.charge]
                                ['experiments'][self.experiment])
        self.edgeComboBox.updateItems(edges)
        self.edge = self.edgeComboBox.currentText()
        self.updatePolarization()

    def updatePolarization(self):
        polarizations = ['iso']
        self.polarizationComboBox.updateItems(polarizations)
        self.polarization = self.polarizationComboBox.currentText()
        self.updateHamiltonianModelData()

    def updateHamiltonianModelData(self):
        configurations = (self.parameters[self.element][self.charge]
                                         ['experiments'][self.experiment]
                                         [self.edge]['configurations'])

        hamiltonians = (self.parameters[self.element][self.charge]
                                       ['hamiltonians'])

        for hamiltonian in hamiltonians:
            self.hamiltonianModelData[hamiltonian] = collections.OrderedDict()

            if 'Crystal field' in hamiltonian:
                parameters = hamiltonians[hamiltonian][self.symmetry]
            else:
                parameters = hamiltonians[hamiltonian]

            for configuration in configurations:
                label = '{0} ({1})'.format(
                    configuration.capitalize(), configurations[configuration])

                self.hamiltonianModelData[hamiltonian][label] = (
                    parameters[configurations[configuration]])

        # Create the Hamiltonian model.
        self.hamiltonianModel = TreeModel(
            header=['parameter', 'value', 'min', 'max'],
            data=self.hamiltonianModelData)

        # Assign the Hamiltonian model to the Hamiltonian view.
        self.hamiltonianView.setModel(self.hamiltonianModel)
        self.hamiltonianView.selectionModel().setCurrentIndex(
            self.hamiltonianModel.index(0, 0), QItemSelectionModel.Select)
        currentIndex = self.hamiltonianView.selectionModel().currentIndex()
        self.hamiltonianView.selectionModel().selectionChanged.connect(
            self.selectedHamiltonianTermChanged)
        self.hamiltonianView.setAttribute(Qt.WA_MacShowFocusRect, False)

        # Assign the Hamiltonian model to the Hamiltonian parameters view, and
        # set some properties.
        self.hamiltonianParametersView.setModel(self.hamiltonianModel)
        self.hamiltonianParametersView.expandAll()
        self.hamiltonianParametersView.resizeAllColumns()
        self.hamiltonianParametersView.setRootIndex(currentIndex)
        self.hamiltonianParametersView.setAttribute(Qt.WA_MacShowFocusRect, False)

    # def keyPressEvent(self, press):
        # if press.key() == Qt.Key_Escape:
            # sys.exit()


def main():
    import os
    import sys

    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtWidgets import QApplication

    from .canvas import MainWindow

    app = QApplication(sys.argv)
    # app.setStyle('Windows')
    # app.setStyle('Fusion')
    window = MainWindow()
    window.setWindowTitle('CRiSPy')
    window.show()

    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
