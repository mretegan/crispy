# coding: utf-8

import collections
import copy
import json
import numpy as np
import os
import shutil
import subprocess

from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtWidgets import QAbstractItemView, QDockWidget, QFileDialog
from PyQt5.uic import loadUi

from .models.treemodel import TreeModel
from .models.listmodel import ListModel
from ..resources import resourceFileName

from pprint import pprint as print


class QuantyDockWidget(QDockWidget):

    _defaults = {
        'element': 'Ni',
        'charge': '2+',
        'symmetry': 'Oh',
        'model': 'Crystal field (CF)',
        'experiment': 'XAS',
        'edge': 'L2,3 (2p)',
        'temperature': None,
        'energies': None,
        'configurations': None,
        'shells': None,
        'hamiltonian': None,
        'label': None,
        'spectrum': None,
        'templateName': None,
        'baseName': None,
        'input': None,
        'inputName': None,
        'command': None,
        }

    def __init__(self):
        super(QuantyDockWidget, self).__init__()
        self.__dict__.update(self._defaults)

        # Load the external .ui file for the widget.
        path = resourceFileName(os.path.join(
            'gui', 'uis', 'quanty.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')

        # Load the external parameters.
        path = resourceFileName(os.path.join(
            'modules', 'quanty', 'parameters', 'ui.json'))

        with open(path) as p:
            self.uiParameters = json.loads(
                p.read(), object_pairs_hook=collections.OrderedDict)

        path = resourceFileName(os.path.join(
            'modules', 'quanty', 'parameters', 'hamiltonian.json'))

        with open(path) as p:
            self.hamiltonianParameters = json.loads(
                p.read(), object_pairs_hook=collections.OrderedDict)

        self.setUiParameters()
        self.createActions()

    def loadSimulationParameters(self, simulation):
        """Load parameters from a dictionary."""
        for key in simulation:
            self.__dict__[key] = copy.deepcopy(simulation[key])

    def setUiParameters(self):
        # Set the values for the combo boxes.
        elements = self.uiParameters
        element = self.elementComboBox.updateItems(elements, self.element)

        charges = elements[element]
        charge = self.chargeComboBox.updateItems(charges, self.charge)

        symmetries = charges[charge]
        symmetry = self.symmetryComboBox.updateItems(
            symmetries, self.symmetry)

        models = symmetries[symmetry]
        model = self.modelComboBox.updateItems(models, self.model)

        experiments = models[model]
        experiment = self.experimentComboBox.updateItems(
            experiments, self.experiment)

        edges = experiments[experiment]
        edge = self.edgeComboBox.updateItems(edges, self.edge)

        # Set the temperature spin box.
        if self.temperature:
            self.temperatureDoubleSpinBox.setValue(self.temperature)

        # Set the energies group boxes.
        parameters = edges[edge]
        if not self.energies:
            energies = parameters['energies']
        else:
            energies = self.energies

        self.e1GroupBox.setTitle(energies['e1']['label'])
        self.e1MinDoubleSpinBox.setValue(energies['e1']['min'])
        self.e1MaxDoubleSpinBox.setValue(energies['e1']['max'])
        self.e1NPointsDoubleSpinBox.setValue(energies['e1']['npoints'])
        self.e1GammaDoubleSpinBox.setValue(energies['e1']['gamma'])

        if 'RIXS' in self.experiment:
            self.e2GroupBox.setTitle(energies['e2']['label'])
            self.e2MinDoubleSpinBox.setValue(energies['e2']['min'])
            self.e2MaxDoubleSpinBox.setValue(energies['e2']['max'])
            self.e2NPointsDoubleSpinBox.setValue(energies['e2']['npoints'])
            self.e2GammaDoubleSpinBox.setValue(energies['e2']['gamma'])
            self.e2GroupBox.setHidden(False)
        else:
            self.e2GroupBox.setHidden(True)

        # Set the Hamiltonian parameters.
        if not self.hamiltonian:
            configurations = parameters['configurations']

            hamiltonian = collections.OrderedDict()
            terms = self.hamiltonianParameters[element][charge]

            for term in terms:
                if 'Crystal field' not in term and 'Ligand field' not in term:
                    termParameters = terms[term]
                else:
                    term = model
                    termParameters = terms[term][symmetry]

                hamiltonian[term] = collections.OrderedDict()

                for configuration in configurations:
                    label = '{0} CFG ({1})'.format(
                        configuration, configurations[configuration])

                    hamiltonian[term][label] = (
                        termParameters[configurations[configuration]])
        else:
            hamiltonian = self.hamiltonian

        # Create the Hamiltonian model.
        self.hamiltonianModel = TreeModel(
            header=['Parameter', 'Value', 'Scaling'], data=hamiltonian)

        # Assign the Hamiltonian model to the Hamiltonian view.
        self.hamiltonianTermsView.setModel(self.hamiltonianModel)
        self.hamiltonianTermsView.selectionModel().setCurrentIndex(
            self.hamiltonianModel.index(0, 0), QItemSelectionModel.Select)

        # Assign the Hamiltonian model to the Hamiltonian parameters view, and
        # set some properties.
        self.hamiltonianParametersView.setModel(self.hamiltonianModel)
        self.hamiltonianParametersView.expandAll()
        self.hamiltonianParametersView.resizeAllColumnsToContents()
        self.hamiltonianParametersView.setColumnWidth(0, 160)

        index = self.hamiltonianTermsView.selectionModel().currentIndex()
        self.hamiltonianParametersView.setRootIndex(index)
        self.hamiltonianTermsView.selectionModel().selectionChanged.connect(
            self.selectedHamiltonianTermChanged)

        # Create the results model and assign it to the view.
        if not hasattr(self, 'resultsModel'):
            self.resultsModel = ListModel(list())
            self.resultsView.setSelectionMode(
                    QAbstractItemView.ExtendedSelection)
            self.resultsView.setModel(self.resultsModel)
            self.resultsView.selectionModel().selectionChanged.connect(
                self.selectedResultsChanged)

        # Set some of the derived data. This is not related to the UI,
        # but it makes sens to set it here.
        if not self.energies:
            self.energies = parameters['energies']
        if not self.configurations:
            self.configurations = parameters['configurations']
        if not self.shells:
            self.shells = parameters['shells']
        if not self.templateName:
            self.templateName = parameters['template name']

    def updateComboBoxes(self):
        self.element = self.elementComboBox.currentText()
        self.charge = self.chargeComboBox.currentText()
        self.symmetry = self.symmetryComboBox.currentText()
        self.model = self.modelComboBox.currentText()
        self.experiment = self.experimentComboBox.currentText()
        self.edge = self.edgeComboBox.currentText()

        # Reset the rest of the parameters
        for key in self._defaults:
            if not self._defaults[key]:
                self.__dict__[key] = None

        self.setUiParameters()

    def createActions(self):
        self.elementComboBox.currentTextChanged.connect(self.updateComboBoxes)
        self.chargeComboBox.currentTextChanged.connect(self.updateComboBoxes)
        self.symmetryComboBox.currentTextChanged.connect(self.updateComboBoxes)
        self.modelComboBox.currentTextChanged.connect(self.updateComboBoxes)
        self.experimentComboBox.currentTextChanged.connect(
                self.updateComboBoxes)
        self.edgeComboBox.currentTextChanged.connect(self.updateComboBoxes)

        self.savePushButton.clicked.connect(self.saveInput)
        self.runPushButton.beforeExecuting.connect(self.runCalculation)
        self.runPushButton.succeeded.connect(self.processResults)

    def getUiParameters(self):
        self.element = self.elementComboBox.currentText()
        self.charge = self.chargeComboBox.currentText()
        self.symmetry = self.symmetryComboBox.currentText()
        self.model = self.modelComboBox.currentText()
        self.experiment = self.experimentComboBox.currentText()
        self.edge = self.edgeComboBox.currentText()

        self.temperature = self.temperatureDoubleSpinBox.value()

        self.energies['e1']['min'] = self.e1MinDoubleSpinBox.value()
        self.energies['e1']['max'] = self.e1MaxDoubleSpinBox.value()
        self.energies['e1']['npoints'] = int(
            self.e1NPointsDoubleSpinBox.value())
        self.energies['e1']['gamma'] = self.e1GammaDoubleSpinBox.value()

        if 'RIXS' in self.experiment:
            self.energies['e2']['min'] = self.e2MinDoubleSpinBox.value()
            self.energies['e2']['max'] = self.e2MaxDoubleSpinBox.value()
            self.energies['e2']['npoints'] = int(
                    self.e2NPointsDoubleSpinBox.value())
            self.energies['e2']['gamma'] = self.e2GammaDoubleSpinBox.value()

        self.hamiltonian = self.hamiltonianModel.getModelData()

    def saveInput(self):
        # Load the template file specific to the requested calculation.
        path = resourceFileName(
            os.path.join('modules', 'quanty', 'templates',
                         '{0:s}'.format(self.templateName)))

        try:
            with open(path) as p:
                template = p.read()
        except FileNotFoundError:
            print('Could not find template: {0:s}'.format(self.template))
            return

        self.getUiParameters()

        replacements = collections.OrderedDict()

        for shell in self.shells:
            replacements['$NElectrons_{}'.format(shell)] = self.shells[shell]

        replacements['$T'] = self.temperature

        replacements['$Bx'] = '0'
        replacements['$By'] = '0'
        replacements['$Bz'] = '1e-6'

        replacements['$Emin1'] = self.energies['e1']['min']
        replacements['$Emax1'] = self.energies['e1']['max']
        replacements['$NE1'] = self.energies['e1']['npoints']
        replacements['$Gamma1'] = self.energies['e1']['gamma']

        if 'RIXS' in self.experiment:
            replacements['$Emin2'] = self.energies['e2']['min']
            replacements['$Emax2'] = self.energies['e2']['max']
            replacements['$NE2'] = self.energies['e2']['npoints']
            replacements['$Gamma2'] = self.energies['e2']['gamma']

        for term in self.hamiltonian:
            configurations = self.hamiltonian[term]
            for configuration in configurations:
                if 'Starting' in configuration:
                    suffix = 'sc'
                elif 'Intermediate' in configuration:
                    suffix = 'ic'
                elif 'Final' in configuration:
                    suffix = 'fc'
                parameters = configurations[configuration]
                for parameter, value in parameters.items():
                    if isinstance(value, list):
                        value = float(value[0]) * float(value[1])
                    else:
                        value = float(value)
                    key = '${0:s}_{1:s}'.format(parameter, suffix)
                    replacements[key] = '{0:12.6}'.format(value)

        terms = self.hamiltonianModel.getNodesState()
        for term in terms:
            if 'Coulomb' in term:
                termName = 'H_coulomb'
            elif 'Spin-orbit coupling' in term:
                termName = 'H_soc'
            elif 'Crystal field' in term:
                termName = 'H_cf'
            elif 'Ligand field' in term:
                termName = 'H_lf'

            termState = terms[term]
            if termState > 0:
                termState = 1

            replacements['${}_flag'.format(termName)] = termState

        if not self.baseName:
            self.baseName = 'untitled'

        replacements['$baseName'] = self.baseName

        for replacement in replacements:
            template = template.replace(
                replacement, str(replacements[replacement]))

        self.inputName = '{0:s}.lua'.format(self.baseName)

        with open(self.inputName, 'w') as f:
            f.write(template)

        self.input = template

    def saveAsInput(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Quanty Input', '{0:s}.lua'.format(self.baseName),
            'Quanty Input File (*.lua)')

        if path:
            os.chdir(os.path.dirname(path))
            self.baseName = os.path.splitext(os.path.basename(path))[0]
            self.saveInput()

    def runCalculation(self):
        # Determine the location of the executable program.
        self.command = shutil.which('Quanty') or shutil.which('Quanty.exe')

        if self.command is None:
            print('Could not find Quanty in the path.')
            return

        # Write the input file to disk.
        if self.inputName:
            self.saveInput()
        else:
            self.saveAsInput()

        if not self.inputName:
            return

        self.runPushButton.setCallable(
            subprocess.run, [self.command, self.inputName])

    def processResults(self):
        spectrumName = '{0:s}.spec'.format(self.baseName)
        spectrum = np.loadtxt(spectrumName, skiprows=5)

        if 'RIXS' in self.experiment:
            self.spectrum = -spectrum[:, 2::2]
        else:
            self.spectrum = spectrum[:, ::2]
            self.spectrum[:, 1] = -self.spectrum[:, 1]

        # Remove the spectrum file
        os.remove(spectrumName)

        index = self.resultsModel.size() + 1
        self.label = '#{:d} - {:s}{:s} | {:s} | {:s} | {:s}'.format(
            index, self.element, self.charge, self.symmetry, self.experiment,
            self.edge)

        simulation = collections.OrderedDict()
        for key in self._defaults:
            simulation[key] = copy.deepcopy(self.__dict__[key])

        # Store the simulation details.
        self.resultsModel.appendItem(simulation)

        # Update the selected item in the results view.
        self.resultsView.selectionModel().clearSelection()
        index = self.resultsModel.index(self.resultsModel.size() - 1)
        self.resultsView.selectionModel().select(
            index, QItemSelectionModel.Select)

    def plotResults(self):
        if 'RIXS' in self.experiment:
            self.parent().plotWidget.setGraphXLabel('Incident Energy (eV)')
            self.parent().plotWidget.setGraphYLabel('Energy Transfer (eV)')

            colormap = {'name': 'viridis', 'normalization': 'linear',
                                'autoscale': True, 'vmin': 0.0, 'vmax': 1.0}
            self.parent().plotWidget.setDefaultColormap(colormap)

            xMin = self.energies['e1']['min']
            xMax = self.energies['e1']['max']
            xPoints = self.energies['e1']['npoints']
            xScale = (xMax - xMin) / xPoints

            yMin = self.energies['e2']['min']
            yMax = self.energies['e2']['max']
            yPoints = self.energies['e2']['npoints']
            yScale = (yMax - yMin) / yPoints

            self.parent().plotWidget.addImage(
                self.spectrum, origin=(xMin, yMin), scale=(xScale, yScale))
        else:
            self.parent().plotWidget.setGraphXLabel('Absorption Energy (eV)')
            self.parent().plotWidget.setGraphYLabel(
                'Absorption cross section (a.u.)')

            self.parent().plotWidget.addCurve(
                self.spectrum[:, 0], self.spectrum[:, 1], legend=self.label)

    def selectedHamiltonianTermChanged(self):
        index = self.hamiltonianTermsView.selectionModel().currentIndex()
        self.hamiltonianParametersView.setRootIndex(index)

    def selectedResultsChanged(self):
        self.parent().plotWidget.clear()
        selectedIndexes = self.resultsView.selectionModel().selectedIndexes()
        for index in selectedIndexes:
            simulation = self.resultsModel.getIndexData(index)
            self.loadSimulationParameters(simulation)
            self.setUiParameters()
            self.plotResults()


def main():
    pass

if __name__ == '__main__':
    main()
