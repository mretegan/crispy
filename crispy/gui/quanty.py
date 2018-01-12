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
__date__ = '06/12/2017'


import collections
import copy
import datetime
import json
import numpy as np
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
import platform
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


class InvalidVectorError(Exception):
    pass


class QuantyCalculation(object):

    # Parameters not loaded from external files should have defaults.
    _defaults = {
        'element': 'Ni',
        'charge': '2+',
        'symmetry': 'Oh',
        'experiment': 'XAS',
        'edge': 'L2,3 (2p)',
        'temperature': 10.0,
        'magneticField': 0.0,
        'kin': np.array([0.0, 0.0, -1.0]),
        'ein': np.array([0.0, 1.0, 0.0]),
        'kout': np.array([0.0, 0.0, 0.0]),
        'eout': np.array([0.0, 0.0, 0.0]),
        'calculateIso': 1,
        'calculateCD': 0,
        'calculateLD': 0,
        'nPsisAuto': 1,
        'fk': 0.8,
        'gk': 0.8,
        'zeta': 1.0,
        'baseName': 'untitled',
        'spectra': None,
        'uuid': None,
        'startingTime': None,
        'endingTime': None,
        'verbosity': '0x0000',
        'needsCompleteUiEnabled': False
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
        self.elements = list(branch)
        if self.element not in self.elements:
            self.element = self.elements[0]

        branch = branch[self.element]['charges']
        self.charges = list(branch)
        if self.charge not in self.charges:
            self.charge = self.charges[0]

        branch = branch[self.charge]['symmetries']
        self.symmetries = list(branch)
        if self.symmetry not in self.symmetries:
            self.symmetry = self.symmetries[0]

        branch = branch[self.symmetry]['experiments']
        self.experiments = list(branch)
        if self.experiment not in self.experiments:
            self.experiment = self.experiments[0]

        branch = branch[self.experiment]['edges']
        self.edges = list(branch)
        if self.edge not in self.edges:
            self.edge = self.edges[0]

        branch = branch[self.edge]

        self.templateName = branch['template name']

        self.configurations = branch['configurations']
        self.nPsis = branch['number of states']
        try:
            self.monoElectronicRadialME = (branch[
                'monoelectronic radial matrix elements'])
        except KeyError:
            self.monoElectronicRadialME = None

        self.e1Label = branch['energies'][0][0]
        self.e1Min = branch['energies'][0][1]
        self.e1Max = branch['energies'][0][2]
        self.e1NPoints = branch['energies'][0][3]
        self.e1Edge = branch['energies'][0][4]
        self.e1Lorentzian = branch['energies'][0][5]
        self.e1Gaussian = branch['energies'][0][6]

        if 'RIXS' in self.experiment:
            self.e2Label = branch['energies'][1][0]
            self.e2Min = branch['energies'][1][1]
            self.e2Max = branch['energies'][1][2]
            self.e2NPoints = branch['energies'][1][3]
            self.e2Edge = branch['energies'][1][4]
            self.e2Lorentzian = branch['energies'][1][5]
            self.e2Gaussian = branch['energies'][1][6]

        self.hamiltonianData = OrderedDict()
        self.hamiltonianState = OrderedDict()

        branch = tree['elements'][self.element]['charges'][self.charge]

        for label, configuration in self.configurations:
            label = '{} Hamiltonian'.format(label)
            terms = branch['configurations'][configuration]['terms']

            for term in terms:
                # Hack to include the magnetic and exchange terms only for
                # selected calculations.
                subshell = self.configurations[0][1][:2]
                if not ((subshell == '4f' and self.edge == 'M4,5 (3d)') or
                        (subshell == '3d' and self.edge == 'L2,3 (2p)') or
                        (subshell == '4d' and self.edge == 'L2,3 (2p)') or
                        (subshell == '5d' and self.edge == 'L2,3 (2p)')):
                    if 'Magnetic' in term or 'Exchange' in term:
                        continue

                if 'Magnetic' in term or 'Exchange' in term:
                    self.needsCompleteUiEnabled = True
                else:
                    self.needsCompleteUiEnabled = False

                if ('Atomic' in term or 'Magnetic' in term or
                        'Exchange' in term):
                    parameters = terms[term]
                elif '3d-4p Hybridization' in term:
                    try:
                        parameters = terms[term][self.symmetry][configuration]
                    except KeyError:
                        continue
                else:
                    try:
                        parameters = terms[term][self.symmetry]
                    except KeyError:
                        continue

                for parameter in parameters:
                    if 'Atomic' in term:
                        if parameter[0] in ('F', 'G'):
                            scaling = 0.8
                        else:
                            scaling = 1.0
                    else:
                        scaling = str()

                    self.hamiltonianData[term][label][parameter] = (
                        parameters[parameter], scaling)

                if 'Atomic' in term or 'Crystal Field' in term:
                    self.hamiltonianState[term] = 2
                else:
                    self.hamiltonianState[term] = 0

    def saveInput(self):
        templatePath = resourceFileName(
            'crispy:' + os.path.join('modules', 'quanty', 'templates',
                                     '{}'.format(self.templateName)))

        with open(templatePath) as p:
            self.template = p.read()

        replacements = collections.OrderedDict()

        replacements['$verbosity'] = self.verbosity

        subshell = self.configurations[0][1][:2]
        subshell_occupation = self.configurations[0][1][2:]
        replacements['$NElectrons_{}'.format(subshell)] = subshell_occupation

        replacements['$T'] = self.temperature

        replacements['$Emin1'] = self.e1Min
        replacements['$Emax1'] = self.e1Max
        replacements['$NE1'] = self.e1NPoints
        replacements['$Eedge1'] = self.e1Edge
        replacements['$Gamma1'] = self.e1Lorentzian

        s = '{{{0:.6g}, {1:.6g}, {2:.6g}}}'
        u = self.kin / np.linalg.norm(self.kin)
        replacements['$kin'] = s.format(u[0], u[1], u[2])

        v = self.ein / np.linalg.norm(self.ein)
        replacements['$ein1'] = s.format(v[0], v[1], v[2])

        # Generate a second, perpedicular, polarization vector to the plane
        # defined by the wave vector and the first polarization vector.
        w = np.cross(v, u)
        w = w / np.linalg.norm(w)
        replacements['$ein2'] = s.format(w[0], w[1], w[2])

        replacements['$calculateIso'] = self.calculateIso
        replacements['$calculateCD'] = self.calculateCD
        replacements['$calculateLD'] = self.calculateLD

        if 'RIXS' in self.experiment:
            # The Lorentzian broadening along the incident axis cannot be
            # changed in the interface, and must therefore be set to the
            # final value before the start of the calculation.
            # replacements['$Gamma1'] = self.e1Lorentzian
            replacements['$Emin2'] = self.e2Min
            replacements['$Emax2'] = self.e2Max
            replacements['$NE2'] = self.e2NPoints
            replacements['$Eedge2'] = self.e2Edge
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
            elif 'Magnetic Field' in term:
                name = 'H_magnetic_field'
            elif 'Exchange Field' in term:
                name = 'H_exchange_field'
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
                    # Convert to parameters name from Greek letters.
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

        replacements['$baseName'] = self.baseName

        for replacement in replacements:
            self.template = self.template.replace(
                replacement, str(replacements[replacement]))

        with open(self.baseName + '.lua', 'w') as f:
            f.write(self.template)

        self.uuid = uuid.uuid4().hex[:4]

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
        self.magneticFieldLineEdit.setValidator(QDoubleValidator(self))

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

        self.nPsisLineEdit.setValidator(QIntValidator(self))
        self.fkLineEdit.setValidator(QDoubleValidator(self))
        self.gkLineEdit.setValidator(QDoubleValidator(self))
        self.zetaLineEdit.setValidator(QDoubleValidator(self))

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

        self.magneticFieldLineEdit.editingFinished.connect(
            self.updateMagneticField)

        self.e1GaussianLineEdit.editingFinished.connect(self.updateBroadening)
        self.e2GaussianLineEdit.editingFinished.connect(self.updateBroadening)

        self.kinLineEdit.editingFinished.connect(self.updateIncidentWaveVector)
        self.einLineEdit.editingFinished.connect(
            self.updateIncidentPolarizationVector)

        self.nPsisAutoCheckBox.toggled.connect(self.updateNPsisLineEditState)
        self.fkLineEdit.editingFinished.connect(self.updateScalingFactors)
        self.gkLineEdit.editingFinished.connect(self.updateScalingFactors)
        self.zetaLineEdit.editingFinished.connect(self.updateScalingFactors)

        self.plotIsoCheckBox.toggled.connect(self.plotSelectedCalculations)
        self.plotCDCheckBox.toggled.connect(self.plotSelectedCalculations)
        self.plotLDCheckBox.toggled.connect(self.plotSelectedCalculations)

        self.saveInputAsPushButton.clicked.connect(self.saveInputAs)
        self.calculationPushButton.clicked.connect(self.runCalculation)

    def updateUi(self):
        c = self.calculation

        self.elementComboBox.setItems(c.elements, c.element)
        self.chargeComboBox.setItems(c.charges, c.charge)
        self.symmetryComboBox.setItems(c.symmetries, c.symmetry)
        self.experimentComboBox.setItems(c.experiments, c.experiment)
        self.edgeComboBox.setItems(c.edges, c.edge)

        self.temperatureLineEdit.setText(str(c.temperature))
        self.magneticFieldLineEdit.setText(str(c.magneticField))

        if c.needsCompleteUiEnabled:
            self.magneticFieldLineEdit.setEnabled(True)
            self.kinLineEdit.setEnabled(True)
            self.einLineEdit.setEnabled(True)
            self.calculateIsoCheckBox.setEnabled(True)
            self.calculateCDCheckBox.setEnabled(True)
            self.calculateLDCheckBox.setEnabled(True)
        else:
            self.magneticFieldLineEdit.setEnabled(False)
            self.kinLineEdit.setEnabled(False)
            self.einLineEdit.setEnabled(False)
            self.calculateIsoCheckBox.setEnabled(True)
            self.calculateCDCheckBox.setEnabled(False)
            self.calculateLDCheckBox.setEnabled(False)

        self.kinLineEdit.setText(self.vectorToString(c.kin))
        self.einLineEdit.setText(self.vectorToString(c.ein))

        self.calculateIsoCheckBox.setChecked(c.calculateIso)
        self.calculateCDCheckBox.setChecked(c.calculateCD)
        self.calculateLDCheckBox.setChecked(c.calculateLD)

        self.nPsisLineEdit.setText(str(c.nPsis))
        self.nPsisAutoCheckBox.setChecked(c.nPsisAuto)

        self.fkLineEdit.setText(str(c.fk))
        self.gkLineEdit.setText(str(c.gk))
        self.zetaLineEdit.setText(str(c.zeta))

        self.energiesTabWidget.setTabText(0, str(c.e1Label))
        self.e1MinLineEdit.setText(str(c.e1Min))
        self.e1MaxLineEdit.setText(str(c.e1Max))
        self.e1NPointsLineEdit.setText(str(c.e1NPoints))
        self.e1LorentzianLineEdit.setText(str(c.e1Lorentzian))
        self.e1GaussianLineEdit.setText(str(c.e1Gaussian))

        if 'RIXS' in c.experiment:
            if self.energiesTabWidget.count() == 1:
                tab = self.energiesTabWidget.findChild(QWidget, 'e2Tab')
                self.energiesTabWidget.addTab(tab, tab.objectName())
                self.energiesTabWidget.setTabText(1, c.e2Label)
            self.e2MinLineEdit.setText(str(c.e2Min))
            self.e2MaxLineEdit.setText(str(c.e2Max))
            self.e2NPointsLineEdit.setText(str(c.e2NPoints))
            self.e2LorentzianLineEdit.setText(str(c.e2Lorentzian))
            self.e2GaussianLineEdit.setText(str(c.e2Gaussian))
        else:
            self.energiesTabWidget.removeTab(1)

        self.updateHamiltonian()

    def updateHamiltonian(self):
        c = self.calculation

        # Create a Hamiltonian model.
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
        self.hamiltonianParametersView.setColumnWidth(0, 130)
        self.hamiltonianParametersView.setRootIndex(
            self.hamiltonianTermsView.currentIndex())

        # Set the sizes of the two views.
        self.hamiltonianSplitter.setSizes((130, 300))

    def setUiEnabled(self, flag=True):
        self.elementComboBox.setEnabled(flag)
        self.chargeComboBox.setEnabled(flag)
        self.symmetryComboBox.setEnabled(flag)
        self.experimentComboBox.setEnabled(flag)
        self.edgeComboBox.setEnabled(flag)

        self.temperatureLineEdit.setEnabled(flag)
        self.magneticFieldLineEdit.setEnabled(flag)

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

        c = self.calculation
        if c.needsCompleteUiEnabled:
            self.kinLineEdit.setEnabled(flag)
            self.einLineEdit.setEnabled(flag)
            self.calculateIsoCheckBox.setEnabled(flag)
            self.calculateCDCheckBox.setEnabled(flag)
            self.calculateLDCheckBox.setEnabled(flag)
        else:
            self.kinLineEdit.setEnabled(False)
            self.einLineEdit.setEnabled(False)
            self.calculateIsoCheckBox.setEnabled(False)
            self.calculateCDCheckBox.setEnabled(False)
            self.calculateLDCheckBox.setEnabled(False)

        self.nPsisAutoCheckBox.setEnabled(flag)
        if self.nPsisAutoCheckBox.isChecked():
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

    def updateMagneticField(self):
        c = self.calculation

        magneticField = float(self.magneticFieldLineEdit.text())

        if magneticField == 0:
            c.hamiltonianState['Magnetic Field'] = 0
            self.calculateCDCheckBox.setChecked(False)
        else:
            c.hamiltonianState['Magnetic Field'] = 2
            self.calculateCDCheckBox.setChecked(True)

        kin = self.stringToVector(self.kinLineEdit.text())
        kin = kin / np.linalg.norm(kin)
        configurations = c.hamiltonianData['Magnetic Field']
        for configuration in configurations:
            parameters = configurations[configuration]
            for i, parameter in enumerate(parameters):
                value = magneticField * -kin[i]
                if abs(value) == 0.0:
                    value = 0.0
                configurations[configuration][parameter] = (value, str())
        self.updateHamiltonian()

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
            if 'RIXS' in c.experiment:
                c.e2Gaussian = float(self.e2GaussianLineEdit.text())
            self.resultsModel.replaceItem(index, c)
            self.plotSelectedCalculations()

    def updateIncidentWaveVector(self):
        # TODO: Write proper validators.
        statusBar = self.parent().statusBar()

        try:
            kin = self.stringToVector(self.kinLineEdit.text())
        except InvalidVectorError:
            message = 'Wrong expression given for the wave vector.'
            statusBar.showMessage(message)
            return

        if np.all(kin == 0):
            message = 'The wave vector cannot be null.'
            statusBar.showMessage(message)
            return

        ein = self.stringToVector(self.einLineEdit.text())
        # Check if the wave and polarization vectors are perpendicular.
        if np.dot(kin, ein) != 0:
            # Determine a possible perpendicular vector.
            if kin[2] != 0 or (-kin[0] - kin[1]) != 0:
                ein = np.array([kin[2], kin[2], -kin[0] - kin[1]])
            else:
                ein = np.array([-kin[2] - kin[1], kin[0], kin[0]])
        self.einLineEdit.setText(self.vectorToString(ein))

        self.updateMagneticField()

    def updateIncidentPolarizationVector(self):
        statusBar = self.parent().statusBar()

        try:
            ein = self.stringToVector(self.einLineEdit.text())
        except:
            message = 'Wrong expression given for the polarization vector.'
            statusBar.showMessage(message)
            return

        if np.all(ein == 0):
            message = 'The polarization vector cannot be null.'
            statusBar.showMessage(message)
            return

        kin = self.stringToVector(self.kinLineEdit.text())
        if np.dot(kin, ein) != 0:
            message = ('The wave and polarization vectors need to be '
                       'perpendicular.')
            statusBar.showMessage(message)

    def updateNPsisLineEditState(self):
        if self.nPsisAutoCheckBox.isChecked():
            self.nPsisLineEdit.setEnabled(False)
        else:
            self.nPsisLineEdit.setEnabled(True)

    def updateScalingFactors(self):
        c = self.calculation

        c.fk = float(self.fkLineEdit.text())
        c.gk = float(self.gkLineEdit.text())
        c.zeta = float(self.zetaLineEdit.text())

        terms = c.hamiltonianData

        for term in terms:
            configurations = terms[term]
            for configuration in configurations:
                parameters = configurations[configuration]
                for parameter in parameters:
                    value, scaling = parameters[parameter]
                    if parameter.startswith('F'):
                        terms[term][configuration][parameter] = (value, c.fk)
                    elif parameter.startswith('G'):
                        terms[term][configuration][parameter] = (value, c.gk)
                    elif parameter.startswith('ζ'):
                        terms[term][configuration][parameter] = (value, c.zeta)
                    else:
                        continue
        self.updateUi()

    def saveInput(self):
        self.updateCalculation()
        statusBar = self.parent().statusBar()
        try:
            self.calculation.saveInput()
        except PermissionError:
            statusBar.showMessage(
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
        c = copy.deepcopy(self.calculation)

        c.temperature = float(self.temperatureLineEdit.text())
        c.magneticField = float(self.magneticFieldLineEdit.text())

        c.kin = self.stringToVector(self.kinLineEdit.text())
        c.ein = self.stringToVector(self.einLineEdit.text())

        c.calculateIso = int(self.calculateIsoCheckBox.isChecked())
        c.calculateCD = int(self.calculateCDCheckBox.isChecked())
        c.calculateLD = int(self.calculateLDCheckBox.isChecked())

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

        c.nPsis = int(self.nPsisLineEdit.text())
        c.nPsisAuto = int(self.nPsisAutoCheckBox.isChecked())

        c.hamiltonianData = self.hamiltonianModel.getModelData()
        c.hamiltonianState = self.hamiltonianModel.getNodesCheckState()

        c.spectra = dict()

        self.calculation = copy.deepcopy(c)

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
        self.updateMainWindowTitle()
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
        arch = '64-bit' if '64' in platform.machine() else '32-bit'
        path = resourceFileName(
            'crispy:' + os.path.join(
                'modules', 'quanty', 'bin', sys.platform, arch))
        os.environ['PATH'] = '{};{}'.format(path, os.environ['PATH'])

        if 'win32' in sys.platform:
            self.command = 'Quanty.exe'
        else:
            self.command = 'Quanty'

        statusBar = self.parent().statusBar()
        with open(os.devnull, 'w') as f:
            try:
                subprocess.call(self.command, stdout=f, stderr=f)
            except:
                statusBar.showMessage(
                    'Could not find Quanty. Please install '
                    'it and set the PATH environment variable.')
                return

        # Write the input file to disk.
        self.saveInput()

        self.parent().splitter.setSizes((450, 150))

        # Disable the UI while the calculation is running.
        self.setUiEnabled(False)

        c = self.calculation
        c.startingTime = datetime.datetime.now()

        # Run Quanty using QProcess.
        self.process = QProcess()

        self.process.start(self.command, (c.baseName + '.lua', ))
        statusBar.showMessage(
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
            return
        # exitCode is platform dependend; exitStatus is always 1.
        elif exitStatus == 1:
            message = 'Quanty was stopped.'
            statusBar.showMessage(message, timeout)
            return

        spectra = list()
        if c.calculateIso:
            spectra.append(('Isotropic', '_iso.spec'))

        if c.calculateCD:
            spectra.append(('XMCD', '_cd.spec'))

        if c.calculateLD:
            spectra.append(('X(M)LD', '_ld.spec'))

        for spectrum, suffix in spectra:
            try:
                f = '{0:s}{1:s}'.format(c.baseName, suffix)
                data = np.loadtxt(f, skiprows=5)
            except FileNotFoundError:
                continue

            if 'RIXS' in c.experiment:
                c.spectra[spectrum] = -data[:, 2::2]
            else:
                c.spectra[spectrum] = -data[:, 2::2][:, 0]

        # Store the calculation in the model.
        self.resultsModel.appendItems([c])

        # Should this be a signal?
        self.updateResultsViewSelection()

        # Open the results page.
        self.quantyToolBox.setCurrentWidget(self.resultsPage)

    def plot(self, spectrumName):
        plotWidget = self.parent().plotWidget
        statusBar = self.parent().statusBar()

        c = self.calculation
        try:
            data = c.spectra[spectrumName]
        except KeyError:
            return

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

            z = data

            if c.e1Gaussian > 0. and c.e2Gaussian > 0.:
                xFwhm = c.e1Gaussian / xScale
                yFwhm = c.e2Gaussian / yScale

                fwhm = [xFwhm, yFwhm]
                z = broaden(z, fwhm, 'gaussian')

            plotWidget.addImage(z, origin=origin, scale=scale, reset=False)

        else:
            # Check if the data is valid.
            if np.max(np.abs(data)) < np.finfo(np.float32).eps:
                message = 'The {} spectrum has very low intensity.'.format(
                    spectrumName)
                statusBar.showMessage(message)

            plotWidget.setGraphXLabel('Absorption Energy (eV)')
            plotWidget.setGraphYLabel('Absorption Cross Section (a.u.)')

            legend = '{} | {} | id: {}'.format(c.label, spectrumName, c.uuid)
            scale = (c.e1Max - c.e1Min) / c.e1NPoints

            x = np.linspace(c.e1Min, c.e1Max, c.e1NPoints + 1)
            y = data

            if c.e1Gaussian > 0.:
                fwhm = c.e1Gaussian / scale
                y = broaden(y, fwhm, 'gaussian')

            try:
                plotWidget.addCurve(x, y, legend)
            except AssertionError:
                message = 'The x and y arrays have different lengths.'
                statusBar.showMessage(message)

        # TODO: Work on saving the calculation data to different formats.
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
        self.plotSelectedCalculations()
        self.updateUi()

    def plotSelectedCalculations(self):
        # Reset the plot widget.
        self.parent().plotWidget.reset()

        spectraName = list()
        if self.plotIsoCheckBox.isChecked():
            spectraName.append('Isotropic')

        # Maybe add the left and right polarizations.
        if self.plotCDCheckBox.isChecked():
            spectraName.append('XMCD')

        if self.plotLDCheckBox.isChecked():
            spectraName.append('X(M)LD')

        for calculation in self.selectedCalculations():
            self.calculation = copy.deepcopy(calculation)
            for spectrumName in spectraName:
                self.plot(spectrumName)

    def updateResultsViewSelection(self):
        self.resultsView.selectionModel().clearSelection()
        index = self.resultsModel.index(self.resultsModel.rowCount() - 1)
        self.resultsView.selectionModel().select(
            index, QItemSelectionModel.Select)

    def handleOutputLogging(self):
        self.process.setReadChannel(QProcess.StandardOutput)
        data = self.process.readAllStandardOutput().data()
        data = data.decode('utf-8').rstrip()
        self.parent().loggerWidget.appendPlainText(data)

    def handleErrorLogging(self):
        self.process.setReadChannel(QProcess.StandardError)
        data = self.process.readAllStandardError().data()
        self.parent().loggerWidget.appendPlainText(data.decode('utf-8'))

    def updateMainWindowTitle(self):
        c = self.calculation
        title = 'Crispy - {}'.format(c.baseName + '.lua')
        self.parent().setWindowTitle(title)

    @staticmethod
    def vectorToString(v):
        return('[{0:.1g}, {1:.1g}, {2:.1g}]'.format(v[0], v[1], v[2]))

    @staticmethod
    def stringToVector(s):
        # Remove the square brakets and split the string.
        tokens = s[1:-1].split(',')
        try:
            v = np.array([tokens[0], tokens[1], tokens[2]], dtype=np.float64)
        except (ValueError, IndexError):
            raise(InvalidVectorError)
        else:
            return(v)


if __name__ == '__main__':
    pass
