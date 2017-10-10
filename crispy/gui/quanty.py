# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

from __future__ import absolute_import, division, unicode_literals

__authors__ = ['Marius Retegan']
__license__ = 'MIT'
__date__ = '10/10/2017'


import collections
import copy
import datetime
import glob
import json
import numpy as np
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
import subprocess
import sys
import uuid

from PyQt5.QtCore import QItemSelectionModel, QProcess, Qt, QPoint
from PyQt5.QtGui import QIcon, QCursor, QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import (
    QAbstractItemView, QDockWidget, QFileDialog, QAction, QMenu,
    QWidget)
from PyQt5.uic import loadUi
from silx.resources import resource_filename as resourceFileName

from .models.treemodel import TreeModel
from .models.listmodel import ListModel
from ..utils.broaden import broaden


class OrderedDict(collections.OrderedDict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


class QuantyCalculation(object):

    MIN_BROADENING = 0.1

    _defaults = {
        'element': 'Ni',
        'charge': '2+',
        'symmetry': 'Oh',
        'experiment': 'XAS',
        'edge': 'L2,3 (2p)',
        'temperature': 10.,
        'magneticFieldX': 0.,
        'magneticFieldY': 0.,
        'magneticFieldZ': 0.,
        'nPsisAuto': 1,
        'baseName': 'untitled',
        '_uuid': None,
        'spectra': None,
        '_spectra': None,
        'startingTime': None,
        'endingTime': None,
    }

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        self.__dict__.update(kwargs)

        path = resourceFileName(
            'crispy:' + os.path.join('modules', 'quanty', 'parameters',
                                     'parameters.json'))

        with open(path) as p:
            tree = json.loads(
                p.read(), object_pairs_hook=collections.OrderedDict)

        branch = tree['elements']
        self._elements = list(branch)
        if self.element not in self._elements:
            self.element = self._elements[0]

        branch = branch[self.element]['charges']
        self._charges = list(branch)
        if self.charge not in self._charges:
            self.charge = self._charges[0]

        branch = branch[self.charge]['symmetries']
        self._symmetries = list(branch)
        if self.symmetry not in self._symmetries:
            self.symmetry = self._symmetries[0]

        branch = branch[self.symmetry]['experiments']
        self._experiments = list(branch)
        if self.experiment not in self._experiments:
            self.experiment = self._experiments[0]

        branch = branch[self.experiment]['edges']
        self._edges = list(branch)
        if self.edge not in self._edges:
            self.edge = self._edges[0]

        branch = branch[self.edge]

        self._templateName = branch['template name']

        self._configurations = branch['configurations']
        self.nPsis = branch['number of states']
        try:
            self.monoElectronicRadialME = (branch[
                'monoelectronic radial matrix elements'])
        except KeyError:
            self.monoElectronicRadialME = None

        self._e1Label = branch['energies'][0][0]
        self.e1Min = branch['energies'][0][1]
        self.e1Max = branch['energies'][0][2]
        self.e1NPoints = branch['energies'][0][3]
        self.e1Energy = branch['energies'][0][4]
        self.e1Lorentzian = branch['energies'][0][5]
        self.e1Gaussian = branch['energies'][0][6]

        self._e1LorentzianMin = min(self.MIN_BROADENING, self.e1Lorentzian)

        if 'RIXS' in self.experiment:
            self._e2Label = branch['energies'][1][0]
            self.e2Min = branch['energies'][1][1]
            self.e2Max = branch['energies'][1][2]
            self.e2NPoints = branch['energies'][1][3]
            self.e2Energy = branch['energies'][1][4]
            self.e2Lorentzian = branch['energies'][1][5]
            self.e2Gaussian = branch['energies'][1][6]

            self._e2LorentzianMin = min(self.MIN_BROADENING, self.e2Lorentzian)

        self.hamiltonianData = OrderedDict()
        self.hamiltonianState = OrderedDict()

        branch = tree['elements'][self.element]['charges'][self.charge]

        for label, configuration in self._configurations:
            label = '{} Hamiltonian'.format(label)
            terms = branch['configurations'][configuration]['terms']

            for term in terms:
                if 'Atomic' in term:
                    parameters = terms[term]
                else:
                    try:
                        parameters = terms[term][self.symmetry]
                    except KeyError:
                        continue

                for parameter in parameters:
                    if parameter[0] in ('F', 'G'):
                        scaling = 0.8
                    else:
                        scaling = 1.0
                    self.hamiltonianData[term][label][parameter] = (
                        parameters[parameter], scaling)

                if 'Atomic' in term or 'Crystal Field' in term:
                    self.hamiltonianState[term] = 2
                else:
                    self.hamiltonianState[term] = 0

    @property
    def spectra(self):
        return self._spectra

    @spectra.setter
    def spectra(self, files):
        self._spectra = OrderedDict()

        for f in files:
            try:
                spectrum = np.loadtxt(f, skiprows=5)
            except FileNotFoundError:
                continue

            if '_iso.spec' in f:
                key = 'Isotropic'
            elif '_cd.spec' in f:
                key = 'Circular Dichroism'

            if 'RIXS' in self.experiment:
                self._spectra[key] = -spectrum[:, 2::2]
            else:
                self._spectra[key] = -spectrum[:, 2::2][:, 0]

            # os.remove(f)

    def saveInput(self):
        templatePath = resourceFileName(
            'crispy:' + os.path.join('modules', 'quanty', 'templates',
                                     '{}'.format(self._templateName)))

        with open(templatePath) as p:
            self._template = p.read()

        replacements = collections.OrderedDict()

        subshell = self._configurations[0][1][:2]
        subshell_occupation = self._configurations[0][1][2:]
        replacements['$NElectrons_{}'.format(subshell)] = subshell_occupation

        replacements['$T'] = self.temperature

        replacements['$Bx'] = self.magneticFieldX
        replacements['$By'] = self.magneticFieldY
        replacements['$Bz'] = self.magneticFieldZ

        replacements['$Emin1'] = self.e1Min
        replacements['$Emax1'] = self.e1Max
        replacements['$NE1'] = self.e1NPoints
        replacements['$Gamma1'] = self.e1Lorentzian

        if 'RIXS' in self.experiment:
            # The Lorentzian broadening along the incident axis cannot be
            # changed in the interface, and must therefore be set to the
            # final value before the start of the calculation.
            # replacements['$Gamma1'] = self.e1Lorentzian
            replacements['$Emin2'] = self.e2Min
            replacements['$Emax2'] = self.e2Max
            replacements['$NE2'] = self.e2NPoints
            replacements['$Gamma2'] = self.e2Lorentzian

        replacements['$NPsisAuto'] = self.nPsisAuto
        replacements['$NPsis'] = self.nPsis

        for term in self.hamiltonianData:
            if 'Atomic' in term:
                name = 'H_atomic'
            elif 'Crystal Field' in term:
                name = 'H_cf'
            elif '3d-Ligands Hybridization' in term:
                name = 'H_3d_Ld_hybridization'
            elif '3d-4p Hybridization' in term:
                name = 'H_3d_4p_hybridization'
            elif '4d-Ligands Hybridization' in term:
                name = 'H_4d_Ld_hybridization'
            elif '5d-Ligands Hybridization' in term:
                name = 'H_5d_Ld_hybridization'
            else:
                pass

            configurations = self.hamiltonianData[term]
            for configuration, parameters in configurations.items():
                if 'Initial' in configuration:
                    suffix = 'i'
                elif 'Intermediate' in configuration:
                    suffix = 'm'
                elif 'Final' in configuration:
                    suffix = 'f'
                for parameter, (value, scaling) in parameters.items():
                    # Convert to parameters name from Greek letter.
                    parameter = parameter.replace('ζ', 'zeta')
                    parameter = parameter.replace('Δ', 'Delta')
                    parameter = parameter.replace('σ', 'sigma')
                    parameter = parameter.replace('τ', 'tau')
                    key = '${}_{}_value'.format(parameter, suffix)
                    replacements[key] = '{}'.format(value)
                    key = '${}_{}_scaling'.format(parameter, suffix)
                    replacements[key] = '{}'.format(scaling)

            checkState = self.hamiltonianState[term]
            if checkState > 0:
                checkState = 1

            replacements['${}'.format(name)] = checkState

        if self.monoElectronicRadialME:
            for parameter in self.monoElectronicRadialME:
                value = self.monoElectronicRadialME[parameter]
                replacements['${}'.format(parameter)] = value
            replacements['$edgeEnergy'] = self.e1Energy

        replacements['$baseName'] = self.baseName

        for replacement in replacements:
            self._template = self._template.replace(
                replacement, str(replacements[replacement]))

        with open(self.baseName + '.lua', 'w') as f:
            f.write(self._template)

        self._uuid = uuid.uuid4().hex

        self.label = '{} | {} | {} | {} | {}'.format(
            self.element, self.charge, self.symmetry, self.experiment,
            self.edge)


class QuantyDockWidget(QDockWidget):

    def __init__(self):
        super(QuantyDockWidget, self).__init__()

        # Load the external .ui file for the widget.
        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'quanty.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.calculation = QuantyCalculation()
        self.setUi()
        self.updateUi()

    def setUi(self):
        self.temperatureLineEdit.setValidator(QDoubleValidator(self))
        self.nPsisLineEdit.setValidator(QIntValidator(self))

        self.magneticFieldXLineEdit.setValidator(QDoubleValidator(self))
        self.magneticFieldYLineEdit.setValidator(QDoubleValidator(self))
        self.magneticFieldZLineEdit.setValidator(QDoubleValidator(self))

        self.e1MinLineEdit.setValidator(QDoubleValidator(self))
        self.e1MaxLineEdit.setValidator(QDoubleValidator(self))
        self.e1NPointsLineEdit.setValidator(QIntValidator(self))
        self.e1LorentzianLineEdit.setValidator(QDoubleValidator(self))
        self.e1GaussianLineEdit.setValidator(QDoubleValidator(self))

        self.e2MinLineEdit.setValidator(QDoubleValidator(self))
        self.e2MaxLineEdit.setValidator(QDoubleValidator(self))
        self.e2NPointsLineEdit.setValidator(QIntValidator(self))
        self.e2LorentzianLineEdit.setValidator(QDoubleValidator(self))
        self.e2GaussianLineEdit.setValidator(QDoubleValidator(self))

        # Create the results model and assign it to the view.
        self.resultsModel = ListModel()

        self.resultsView.setModel(self.resultsModel)
        self.resultsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.resultsView.selectionModel().selectionChanged.connect(
            self.selectedCalculationsChanged)
        # Add a context menu.
        self.resultsView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.createResultsContextMenu()
        self.resultsView.customContextMenuRequested[QPoint].connect(
            self.showResultsContextMenu)

        # Enable actions.
        self.elementComboBox.currentTextChanged.connect(self.resetCalculation)
        self.chargeComboBox.currentTextChanged.connect(self.resetCalculation)
        self.symmetryComboBox.currentTextChanged.connect(self.resetCalculation)
        self.experimentComboBox.currentTextChanged.connect(
            self.resetCalculation)
        self.edgeComboBox.currentTextChanged.connect(self.resetCalculation)

        self.e1GaussianLineEdit.editingFinished.connect(self.updateBroadening)
        self.e2GaussianLineEdit.editingFinished.connect(self.updateBroadening)

        self.nPsisCheckBox.toggled.connect(self.updateNPsisLineEditState)
        self.fkLineEdit.editingFinished.connect(self.updateScalingFactors)
        self.gkLineEdit.editingFinished.connect(self.updateScalingFactors)
        self.zetaLineEdit.editingFinished.connect(self.updateScalingFactors)

        self.saveInputAsPushButton.clicked.connect(self.saveInputAs)
        self.calculationPushButton.clicked.connect(self.runCalculation)

    def updateUi(self):
        c = self.calculation

        self.elementComboBox.setItems(c._elements, c.element)
        self.chargeComboBox.setItems(c._charges, c.charge)
        self.symmetryComboBox.setItems(c._symmetries, c.symmetry)
        self.experimentComboBox.setItems(c._experiments, c.experiment)
        self.edgeComboBox.setItems(c._edges, c.edge)

        self.temperatureLineEdit.setText(str(c.temperature))

        self.magneticFieldXLineEdit.setText(str(c.magneticFieldX))
        self.magneticFieldYLineEdit.setText(str(c.magneticFieldY))
        self.magneticFieldZLineEdit.setText(str(c.magneticFieldZ))

        self.nPsisLineEdit.setText(str(c.nPsis))
        if c.nPsisAuto == 1:
            self.nPsisCheckBox.setChecked(True)
        else:
            self.nPsisCheckBox.setChecked(False)

        # self.fkLineEdit.setText('0.8')
        # self.gkLineEdit.setText('0.8')
        # self.zetaLineEdit.setText('1.0')

        self.energiesTabWidget.setTabText(0, str(c._e1Label))
        self.e1MinLineEdit.setText(str(c.e1Min))
        self.e1MaxLineEdit.setText(str(c.e1Max))
        self.e1NPointsLineEdit.setText(str(c.e1NPoints))
        self.e1LorentzianLineEdit.setText(str(c.e1Lorentzian))
        self.e1GaussianLineEdit.setText(str(c.e1Gaussian))

        if 'RIXS' in c.experiment:
            if self.energiesTabWidget.count() == 1:
                tab = self.energiesTabWidget.findChild(QWidget, 'e2Tab')
                self.energiesTabWidget.addTab(tab, tab.objectName())
                self.energiesTabWidget.setTabText(1, c._e2Label)
            self.e2MinLineEdit.setText(str(c.e2Min))
            self.e2MaxLineEdit.setText(str(c.e2Max))
            self.e2NPointsLineEdit.setText(str(c.e2NPoints))
            self.e2LorentzianLineEdit.setText(str(c.e2Lorentzian))
            self.e2GaussianLineEdit.setText(str(c.e2Gaussian))
        else:
            self.energiesTabWidget.removeTab(1)

        # Create the Hamiltonian model.
        self.hamiltonianModel = TreeModel(
            ('Parameter', 'Value', 'Scaling'), c.hamiltonianData)
        self.hamiltonianModel.setNodesCheckState(c.hamiltonianState)

        # Assign the Hamiltonian model to the Hamiltonian terms view.
        self.hamiltonianTermsView.setModel(self.hamiltonianModel)
        self.hamiltonianTermsView.selectionModel().setCurrentIndex(
            self.hamiltonianModel.index(0, 0), QItemSelectionModel.Select)
        self.hamiltonianTermsView.selectionModel().selectionChanged.connect(
            self.selectedHamiltonianTermChanged)

        # Assign the Hamiltonian model to the Hamiltonian parameters view.
        self.hamiltonianParametersView.setModel(self.hamiltonianModel)
        self.hamiltonianParametersView.expandAll()
        self.hamiltonianParametersView.resizeAllColumnsToContents()
        self.hamiltonianParametersView.setColumnWidth(0, 140)
        self.hamiltonianParametersView.setRootIndex(
            self.hamiltonianTermsView.currentIndex())

        # Set the sizes of the two views.
        self.hamiltonianSplitter.setSizes((120, 300))

    def setUiEnabled(self, flag=True):
        self.elementComboBox.setEnabled(flag)
        self.chargeComboBox.setEnabled(flag)
        self.symmetryComboBox.setEnabled(flag)
        self.experimentComboBox.setEnabled(flag)
        self.edgeComboBox.setEnabled(flag)

        self.temperatureLineEdit.setEnabled(flag)
        self.magneticFieldXLineEdit.setEnabled(flag)
        self.magneticFieldYLineEdit.setEnabled(flag)
        self.magneticFieldZLineEdit.setEnabled(flag)

        self.e1MinLineEdit.setEnabled(flag)
        self.e1MaxLineEdit.setEnabled(flag)
        self.e1NPointsLineEdit.setEnabled(flag)
        self.e1LorentzianLineEdit.setEnabled(flag)
        self.e1GaussianLineEdit.setEnabled(flag)

        self.e2MinLineEdit.setEnabled(flag)
        self.e2MaxLineEdit.setEnabled(flag)
        self.e2NPointsLineEdit.setEnabled(flag)
        self.e2LorentzianLineEdit.setEnabled(flag)
        self.e2GaussianLineEdit.setEnabled(flag)

        self.nPsisCheckBox.setEnabled(flag)
        if self.nPsisCheckBox.isChecked():
            self.nPsisLineEdit.setEnabled(False)
        else:
            self.nPsisLineEdit.setEnabled(True)
        self.fkLineEdit.setEnabled(flag)
        self.gkLineEdit.setEnabled(flag)
        self.zetaLineEdit.setEnabled(flag)

        self.hamiltonianTermsView.setEnabled(flag)
        self.hamiltonianParametersView.setEnabled(flag)
        self.resultsView.setEnabled(flag)

        self.saveInputAsPushButton.setEnabled(flag)

        # if self.calculation.spectra:
        #     self.elementComboBox.setEnabled(True)
        #     self.chargeComboBox.setEnabled(True)
        #     self.symmetryComboBox.setEnabled(True)
        #     self.experimentComboBox.setEnabled(True)
        #     self.edgeComboBox.setEnabled(True)

        #     self.e1GaussianLineEdit.setEnabled(True)
        #     self.e2GaussianLineEdit.setEnabled(True)

        #     self.resultsView.setEnabled(True)

        #     self.saveInputAsPushButton.setEnabled(True)

        # if flag:
        #     self.hamiltonianParametersView.setEditTriggers(
        #         QAbstractItemView.DoubleClicked)
        #     self.resultsView.setSelectionMode(
        #         QAbstractItemView.ExtendedSelection)
        # else:
        #     self.hamiltonianParametersView.setEditTriggers(
        #         QAbstractItemView.NoEditTriggers)
        #     self.resultsView.setSelectionMode(
        #         QAbstractItemView.NoSelection)

        # if self.calculation.spectra:
        #     self.resultsView.setSelectionMode(
        #         QAbstractItemView.ExtendedSelection)

    def updateBroadening(self):
        c = self.calculation

        if not c.spectra:
            return

        try:
            index = list(self.resultsView.selectedIndexes())[-1]
        except IndexError:
            return
        else:
            c.e1Gaussian = float(self.e1GaussianLineEdit.text())
            c.e2Gaussian = float(self.e2GaussianLineEdit.text())
            self.resultsModel.replaceItem(index, c)
            self.selectedCalculationsChanged()

    def updateNPsisLineEditState(self):
        if self.nPsisCheckBox.isChecked():
            self.nPsisLineEdit.setEnabled(False)
        else:
            self.nPsisLineEdit.setEnabled(True)

    def updateScalingFactors(self):
        fk = float(self.fkLineEdit.text())
        gk = float(self.gkLineEdit.text())
        zeta = float(self.zetaLineEdit.text())

        c = self.calculation
        terms = c.hamiltonianData

        for term in terms:
            configurations = terms[term]
            for configuration in configurations:
                parameters = configurations[configuration]
                for parameter in parameters:
                    value, factor = parameters[parameter]
                    if parameter.startswith('F'):
                        terms[term][configuration][parameter] = (value, fk)
                    elif parameter.startswith('G'):
                        terms[term][configuration][parameter] = (value, gk)
                    elif parameter.startswith('ζ'):
                        terms[term][configuration][parameter] = (value, zeta)
                    else:
                        continue
        self.updateUi()

    def saveInput(self):
        self.updateCalculation()
        try:
            self.calculation.saveInput()
        except PermissionError:
            self.parent().statusBar().showMessage(
                'Permission denied to write Quanty input file.')
            return

    def saveInputAs(self):
        c = self.calculation
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Quanty Input', '{}'.format(c.baseName + '.lua'),
            'Quanty Input File (*.lua)')

        if path:
            self.calculation.baseName, _ = os.path.splitext(
                    os.path.basename(path))
            self.updateMainWindowTitle()
            os.chdir(os.path.dirname(path))
            self.saveInput()

    def saveSelectedCalculationsAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Calculations', 'untitled.pkl', 'Pickle File (*.pkl)')
        if path:
            os.chdir(os.path.dirname(path))
            calculations = self.selectedCalculations()
            calculations.reverse()
            with open(path, 'wb') as p:
                pickle.dump(calculations, p)

    def updateCalculation(self):
        c = self.calculation

        c.temperature = float(self.temperatureLineEdit.text())
        c.magneticFieldX = float(self.magneticFieldXLineEdit.text())
        c.magneticFieldY = float(self.magneticFieldYLineEdit.text())
        c.magneticFieldZ = float(self.magneticFieldZLineEdit.text())

        c.nPsis = int(self.nPsisLineEdit.text())
        c.nPsisAuto = int(self.nPsisCheckBox.isChecked())

        c.e1Min = float(self.e1MinLineEdit.text())
        c.e1Max = float(self.e1MaxLineEdit.text())
        c.e1NPoints = int(self.e1NPointsLineEdit.text())
        c.e1Lorentzian = float(self.e1LorentzianLineEdit.text())
        c.e1Gaussian = float(self.e1GaussianLineEdit.text())

        if 'RIXS' in c.experiment:
            c.e2Min = float(self.e2MinLineEdit.text())
            c.e2Max = float(self.e2MaxLineEdit.text())
            c.e2NPoints = int(self.e2NPointsLineEdit.text())
            c.e2Lorentzian = float(self.e2LorentzianLineEdit.text())
            c.e2Gaussian = float(self.e2GaussianLineEdit.text())

        c.hamiltonianData = self.hamiltonianModel.getModelData()
        c.hamiltonianState = self.hamiltonianModel.getNodesCheckState()

    def resetCalculation(self):
        element = self.elementComboBox.currentText()
        charge = self.chargeComboBox.currentText()
        symmetry = self.symmetryComboBox.currentText()
        experiment = self.experimentComboBox.currentText()
        edge = self.edgeComboBox.currentText()

        self.calculation = QuantyCalculation(
            element=element, charge=charge, symmetry=symmetry,
            experiment=experiment, edge=edge)

        self.updateUi()
        self.parent().plotWidget.reset()
        self.resultsView.selectionModel().clearSelection()

    def removeSelectedCalculations(self):
        self.resultsModel.removeItems(self.resultsView.selectedIndexes())
        self.updateResultsViewSelection()

    def removeAllCalculations(self):
        self.resultsModel.reset()
        self.parent().plotWidget.reset()

    def loadCalculations(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Load Calculations', '', 'Pickle File (*.pkl)')
        if path:
            with open(path, 'rb') as p:
                self.resultsModel.appendItems(pickle.load(p))
        self.updateResultsViewSelection()
        self.updateMainWindowTitle()

    def runCalculation(self):
        # import sys
        if 'win32' in sys.platform:
            self.command = 'Quanty.exe'
        else:
            self.command = 'Quanty'

        with open(os.devnull, 'w') as f:
            try:
                subprocess.call(self.command, stdout=f, stderr=f)
            except:
                self.parent().statusBar().showMessage(
                    'Could not find Quanty. Please install '
                    'it and set the PATH environment variable.')
                return

        # Write the input file to disk.
        self.saveInput()

        # Disable the UI while the calculation is running.
        self.setUiEnabled(False)

        c = self.calculation
        c.startingTime = datetime.datetime.now()

        # Run Quanty using QProcess.
        self.process = QProcess()

        self.process.start(self.command, (c.baseName + '.lua', ))
        self.parent().statusBar().showMessage(
            'Running "{} {}" in {}.'.format(
                self.command, c.baseName + '.lua', os.getcwd()))

        self.process.readyReadStandardOutput.connect(self.handleOutputLogging)
        self.process.started.connect(self.updateCalculationPushButton)
        self.process.finished.connect(self.processCalculation)

    def updateCalculationPushButton(self):
        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'stop.svg')))
        self.calculationPushButton.setIcon(icon)

        self.calculationPushButton.setText('Stop')
        self.calculationPushButton.setToolTip('Stop Quanty')

        self.calculationPushButton.disconnect()
        self.calculationPushButton.clicked.connect(self.stopCalculation)

    def resetCalculationPushButton(self):
        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'play.svg')))
        self.calculationPushButton.setIcon(icon)

        self.calculationPushButton.setText('Run')
        self.calculationPushButton.setToolTip('Run Quanty')

        self.calculationPushButton.disconnect()
        self.calculationPushButton.clicked.connect(self.runCalculation)

    def stopCalculation(self):
        self.process.kill()
        self.setUiEnabled(True)

    def processCalculation(self):
        c = self.calculation

        # When did I finish?
        c.endingTime = datetime.datetime.now()

        # Reset the calculation button.
        self.resetCalculationPushButton()

        # Re-enable the UI if the calculation has finished.
        self.setUiEnabled(True)

        # Evaluate the exit code and status of the process.
        exitStatus = self.process.exitStatus()
        exitCode = self.process.exitCode()
        timeout = 10000
        statusBar = self.parent().statusBar()
        if exitStatus == 0 and exitCode == 0:
            message = ('Quanty has finished successfully in ')
            delta = int((c.endingTime - c.startingTime).total_seconds())
            hours, reminder = divmod(delta, 60)
            minutes, seconds = divmod(reminder, 60)
            if hours > 0:
                message += '{} hours {} minutes and {} seconds.'.format(
                    hours, minutes, seconds)
            elif minutes > 0:
                message += '{} minutes and {} seconds.'.format(minutes, hours)
            else:
                message += '{} seconds.'.format(seconds)
            statusBar.showMessage(message, timeout)
        elif exitStatus == 0 and exitCode == 1:
            self.handleErrorLogging()
            statusBar.showMessage((
                'Quanty has finished unsuccessfully. '
                'Check the logging window for more details.'), timeout)
            self.parent().splitter.setSizes((400, 200))
            return
        # exitCode is platform dependend; exitStatus is always 1.
        elif exitStatus == 1:
            message = 'Quanty was stopped.'
            statusBar.showMessage(message, timeout)
            return

        c.spectra = glob.glob('{}*.spec'.format(c.baseName))

        # Store the calculation in the model.
        self.resultsModel.appendItems([c])

        # This should be in a signal?
        self.updateResultsViewSelection()

        # Open the results page.
        # self.quantyToolBox.setCurrentWidget(self.resultsPage)

    def plot(self):
        c = self.calculation

        plotWidget = self.parent().plotWidget

        if 'RIXS' in c.experiment:
            plotWidget.setGraphXLabel('Incident Energy (eV)')
            plotWidget.setGraphYLabel('Energy Transfer (eV)')

            colormap = {'name': 'viridis', 'normalization': 'linear',
                                'autoscale': True, 'vmin': 0.0, 'vmax': 1.0}
            plotWidget.setDefaultColormap(colormap)

            xScale = (c.e1Max - c.e1Min) / c.e1NPoints
            yScale = (c.e2Max - c.e2Min) / c.e2NPoints
            scale = (xScale, yScale)

            xOrigin = c.e1Min
            yOrigin = c.e2Min
            origin = (xOrigin, yOrigin)

            z = c.spectra['Isotropic']

            if c.e1Gaussian > 0. and c.e2Gaussian > 0.:
                xFwhm = c.e1Gaussian / xScale
                yFwhm = c.e2Gaussian / yScale

                fwhm = [xFwhm, yFwhm]
                z = broaden(z, fwhm, 'gaussian')

            plotWidget.addImage(z, origin=origin, scale=scale, reset=False)

        else:
            plotWidget.setGraphXLabel('Absorption Energy (eV)')
            plotWidget.setGraphYLabel('Absorption Cross Section (a.u.)')

            legend = c.label + ' | ' + c._uuid
            x = np.linspace(c.e1Min, c.e1Max, c.e1NPoints + 1)
            scale = (c.e1Max - c.e1Min) / c.e1NPoints
            y = c.spectra['Isotropic']

            if c.e1Gaussian > 0.:
                fwhm = c.e1Gaussian / scale
                y = broaden(y, fwhm, 'gaussian')

            try:
                plotWidget.addCurve(x, y, legend)
            except AssertionError:
                statusBar = self.parent().statusBar()
                message = 'The x and y arrays have different lengths.'
                timeout = 4000
                statusBar.showMessage(message, timeout)

        # self.saveSelectedCalculationsAsAction.setEnabled(False)

    def selectedHamiltonianTermChanged(self):
        index = self.hamiltonianTermsView.currentIndex()
        self.hamiltonianParametersView.setRootIndex(index)

    # Results view related methods.
    def createResultsContextMenu(self):
        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'save.svg')))
        self.saveSelectedCalculationsAsAction = QAction(
            icon, 'Save Selected Calculations As...', self,
            triggered=self.saveSelectedCalculationsAs)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'trash.svg')))
        self.removeCalculationsAction = QAction(
            icon, 'Remove Selected Calculations', self,
            triggered=self.removeSelectedCalculations)
        self.removeAllCalculationsAction = QAction(
            icon, 'Remove All Calculations', self,
            triggered=self.removeAllCalculations)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'folder-open.svg')))
        self.loadCalculationsAction = QAction(
            icon, 'Load Calculations', self,
            triggered=self.loadCalculations)

        self.itemsContextMenu = QMenu('Items Context Menu', self)
        # icon = QIcon(resourceFileName(
        #     'crispy:' + os.path.join('gui', 'icons', 'area-chart.svg')))
        # spectrum = self.itemsContextMenu.addMenu(icon, 'Spectra')
        # spectrum.addAction(self.removeAllCalculationsAction)
        # self.itemsContextMenu.addSeparator()
        self.itemsContextMenu.addAction(self.saveSelectedCalculationsAsAction)
        self.itemsContextMenu.addAction(self.removeCalculationsAction)

        self.viewContextMenu = QMenu('View Context Menu', self)
        self.viewContextMenu.addAction(self.loadCalculationsAction)
        self.viewContextMenu.addAction(self.removeAllCalculationsAction)

    def showResultsContextMenu(self, position):
        selection = self.resultsView.selectionModel().selection()
        selectedItemsRegion = self.resultsView.visualRegionForSelection(
            selection)
        cursorPosition = self.resultsView.mapFromGlobal(QCursor.pos())

        if selectedItemsRegion.contains(cursorPosition):
            self.itemsContextMenu.exec_(self.resultsView.mapToGlobal(position))
        else:
            self.viewContextMenu.exec_(self.resultsView.mapToGlobal(position))

    def selectedCalculations(self):
        calculations = list()
        indexes = self.resultsView.selectedIndexes()
        for index in indexes:
            calculations.append(self.resultsModel.getIndexData(index))
        return calculations

    def selectedCalculationsChanged(self):
        calculations = self.selectedCalculations()
        self.parent().plotWidget.reset()

        # if not calculations:
        #     self.setUiEnabled(True)
        #     return

        for calculation in calculations:
            self.calculation = copy.deepcopy(calculation)
            self.plot()

        # Set the UI using data from the last selected calculation.
        self.updateUi()
        # self.setUiEnabled(False)

    def updateResultsViewSelection(self):
        self.resultsView.selectionModel().clearSelection()
        index = self.resultsModel.index(self.resultsModel.rowCount() - 1)
        self.resultsView.selectionModel().select(
            index, QItemSelectionModel.Select)

    def handleOutputLogging(self):
        self.process.setReadChannel(QProcess.StandardOutput)
        data = self.process.readAllStandardOutput().data()
        self.parent().loggerWidget.appendPlainText(data.decode('utf-8'))

    def handleErrorLogging(self):
        self.process.setReadChannel(QProcess.StandardError)
        data = self.process.readAllStandardError().data()
        self.parent().loggerWidget.appendPlainText(data.decode('utf-8'))

    def updateMainWindowTitle(self):
        c = self.calculation
        title = 'Crispy - {}'.format(c.baseName + '.lua')
        self.parent().setWindowTitle(title)


if __name__ == '__main__':
    pass
