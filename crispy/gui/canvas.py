# coding: utf-8

import collections
import json
import numpy as np
import os
import sys

from PyQt5.QtCore import QItemSelectionModel, Qt
from PyQt5.QtWidgets import (QAbstractItemView,
    QComboBox, QDockWidget, QListView, QMainWindow, QPushButton, QStatusBar,
    QVBoxLayout, QWidget)

from crispy.gui.treemodel import TreeModel, TreeView
from crispy.gui.listmodel import ListModel
from crispy.gui.spectrum import Spectrum
from crispy.backends.quanty.quanty import Quanty


class defaultdict(collections.defaultdict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


class ToolBarComboBox(QComboBox):
    def __init__(self, fixedWidth=70, *args, **kwargs):
        super(ToolBarComboBox, self).__init__(*args, **kwargs)
        self.setFixedWidth(fixedWidth)

    def updateItems(self, items):
        currentText = self.currentText()
        self.blockSignals(True)
        self.clear()
        self.addItems(items)
        try:
            self.setCurrentText(currentText)
        except ValueError:
            self.setCurrentIndex(0)
        self.blockSignals(False)


class MainWindow(QMainWindow):

    _defaults = {'element': 'Ni',
                 'charge': '2+',
                 'experiment': 'XAS',
                 'edge': 'L2,3',
                 'symmetry': 'Oh',
                 'parameters': None,
                 'data': collections.OrderedDict()}

    def __init__(self):
        super(MainWindow, self).__init__()
        self.__dict__.update(self._defaults)

        self.loadParameters()

        self.resize(1260, 680)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.createToolBar()
        self.createHamiltonianWidget()
        self.createParametersWidget()
        self.createCentralWidget()
        self.createResultsWidget()
        self.createStatusBar()

        self.updateHamiltonianData()

    def loadParameters(self):
        parametersFile = os.path.join(
            os.getenv('CRISPY_ROOT'), 'data', 'parameters.json')
        with open(parametersFile) as jsonFile:
            self.parameters = json.loads(
                jsonFile.read(), object_pairs_hook=collections.OrderedDict)

    def createToolBar(self):
        self.toolBar = self.addToolBar('User selections')

        elements = self.parameters
        self.elementsComboBox = ToolBarComboBox()
        self.elementsComboBox.addItems(elements)
        self.elementsComboBox.setCurrentText(self.element)
        self.elementsComboBox.currentTextChanged.connect(self.updateElement)
        self.toolBar.addWidget(self.elementsComboBox)

        charges = self.parameters[self.element]
        self.chargesComboBox = ToolBarComboBox()
        self.chargesComboBox.addItems(charges)
        self.chargesComboBox.setCurrentText(self.charge)
        self.chargesComboBox.currentTextChanged.connect(self.updateCharge)
        self.toolBar.addWidget(self.chargesComboBox)

        symmetries = ['Oh']
        self.symmetriesComboBox = ToolBarComboBox()
        self.symmetriesComboBox.addItems(symmetries)
        self.symmetriesComboBox.setCurrentText(self.experiment)
        self.symmetriesComboBox.currentTextChanged.connect(self.updateSymmetry)
        self.toolBar.addWidget(self.symmetriesComboBox)

        experiments = ['XAS']
        self.experimentsComboBox = ToolBarComboBox()
        self.experimentsComboBox.addItems(experiments)
        self.experimentsComboBox.setCurrentText(self.experiment)
        self.experimentsComboBox.currentTextChanged.connect(
            self.updateExperiment)
        self.toolBar.addWidget(self.experimentsComboBox)

        edges = self.parameters[self.element][self.charge][self.experiment]
        self.edgesComboBox = ToolBarComboBox()
        self.edgesComboBox.addItems(edges)
        self.edgesComboBox.setCurrentText(self.edge)
        self.edgesComboBox.currentTextChanged.connect(self.updateEdge)
        self.toolBar.addWidget(self.edgesComboBox)

    def createStatusBar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('Ready')

    def createHamiltonianWidget(self):
        self.hamiltonianDockWidget = QDockWidget('Hamiltonian', self)
        self.hamiltonianDockWidget.setFeatures(QDockWidget.DockWidgetMovable)

        self.hamiltonianView = QListView()

        self.hamiltonianDockWidget.setWidget(self.hamiltonianView)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.hamiltonianDockWidget)

    def createParametersWidget(self):
        self.parametersDockWidget = QDockWidget('Parameters', self)
        self.parametersDockWidget.setFeatures(QDockWidget.DockWidgetMovable)

        self.parametersView = TreeView()

        self.parametersDockWidget.setWidget(self.parametersView)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.parametersDockWidget)

    def createCentralWidget(self):
        # Construct the spectrum.
        self.spectrum = Spectrum()

        # Construct the run button.
        self.runButton = QPushButton('Run')
        self.runButton.setFixedWidth(80)
        self.runButton.clicked.connect(self.runCalculation)

        # Set the layout.
        layout = QVBoxLayout(self.centralWidget)
        layout.addWidget(self.spectrum.canvas)
        layout.addWidget(self.runButton)
        self.centralWidget.setLayout(layout)

    def createResultsWidget(self):
        self.resultsDockWidget = QDockWidget('Results', self)
        self.resultsDockWidget.setFeatures(QDockWidget.DockWidgetMovable)

        self.resultsModel = ListModel(list())

        self.resultsView = QListView()
        self.resultsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.resultsView.setModel(self.resultsModel)
        self.resultsView.selectionModel().selectionChanged.connect(
            self.selectedResultsChanged)

        self.resultsDockWidget.setWidget(self.resultsView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.resultsDockWidget)

    def runCalculation(self):
        # Get the most recent data from the model.
        self.data = self.hamiltonianModel.getModelData()

        self.backend = 'quanty'
        # Load the template file specific to the requested calculation.
        templateFile = os.path.join(
            os.getenv('CRISPY_ROOT'), 'backends', self.backend, 'templates',
            self.symmetry.lower(), self.experiment.lower(),
            ''.join(self.shells.keys()), 'crystal_field', 'template')

        try:
            template = open(templateFile, 'r').read()
        except IOError:
            print('Template file not available for the requested'
                  'calculation type.')
            return

        for shellLabel, shellElectrons in self.shells.items():
            template = template.replace('$NElectrons_{0:s}'.format(
                shellLabel), str(shellElectrons))

        for hamiltonianLabel, hamiltonianTerms in self.data.items():
            for stateLabel, stateParameters in hamiltonianTerms.items():
                if 'initial' in stateLabel.lower():
                    suffix = 'i'
                elif 'final' in stateLabel.lower():
                    suffix = 'f'
                else:
                    suffix = ''
                for parameterLabel, parameterValue in stateParameters.items():
                    template = template.replace(
                        '${0:s}_{1:s}'.format(parameterLabel, suffix),
                        '{0:8.4f}'.format(float(parameterValue)))

        # Here something regarding the spectrum parameters.

        # Write the input to file.
        inputFile = 'input.inp'
        with open(inputFile, 'w') as f:
            f.write(template)

        # Run Quanty.
        backend = Quanty()
        backend.run(inputFile)

        # Load the data to be plotted.
        label = '{0:s}{1:s} | {2:s} | {3:s} | {4:s} | isotropic'.format(
            self.element, self.charge, self.symmetry, self.experiment,
            self.edge)
        spectrum = np.loadtxt('spectrum.dat', skiprows=5)

        # Plot the spectrum.
        self.spectrum.clear()
        self.spectrum.plot(spectrum[:, 0], -spectrum[:, 2],label)

        # Store the simulation details.
        self.resultsModel.appendItem((label, spectrum, template))

        # Remove generated files.
        os.remove(inputFile)
        os.remove('spectrum.dat')

    def selectedHamiltonianTermChanged(self):
        currentIndex = self.hamiltonianView.selectionModel().currentIndex()
        self.parametersView.setRootIndex(currentIndex)

    def selectedResultsChanged(self):
        selectedIndexes = self.resultsView.selectionModel().selectedIndexes()
        self.spectrum.clear()
        for index in selectedIndexes:
            label, spectrum, _ = self.resultsModel.getIndexData(index)
            self.spectrum.plot(spectrum[:, 0], -spectrum[:, 2], label)

    def updateElement(self):
        self.element = self.elementsComboBox.currentText()
        self.updateCharge()

    def updateCharge(self):
        charges = self.parameters[self.element]
        self.chargesComboBox.updateItems(charges)
        self.charge = self.chargesComboBox.currentText()
        self.updateExperiment()

    def updateExperiment(self):
        self.experiment = self.experimentsComboBox.currentText()
        self.updateEdge()

    def updateEdge(self):
        edges = self.parameters[self.element][self.charge][self.experiment]
        self.edgesComboBox.updateItems(edges)
        self.edge = self.edgesComboBox.currentText()
        self.updateHamiltonianData()

    def updateSymmetry(self):
        self.symmetry = self.symmetriesComboBox.currentText()
        self.updateHamiltonianData()

    def updateHamiltonianData(self):
        self.states = (self.parameters[self.element]
                       [self.charge][self.experiment][self.edge]['states'])

        self.shells = (self.parameters[self.element]
                       [self.charge][self.experiment][self.edge]['shells'])

        hamiltonians = (['Coulomb', 'Spin-orbit coupling', 'Crystal field', 'Magnetic field'])

        for hamiltonian in hamiltonians:
            self.data[hamiltonian] = collections.OrderedDict()
            for (stateLabel, stateConfiguration) in self.states.items():
                stateLabel = '{0} state ({1})'.format(
                    stateLabel.capitalize(), stateConfiguration)
                if 'Crystal field' in hamiltonian:
                    stateParameters = (self.parameters[self.element]
                                       [self.charge][hamiltonian]
                                       [stateConfiguration][self.symmetry])
                else:
                    stateParameters = (self.parameters[self.element]
                                       [self.charge][hamiltonian]
                                       [stateConfiguration])
                self.data[hamiltonian][stateLabel] = stateParameters

        # Create the Hamiltonian model.
        self.hamiltonianModel = TreeModel(
            header=['parameter', 'value', 'min', 'max'],
            data=self.data)

        # Assign the Hamiltonian model to the Hamiltonian view.
        self.hamiltonianView.setModel(self.hamiltonianModel)
        self.hamiltonianView.selectionModel().setCurrentIndex(
            self.hamiltonianModel.index(0, 0), QItemSelectionModel.Select)
        currentIndex = self.hamiltonianView.selectionModel().currentIndex()
        self.hamiltonianView.selectionModel().selectionChanged.connect(
            self.selectedHamiltonianTermChanged)

        # Assign the Hamiltonian model to the parameters view, and set
        # some properties.
        self.parametersView.setModel(self.hamiltonianModel)
        self.parametersView.expandAll()
        self.parametersView.resizeAllColumns()
        self.parametersView.setRootIndex(currentIndex)

    def keyPressEvent(self, press):
        if press.key() == Qt.Key_Escape:
            sys.exit()

def main():
    pass

if __name__ == '__main__':
    main()
