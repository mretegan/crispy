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
__date__ = '05/12/2017'


import collections
import copy
import datetime
import functools
import json
import numpy as np
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle
import re
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


class NonPerpendicularVectorsError(Exception):
    pass


class NullVectorError(Exception):
    pass


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
        '_kin': np.array([0.0, -1.0, 0.0]),
        '_ein': np.array([0.0, 0.0, 1.0]),
        '_kout': np.array([0.0, 0.0, 0.0]),
        '_eout': np.array([0.0, 0.0, 0.0]),
        'nPsisAuto': 1,
        'calculateIso': 1,
        'calculateCD': 0,
        'calculateLD': 0,
        'fk': 0.8,
        'gk': 0.8,
        'zeta': 1.0,
        'baseName': 'untitled',
        'spectra': None,
        '_uuid': None,
        'startingTime': None,
        'endingTime': None,
        '_needsCompleteUiEnabled': False,
        'verbosity': '0x0000'
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
        self.e1Edge = branch['energies'][0][4]
        self.e1Lorentzian = branch['energies'][0][5]
        self.e1Gaussian = branch['energies'][0][6]

        if 'RIXS' in self.experiment:
            self._e2Label = branch['energies'][1][0]
            self.e2Min = branch['energies'][1][1]
            self.e2Max = branch['energies'][1][2]
            self.e2NPoints = branch['energies'][1][3]
            self.e2Edge = branch['energies'][1][4]
            self.e2Lorentzian = branch['energies'][1][5]
            self.e2Gaussian = branch['energies'][1][6]

        self.hamiltonianData = OrderedDict()
        self.hamiltonianState = OrderedDict()

        branch = tree['elements'][self.element]['charges'][self.charge]

        for label, configuration in self._configurations:
            label = '{} Hamiltonian'.format(label)
            terms = branch['configurations'][configuration]['terms']

            for term in terms:
                # Hack to include the magnetic and exchange terms only for
                # selected calculations.
                subshell = self._configurations[0][1][:2]
                if not ((subshell == '4f' and self.edge == 'M4,5 (3d)') or
                        (subshell == '3d' and self.edge == 'L2,3 (2p)') or
                        (subshell == '4d' and self.edge == 'L2,3 (2p)') or
                        (subshell == '5d' and self.edge == 'L2,3 (2p)')):
                    if 'Magnetic' in term or 'Exchange' in term:
                        continue

                if 'Magnetic' in term or 'Exchange' in term:
                    self._needsCompleteUiEnabled = True
                else:
                    self._needsCompleteUiEnabled = False

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

    @property
    def kin(self):
        return(self._kin)

    @kin.setter
    def kin(self, v):
        if np.all(v == 0):
            raise(NullVectorError)
        # self._kin = v / np.linalg.norm(v)
        self._kin = v
        # Check if the wave and polarization vectors are perpendicular.
        if np.dot(self.kin, self.ein) != 0:
            # Determine a possible perpendicular vector.
            if v[2] != 0 or (-v[0] - v[1]) != 0:
                w = np.array([v[2], v[2], -v[0] - v[1]])
            else:
                w = np.array([-v[2] - v[1], v[0], v[0]])
            # Assign it to the polarization vector.
            self.ein = w
            # self.ein = w / np.linalg.norm(w)

    @property
    def ein(self):
        return(self._ein)

    @ein.setter
    def ein(self, w):
        if np.dot(self.kin, w) != 0:
            raise(NonPerpendicularVectorsError)
        else:
            if np.all(w == 0):
                raise(NullVectorError)
        self._ein = w
        # self._ein = w / np.linalg.norm(w)

    def saveInput(self):
        templatePath = resourceFileName(
            'crispy:' + os.path.join('modules', 'quanty', 'templates',
                                     '{}'.format(self._templateName)))

        with open(templatePath) as p:
            self._template = p.read()

        replacements = collections.OrderedDict()

        replacements['$verbosity'] = self.verbosity

        subshell = self._configurations[0][1][:2]
        subshell_occupation = self._configurations[0][1][2:]
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

        self.magneticFieldLineEdit.returnPressed.connect(
            self.updateMagneticField)

        self.e1GaussianLineEdit.returnPressed.connect(self.updateBroadening)
        self.e2GaussianLineEdit.returnPressed.connect(self.updateBroadening)

        self.kinLineEdit.returnPressed.connect(self.updateIncidentWaveVector)
        self.einLineEdit.returnPressed.connect(
            self.updateIncidentPolarizationVector)

        self.nPsisAutoCheckBox.toggled.connect(self.updateNPsisLineEditState)
        self.fkLineEdit.returnPressed.connect(self.updateScalingFactors)
        self.gkLineEdit.returnPressed.connect(self.updateScalingFactors)
        self.zetaLineEdit.returnPressed.connect(self.updateScalingFactors)

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
        self.magneticFieldLineEdit.setText(str(c.magneticField))

        if c._needsCompleteUiEnabled:
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
        if c._needsCompleteUiEnabled:
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
        c.magneticField = float(self.magneticFieldLineEdit.text())

        if c.magneticField == 0:
            c.hamiltonianState['Magnetic Field'] = 0
            c.calculateCD = 0
            self.calculateCDCheckBox.setChecked(False)
        else:
            c.hamiltonianState['Magnetic Field'] = 2
            c.calculateCD = 1
            self.calculateCDCheckBox.setChecked(True)

        configurations = c.hamiltonianData['Magnetic Field']
        for configuration in configurations:
            parameters = configurations[configuration]
            for i, parameter in enumerate(parameters):
                value = c.magneticField * -c.kin[i]
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
            c.e2Gaussian = float(self.e2GaussianLineEdit.text())
            self.resultsModel.replaceItem(index, c)
            try:
                self.plotSelectedCalculations(self.currentSpectrum)
            except AttributeError:
                self.plotSelectedCalculations(None)

    def updateIncidentWaveVector(self):
        timeout = 4000
        statusBar = self.parent().statusBar()

        c = self.calculation
        try:
            c.kin = self.stringToVector(self.kinLineEdit.text())
        except NullVectorError:
            message = 'The wave vector cannot be null.'
            statusBar.showMessage(message, timeout)
        except InvalidVectorError:
            message = 'Wrong expression given for the wave vector.'
            statusBar.showMessage(message, timeout)
        finally:
            self.updateMagneticField()
            self.updateUi()

    def updateIncidentPolarizationVector(self):
        timeout = 4000
        c = self.calculation
        statusBar = self.parent().statusBar()

        try:
            c.ein = self.stringToVector(self.einLineEdit.text())
        except NonPerpendicularVectorsError:
            message = ('The waven and polarization vectors need to be '
                       'perpendicular.')
            statusBar.showMessage(message, timeout)
        except NullVectorError:
            message = 'The polarization vector cannot be null.'
            statusBar.showMessage(message, timeout)
        except InvalidVectorError:
            message = 'Wrong expression given for the polarization vector.'
            statusBar.showMessage(message, timeout)
        finally:
            self.updateUi()

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

        # The wave and the polarization vectors have more complex update
        # mechanisms, and they are updated as soon as the user changes
        # them in the interface.

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

    def plot(self):
        plotWidget = self.parent().plotWidget
        statusBar = self.parent().statusBar()

        c = self.calculation
        data = c.spectra[self.currentSpectrum]

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
                message = 'Spectrum has very low intensity.'
                statusBar.showMessage(message, 4000)

            plotWidget.setGraphXLabel('Absorption Energy (eV)')
            plotWidget.setGraphYLabel('Absorption Cross Section (a.u.)')

            legend = c.label + ' | ' + c._uuid
            x = np.linspace(c.e1Min, c.e1Max, c.e1NPoints + 1)
            scale = (c.e1Max - c.e1Min) / c.e1NPoints
            y = data

            if c.e1Gaussian > 0.:
                fwhm = c.e1Gaussian / scale
                y = broaden(y, fwhm, 'gaussian')

            try:
                plotWidget.addCurve(x, y, legend)
            except AssertionError:
                message = 'The x and y arrays have different lengths.'
                timeout = 4000
                statusBar.showMessage(message, timeout)

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
        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'area-chart.svg')))
        self.spectraMenu = self.itemsContextMenu.addMenu(
            icon, 'Select Spectrum to Plot')
        self.itemsContextMenu.addSeparator()
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
        # Reset the plot widget.
        self.parent().plotWidget.reset()
        self.updateSpectraMenu()
        self.plotSelectedCalculations()
        self.updateUi()

    def plotSelectedCalculations(self, spectrum=None):
        if self.spectraMenu.isEmpty():
            return

        if not spectrum:
            action = self.spectraMenu.actions()[0]
            spectrum = action.text()

        # Updated the currently plotted spectrum.
        self.currentSpectrum = spectrum

        for calculation in self.selectedCalculations():
            self.calculation = copy.deepcopy(calculation)
            self.plot()

    def updateSpectraMenu(self):
        self.spectraMenu.clear()

        # Get the spectra available for the individual calculations.
        spectra = list()
        for calculation in self.selectedCalculations():
            spectra.append((set(calculation.spectra.keys())))

        # Find the common spectra among the calculations.
        try:
            spectra = sorted(set.intersection(*spectra))
        except TypeError:
            return

        if len(spectra) == 0:
            return

        for spectrum in spectra:
            action = QAction(spectrum, self)
            self.spectraMenu.addAction(action)
            action.triggered.connect(
                functools.partial(self.plotSelectedCalculations, spectrum))

    def updateResultsViewSelection(self):
        self.resultsView.selectionModel().clearSelection()
        index = self.resultsModel.index(self.resultsModel.rowCount() - 1)
        self.resultsView.selectionModel().select(
            index, QItemSelectionModel.Select)

    def handleOutputLogging(self):
        self.process.setReadChannel(QProcess.StandardOutput)
        data = self.process.readAllStandardOutput().data()
        data = data.decode('utf-8').rstrip()
        # data = data.decode('utf-8')
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
        return '[{0:.1g}, {1:.1g}, {2:.1g}]'.format(v[0], v[1], v[2])

    @staticmethod
    def stringToVector(s):
        match = re.match(r'\[(.+)\]', s)
        try:
            tokens = match.group(1)
        except AttributeError:
            raise(InvalidVectorError)

        tokens = tokens.split(',')

        try:
            v = np.array([tokens[0], tokens[1], tokens[2]], dtype=np.float64)
        except (ValueError, IndexError):
            raise(InvalidVectorError)
        else:
            return(v)


if __name__ == '__main__':
    pass
