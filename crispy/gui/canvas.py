# coding: utf-8

import collections
import json
import numpy as np
import os
import sys

from PyQt5.QtCore import QItemSelectionModel, QEvent, Qt
from PyQt5.QtWidgets import (
    QAbstractItemView, QDoubleSpinBox, QLabel,
    QMainWindow, QGroupBox, QHBoxLayout, QTabWidget)
from PyQt5 import uic

from .models.treemodel import TreeModel
from .models.listmodel import ListModel
from .widgets.plotwidget import PlotWidget
from ..backends import Quanty
from ..resources import resource_filename


class MainWindow(QMainWindow):

    _defaults = {'element': 'Ni',
                 'charge': '2+',
                 'symmetry': 'Oh',
                 'theoreticalModel': 'Crystal field (CF)',
                 'experiment': 'XAS',
                 'edge': 'L2,3 (2p)',
                 'temperature': 1.0,
                 'magneticField': [0.0, 0.0, 0.0],
                 'broadeningGaussian': 0.5,
                 'broadeningLorentzian': 0.5,
                 'backend': 'Quanty',
                 'hamiltonianModelData': collections.OrderedDict()}

    def __init__(self):
        super(MainWindow, self).__init__()
        self.__dict__.update(self._defaults)
        uic.loadUi(resource_filename('gui/uis/canvas.ui'), baseinstance=self,
                package='crispy.gui')

        self.loadParameters()
        self.updateHamiltonianModelData()

        self.populateCanvas()
        self.activateToolBoxActions()
        self.statusBar().showMessage('Ready')

        self.setBackend()

    def loadParameters(self):
        with open(resource_filename('parameters.json')) as f:
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

        symmetries = (self.parameters[self.element][self.charge]
                ['experiments'][self.experiment][self.edge]
                ['templates'][self.theoreticalModel])
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

        theoreticalModels = (self.parameters[self.element][self.charge]
                ['experiments'][self.experiment][self.edge]
                ['templates'])
        self.theoreticalModelComboBox.addItems(theoreticalModels)
        self.theoreticalModelComboBox.setCurrentText(self.theoreticalModel)
        self.theoreticalModelComboBox.currentTextChanged.connect(
                self.updateTheoreticalModel)

        self.temperatureDoubleSpinBox.setValue(self.temperature)

        self.magneticFieldXDoubleSpinBox.setValue(self.magneticField[0])
        self.magneticFieldYDoubleSpinBox.setValue(self.magneticField[1])
        self.magneticFieldZDoubleSpinBox.setValue(self.magneticField[2])

        self.broadeningGaussianDoubleSpinBox.setValue(self.broadeningGaussian)
        self.broadeningLorentzianDoubleSpinBox.setValue(
                self.broadeningLorentzian)

        self.resultsModel = ListModel(list())
        self.resultsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.resultsView.setModel(self.resultsModel)
        self.resultsView.selectionModel().selectionChanged.connect(
            self.selectedResultsChanged)
        self.resultsView.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.resultsView.viewport().installEventFilter(self)

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
                ['templates'][self.theoreticalModel][self.symmetry])

        templateFile = resource_filename(os.path.join('backends',
            self.backend.lower(), 'templates',
            '{0:s}.lua'.format(templateFileName)))

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

        hamiltonian = self.hamiltonianModelData
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

            if hamiltonianTermState == 0:
                termState = 0
            else:
                termState = 1

            self.backendInput = self.backendInput.replace(
                    '${0:s}'.format(termName), '{0:2.1f}'.format(termState))

        with open(self.backendInputFile, 'w') as f:
            f.write(self.backendInput)

    def runBackendCalculation(self):
        self.createBackendInput()

        self.backendRun(self.backendInputFile)
        backendSpec = np.loadtxt(self.backendSpecFile, skiprows=5)

        # Load the data to be plotted.
        id = len(self.resultsModel._data) + 1
        label = '#{:d} - {:s}{:s} | {:s} | {:s} | {:s} | {:s}'.format(
            id, self.element, self.charge, self.symmetry,
            self.experiment, self.edge, self.theoreticalModel)

        # Plot the spectrum.
        self.plotWidget.clear()
        self.plotWidget.plot(backendSpec[:, 0], -backendSpec[:, 2], label[:3])

        # Store the simulation details.
        self.resultsModel.appendItem((label, backendSpec))

        # Update the selected item in the results view.
        self.resultsView.selectionModel().clearSelection()
        index = self.resultsModel.index(self.resultsModel.rowCount()-1)
        self.resultsView.selectionModel().select(
                index, QItemSelectionModel.Select)

        # Remove generated files.
        os.remove(self.backendInputFile)
        os.remove(self.backendSpecFile)

    def selectedHamiltonianTermChanged(self):
        currentIndex = self.hamiltonianView.selectionModel().currentIndex()
        self.hamiltonianParametersView.setRootIndex(currentIndex)

    def selectedResultsChanged(self):
        self.plotWidget.clear()
        selectedIndexes = self.resultsView.selectionModel().selectedIndexes()
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
        self.updateSymmetry()

    def updateSymmetry(self):
        symmetries = (self.parameters[self.element][self.charge]
                ['experiments'][self.experiment][self.edge]
                ['templates'][self.theoreticalModel])
        self.symmetryComboBox.updateItems(symmetries)
        self.symmetry = self.symmetryComboBox.currentText()
        self.updateExperiment()

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
        self.updateTheoreticalModel()

    def updateTheoreticalModel(self):
        theoreticalModels = (self.parameters[self.element][self.charge]
                ['experiments'][self.experiment][self.edge]
                ['templates'])
        self.theoreticalModelComboBox.updateItems(theoreticalModels)
        self.theoreticalModel = self.theoreticalModelComboBox.currentText()
        self.updateHamiltonianModelData()

    def updateHamiltonianModelData(self):
        configurations = (self.parameters[self.element][self.charge]
                ['experiments'][self.experiment][self.edge]['configurations'])

        hamiltonian = (self.parameters[self.element][self.charge]
                                       ['Hamiltonian'])

        self.hamiltonianModelData = collections.OrderedDict()
        for hamiltonianTerm in hamiltonian:

            if 'field' not in hamiltonianTerm:
                parameters = hamiltonian[hamiltonianTerm]
            else:
                hamiltonianTerm = self.theoreticalModel
                parameters = hamiltonian[hamiltonianTerm][self.symmetry]

            self.hamiltonianModelData[hamiltonianTerm] = (
                    collections.OrderedDict())

            for configuration in configurations:
                label = '{0} ({1})'.format(
                    configuration.capitalize(), configurations[configuration])

                self.hamiltonianModelData[hamiltonianTerm][label] = (
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
        self.hamiltonianView.setAttribute(
                Qt.WA_MacShowFocusRect, False)

        # Assign the Hamiltonian model to the Hamiltonian parameters view, and
        # set some properties.
        self.hamiltonianParametersView.setModel(self.hamiltonianModel)
        self.hamiltonianParametersView.expandAll()
        self.hamiltonianParametersView.resizeColumnToContents(0)
        self.hamiltonianParametersView.resizeColumnToContents(1)
        self.hamiltonianParametersView.setRootIndex(currentIndex)
        self.hamiltonianParametersView.setAttribute(
                Qt.WA_MacShowFocusRect, False)
        self.hamiltonianParametersView.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.MouseButtonPress and
            event.button() == Qt.RightButton and
            (source is self.hamiltonianParametersView.viewport() or
                source is self.resultsView.viewport())):
            return True
        else:
            return super(MainWindow, self).eventFilter(source, event)

def main():
    import os
    import sys

    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # app.setStyle('Windows')
    # app.setStyle('Fusion')
    window = MainWindow()
    window.setWindowTitle('')
    window.show()

    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
