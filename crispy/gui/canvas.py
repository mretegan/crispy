# coding: utf-8

import os
import sys
import json
import collections
import numpy as np

from PyQt5.QtCore import QItemSelectionModel, Qt
from PyQt5.QtWidgets import (QComboBox, QDockWidget, QListView, QMainWindow,
        QPushButton, QStatusBar, QVBoxLayout, QWidget)

from crispy.gui.treemodel import TreeModel, TreeView
from crispy.gui.spectrum import Spectrum
from crispy.backends.quanty import Quanty


class ToolBarComboBox(QComboBox):

    def __init__(self, *args, fixedWidth=70, **kwargs):
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

        self.resize(1060, 580)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.createToolBar()
        self.createHamiltonianWidget()
        self.createParametersWidget()
        self.createCentralWidget()
        self.createResultsWidget()
        self.createStatusBar()

        self.updateHamiltonianData()
        self.createToolBarSignals()

    def loadParameters(self):
        parametersFile = os.path.join(os.getenv('CRISPY_ROOT'), 'data',
                'parameters.json')
        with open(parametersFile) as jsonFile:
            self.parameters = json.loads(jsonFile.read(),
                object_pairs_hook=collections.OrderedDict)

    def createToolBar(self):
        self.toolBar = self.addToolBar('User selections')

        elements = self.parameters
        self.elementsComboBox = ToolBarComboBox()
        self.elementsComboBox.addItems(elements)
        self.elementsComboBox.setCurrentText(self.element)
        self.toolBar.addWidget(self.elementsComboBox)

        charges = self.parameters[self.element]
        self.chargesComboBox = ToolBarComboBox()
        self.chargesComboBox.addItems(charges)
        self.chargesComboBox.setCurrentText(self.charge)
        self.toolBar.addWidget(self.chargesComboBox)

        symmetries = ['Oh']
        self.symmetriesComboBox = ToolBarComboBox()
        self.symmetriesComboBox.addItems(symmetries)
        self.symmetriesComboBox.setCurrentText(self.experiment)
        self.toolBar.addWidget(self.symmetriesComboBox)

        experiments = ['XAS']
        self.experimentsComboBox = ToolBarComboBox()
        self.experimentsComboBox.addItems(experiments)
        self.experimentsComboBox.setCurrentText(self.experiment)
        self.toolBar.addWidget(self.experimentsComboBox)

        edges = self.parameters[self.element][self.charge][self.experiment]
        self.edgesComboBox = ToolBarComboBox()
        self.edgesComboBox.addItems(edges)
        self.edgesComboBox.setCurrentText(self.edge)
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

        self.resultsView = TreeView()

        self.resultsDockWidget.setWidget(self.resultsView)
        self.addDockWidget(Qt.RightDockWidgetArea, self.resultsDockWidget)

    def createToolBarSignals(self):
        self.elementsComboBox.currentTextChanged.connect(self.updateElement)
        self.chargesComboBox.currentTextChanged.connect(self.updateCharge)
        self.experimentsComboBox.currentTextChanged.connect(
                self.updateExperiment)
        self.edgesComboBox.currentTextChanged.connect(self.updateEdge)
        self.symmetriesComboBox.currentTextChanged.connect(self.updateSymmetry)

    def runCalculation(self):
        # Get the most recent data from the model.
        self.data = self.hamiltonianModel.getModelData()

        # Load the template file specific to the requested calculation.
        templateFile = os.path.join(os.getenv('CRISPY_ROOT'), 'templates',
                '{0:s}_{1:s}.template'.format(
                    self.experiment.lower(), ''.join(self.shells.keys())))
        try:
            template = open(templateFile, 'r').read()
        except IOError:
            print('Template file not available for the requested calculation '
                'type. Please select another edge.')
            return

        for shellLabel, shellElectrons in self.shells.items():
            template = template.replace('<nelectrons_{0:s}>'.format(
                shellLabel), str(shellElectrons))

        for hamiltonianLabel, hamiltonianTerms in self.data.items():
            for stateLabel, stateParameters in hamiltonianTerms.items():
                if 'initial' in stateLabel.lower():
                    suffix = 'i'
                elif 'final' in stateLabel.lower():
                    suffix = 'f'
                for parameterLabel, parameterValue in stateParameters.items():
                    template = template.replace(
                            '<{0:s}_{1:s}>'.format(parameterLabel, suffix),
                            '{0:8.4f}'.format(float(parameterValue)))

        # Write the input to file.
        inputFile = 'input.lua'
        with open(inputFile, 'w') as luaFile:
            luaFile.write(template)

        # Run Quanty
        quanty = Quanty()
        quanty.run(inputFile)

        # Load the data to be plotted.
        x, y1, y2 = np.loadtxt('spectrum.dat', unpack=True, skiprows=11)
        title = '{0:s} {1:s} simulation for {2:s}{3:s}'.format(
                self.experiment, self.edge, self.element, self.charge)

        # Plot the spectrum.
        self.spectrum.plot(x, -y2, title)

    def selectedHamiltonianTermChanged(self):
        currentIndex = self.hamiltonianView.selectionModel().currentIndex()
        self.parametersView.setRootIndex(currentIndex)

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

        hamiltonians = (['Coulomb', 'Spin-orbit coupling',
            'Crystal field'])

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
                            [self.charge][hamiltonian][stateConfiguration])
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
