# coding: utf-8

import os
import re
import sys
import json
import pprint
import random
import string
import subprocess
import collections
import numpy as np

from PyQt5.QtCore import QItemSelectionModel, Qt
from PyQt5.QtWidgets import (QComboBox, QDockWidget, QListView, QMainWindow,
        QPushButton, QStatusBar, QVBoxLayout, QWidget)

from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg
        as FigureCanvas, NavigationToolbar2QT as NavigationToolBar)
from matplotlib.figure import Figure

from crispy.gui.treemodel import TreeNode, TreeModel, TreeView


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

    defaultAttributes = {'element': 'Ni',
                         'charge': '2+',
                         'experiment': 'XAS',
                         'edge': 'L2,3',
                         'symmetry': 'Oh',
                         'parameters': None,
                         'data': collections.OrderedDict()}

    def __init__(self):
        super(MainWindow, self).__init__()
        self.__dict__.update(self.defaultAttributes)

        self.loadParameters()

        self.resize(920, 580)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.createToolBar()
        self.createHamiltonianWidget()
        self.createParametersWidget()
        self.createPlotWidget()
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

    def createPlotWidget(self):
        # Construct the figure, and assign it to the canvas.
        self.fig = Figure(dpi=100)
        self.fig.patch.set_alpha(0.0)
        self.canvas = FigureCanvas(self.fig)

        # Construct the toolbar.
        # self.toolBar = NavigationToolBar(self.canvas, self)

        # Construct the run button.
        self.runButton = QPushButton('Run')
        self.runButton.setFixedWidth(80)
        self.runButton.clicked.connect(self.runCalculation)

        # Set the layout.
        layout = QVBoxLayout(self.centralWidget)
        # layout.addWidget(self.toolBar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.runButton)
        self.centralWidget.setLayout(layout)

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
        inputFile = open('input.lua', 'w')
        inputFile.write(template)
        inputFile.close()

        # Run Quanty.
        try:
            subprocess.check_output(['Quanty', 'input.lua'])
        except subprocess.CalledProcessError:
            return

        # Plot the calculated spectrum.
        x, y1, y2 = np.loadtxt('spectrum.dat', unpack=True, skiprows=11)

        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.ax.patch.set_alpha(0.0)

        self.ax.plot(x, -y2, '-')
        self.ax.grid(True)
        self.ax.set_title(
                '{0:s} {1:s} simulation for {2:s}{3:s}'.format(
                self.experiment, self.edge, self.element, self.charge))
        self.ax.set_xlabel('Energy (eV)')
        self.ax.yaxis.set_ticklabels([])

        self.canvas.draw()

    def selectedHamiltonianTermChanged(self):
        currentIndex = self.hamiltonianView.selectionModel().currentIndex()
        self.parametersView.setRootIndex(currentIndex)

    def updateElement(self):
        self.element = self.elementsComboBox.currentText()
        self.updateCharge()

    def updateCharge(self):
        charges = self.parameters[self.element]
        self.charge = self.chargesComboBox.currentText()
        self.chargesComboBox.updateItems(charges)
        self.updateExperiment()

    def updateExperiment(self):
        self.experiment = self.experimentsComboBox.currentText()
        self.updateEdge()

    def updateEdge(self):
        edges = self.parameters[self.element][self.charge][self.experiment]
        self.edge = self.edgesComboBox.currentText()
        self.edgesComboBox.updateItems(edges)
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
