# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2018 European Synchrotron Radiation Facility
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
__date__ = '23/03/2018'


import collections
import copy
import datetime
import errno
import gzip
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

from PyQt5.QtCore import (
    QItemSelectionModel, QProcess, Qt, QPoint, QStandardPaths)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAbstractItemView, QDockWidget, QFileDialog, QAction, QMenu,
    QWidget, QDialog)
from PyQt5.uic import loadUi
from silx.resources import resource_filename as resourceFileName

from .models.treemodel import TreeModel
from .models.listmodel import ListModel
from ..utils.broaden import broaden


class odict(collections.OrderedDict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


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
        'nConfigurations': 1,
        'fk': 0.8,
        'gk': 0.8,
        'zeta': 1.0,
        'baseName': 'untitled',
        'spectra': None,
        'uuid': None,
        'startingTime': None,
        'endingTime': None,
        'verbosity': None,
    }

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        self.__dict__.update(kwargs)

        path = resourceFileName(
            'crispy:' + os.path.join('modules', 'quanty', 'parameters',
                                     'parameters.json.gz'))

        with gzip.open(path, 'rb') as p:
            tree = json.loads(
                p.read().decode('utf-8'), object_pairs_hook=odict)

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
        self.block = self.configurations[0][1][:2]
        self.nElectrons = int(self.configurations[0][1][2:])
        self.nPsis = branch['number of states']
        self.nPsisMax = self.nPsis
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

        self.hamiltonianData = odict()
        self.hamiltonianState = odict()

        branch = tree['elements'][self.element]['charges'][self.charge]

        for label, configuration in self.configurations:
            label = '{} Hamiltonian'.format(label)
            terms = branch['configurations'][configuration]['terms']

            for term in terms:
                # Include the magnetic and exchange terms only for
                # selected type of calculations.
                if 'Magnetic Field' in term or 'Exchange Field' in term:
                    if not (('L2,3 (2p)' in self.edge and 'd' in self.block) or
                       ('M4,5 (3d)' in self.edge and 'f' in self.block)):
                            continue

                # Include the p-d hybridization term only for K-edges.
                if '3d-4p Hybridization' in term:
                    if 'K (1s)' not in self.edge:
                        continue

                if ('Atomic' in term or 'Magnetic Field' in term
                        or 'Exchange Field' in term):
                    parameters = terms[term]
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

        replacements = odict()

        replacements['$Verbosity'] = self.verbosity
        replacements['$NConfigurations'] = self.nConfigurations

        subshell = self.configurations[0][1][:2]
        subshell_occupation = self.configurations[0][1][2:]
        replacements['$NElectrons_{}'.format(subshell)] = subshell_occupation

        replacements['$T'] = self.temperature

        replacements['$Emin1'] = self.e1Min
        replacements['$Emax1'] = self.e1Max
        replacements['$NE1'] = self.e1NPoints
        replacements['$Eedge1'] = self.e1Edge

        if len(self.e1Lorentzian) == 1:
            if (('L2,3 (2p)' in self.edge and 'd' in self.block) or
               ('M4,5 (3d)' in self.edge and 'f' in self.block)):
                replacements['$Gamma1'] = '0.1'
                replacements['$Gmin1'] = self.e1Lorentzian[0]
                replacements['$Gmax1'] = self.e1Lorentzian[0]
                replacements['$Egamma1'] = (
                    (self.e1Max - self.e1Min) / 2 + self.e1Min)
            else:
                replacements['$Gamma1'] = self.e1Lorentzian[0]
        else:
            if (('L2,3 (2p)' in self.edge and 'd' in self.block) or
               ('M4,5 (3d)' in self.edge and 'f' in self.block)):
                replacements['$Gamma1'] = 0.1
                replacements['$Gmin1'] = self.e1Lorentzian[0]
                replacements['$Gmax1'] = self.e1Lorentzian[1]
                if len(self.e1Lorentzian) == 2:
                    replacements['$Egamma1'] = (
                        (self.e1Max - self.e1Min) / 2 + self.e1Min)
                else:
                    replacements['$Egamma1'] = self.e1Lorentzian[2]
            else:
                pass

        s = '{{{0:.6g}, {1:.6g}, {2:.6g}}}'
        u = self.kin / np.linalg.norm(self.kin)
        replacements['$kin'] = s.format(u[0], u[1], u[2])

        v = self.ein / np.linalg.norm(self.ein)
        replacements['$ein1'] = s.format(v[0], v[1], v[2])

        # Generate a second, perpendicular, polarization vector to the plane
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
            replacements['$Gamma2'] = self.e2Lorentzian[0]

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

        self.uuid = uuid.uuid4().hex[:8]


class QuantyDockWidget(QDockWidget):

    def __init__(self):
        super(QuantyDockWidget, self).__init__()

        # Load the external .ui file for the widget.
        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'quanty', 'main.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.calculation = QuantyCalculation()
        self.setUi()
        self.updateUi()
        self.loadSettings()

    def setUi(self):
        # Create the results model and assign it to the view.
        self.resultsModel = ListModel()

        self.resultsView.setModel(self.resultsModel)
        self.resultsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.resultsView.selectionModel().selectionChanged.connect(
            self.selectedCalculationsChanged)
        # Add a context menu.
        self.resultsView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.resultsView.customContextMenuRequested[QPoint].connect(
            self.showResultsContextMenu)

        # Add the preferences dialog.
        self.preferencesDialog = QuantyPreferencesDialog()
        self.preferencesDialog.setModal(True)

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

        self.fkLineEdit.editingFinished.connect(self.updateScalingFactors)
        self.gkLineEdit.editingFinished.connect(self.updateScalingFactors)
        self.zetaLineEdit.editingFinished.connect(self.updateScalingFactors)

        self.syncParametersCheckBox.toggled.connect(
            self.updateSyncParametersState)

        self.nPsisAutoCheckBox.toggled.connect(self.updateNPsisLineEditState)
        self.nConfigurationsLineEdit.editingFinished.connect(
            self.updateConfigurations)

        self.plotIsoCheckBox.toggled.connect(self.plotSelectedCalculations)
        self.plotCDCheckBox.toggled.connect(self.plotSelectedCalculations)
        self.plotLDCheckBox.toggled.connect(self.plotSelectedCalculations)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'save.svg')))
        self.saveInputAsPushButton.setIcon(icon)
        self.saveInputAsPushButton.clicked.connect(self.saveInputAs)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'play.svg')))
        self.calculationPushButton.setIcon(icon)
        self.calculationPushButton.clicked.connect(self.runCalculation)

        self.resultsModel.dataChanged.connect(self.plotSelectedCalculations)

        self.preferencesDialog.pathBrowsePushButton.clicked.connect(
            self.setQuantyPath)

    def updateUi(self):
        c = self.calculation

        self.elementComboBox.setItems(c.elements, c.element)
        self.chargeComboBox.setItems(c.charges, c.charge)
        self.symmetryComboBox.setItems(c.symmetries, c.symmetry)
        self.experimentComboBox.setItems(c.experiments, c.experiment)
        self.edgeComboBox.setItems(c.edges, c.edge)

        self.temperatureLineEdit.setValue(c.temperature)
        self.magneticFieldLineEdit.setValue(c.magneticField)

        if (('L2,3 (2p)' in c.edge and 'd' in c.block) or
           ('M4,5 (3d)' in c.edge and 'f' in c.block)):
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

        self.kinLineEdit.setVector(c.kin)
        self.einLineEdit.setVector(c.ein)

        self.calculateIsoCheckBox.setChecked(c.calculateIso)
        self.calculateCDCheckBox.setChecked(c.calculateCD)
        self.calculateLDCheckBox.setChecked(c.calculateLD)

        self.fkLineEdit.setValue(c.fk)
        self.gkLineEdit.setValue(c.gk)
        self.zetaLineEdit.setValue(c.zeta)

        self.nPsisLineEdit.setValue(c.nPsis)
        self.nPsisAutoCheckBox.setChecked(c.nPsisAuto)
        self.nConfigurationsLineEdit.setValue(c.nConfigurations)

        self.nConfigurationsLineEdit.setEnabled(False)
        termName = '{}-Ligands Hybridization'.format(c.block)
        if termName in c.hamiltonianData:
            termState = c.hamiltonianState[termName]
            if termState != 0:
                self.nConfigurationsLineEdit.setEnabled(True)

        self.energiesTabWidget.setTabText(0, str(c.e1Label))
        self.e1MinLineEdit.setValue(c.e1Min)
        self.e1MaxLineEdit.setValue(c.e1Max)
        self.e1NPointsLineEdit.setValue(c.e1NPoints)
        self.e1LorentzianLineEdit.setList(c.e1Lorentzian)
        self.e1GaussianLineEdit.setValue(c.e1Gaussian)

        if 'RIXS' in c.experiment:
            if self.energiesTabWidget.count() == 1:
                tab = self.energiesTabWidget.findChild(QWidget, 'e2Tab')
                self.energiesTabWidget.addTab(tab, tab.objectName())
                self.energiesTabWidget.setTabText(1, c.e2Label)
            self.e2MinLineEdit.setValue(c.e2Min)
            self.e2MaxLineEdit.setValue(c.e2Max)
            self.e2NPointsLineEdit.setValue(c.e2NPoints)
            self.e2LorentzianLineEdit.setList(c.e2Lorentzian)
            self.e2GaussianLineEdit.setValue(c.e2Gaussian)
        else:
            self.energiesTabWidget.removeTab(1)

        # Create a Hamiltonian model.
        self.hamiltonianModel = TreeModel(
            ('Parameter', 'Value', 'Scaling'), c.hamiltonianData)
        self.hamiltonianModel.setNodesCheckState(c.hamiltonianState)
        if self.syncParametersCheckBox.isChecked():
            self.hamiltonianModel.setSyncState(True)
        else:
            self.hamiltonianModel.setSyncState(False)
        self.hamiltonianModel.nodeCheckStateChanged.connect(
            self.updateConfigurations)

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
        self.hamiltonianSplitter.setSizes((150, 300, 0))

    def enableUi(self, flag=True):
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
        if (('L2,3 (2p)' in c.edge and 'd' in c.block) or
           ('M4,5 (3d)' in c.edge and 'f' in c.block)):
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

        self.fkLineEdit.setEnabled(flag)
        self.gkLineEdit.setEnabled(flag)
        self.zetaLineEdit.setEnabled(flag)

        self.nPsisAutoCheckBox.setEnabled(flag)
        if self.nPsisAutoCheckBox.isChecked():
            self.nPsisLineEdit.setEnabled(False)
        else:
            self.nPsisLineEdit.setEnabled(flag)

        self.nConfigurationsLineEdit.setEnabled(flag)

        self.hamiltonianTermsView.setEnabled(flag)
        self.hamiltonianParametersView.setEnabled(flag)
        self.resultsView.setEnabled(flag)

        self.saveInputAsPushButton.setEnabled(flag)

    def updateMagneticField(self):
        c = self.calculation

        magneticField = self.magneticFieldLineEdit.getValue()

        if magneticField == 0:
            c.hamiltonianState['Magnetic Field'] = 0
            self.calculateCDCheckBox.setChecked(False)
        else:
            c.hamiltonianState['Magnetic Field'] = 2
            self.calculateCDCheckBox.setChecked(True)

        kin = c.kin
        kin = kin / np.linalg.norm(kin)

        configurations = c.hamiltonianData['Magnetic Field']
        for configuration in configurations:
            parameters = configurations[configuration]
            for i, parameter in enumerate(parameters):
                value = magneticField * -kin[i]
                if abs(value) == 0.0:
                    value = 0.0
                configurations[configuration][parameter] = (value, str())
        self.hamiltonianModel.updateModelData(c.hamiltonianData)
        self.hamiltonianModel.setNodesCheckState(c.hamiltonianState)

    def updateBroadening(self):
        c = self.calculation

        if not c.spectra:
            return

        try:
            index = list(self.resultsView.selectedIndexes())[-1]
        except IndexError:
            return
        else:
            c.e1Gaussian = self.e1GaussianLineEdit.getValue()
            if 'RIXS' in c.experiment:
                c.e2Gaussian = self.e2GaussianLineEdit.getValue()
            self.resultsModel.replaceItem(index, c)
            self.plotSelectedCalculations()

    def updateIncidentWaveVector(self):
        c = self.calculation

        statusBar = self.parent().statusBar()
        timeout = 4000

        try:
            kin = self.kinLineEdit.getVector()
        except ValueError:
            message = ('Wrong expression given for the wave vector. '
                       'Resetting the previous value.')
            statusBar.showMessage(message, timeout)
            self.kinLineEdit.setVector(c.kin)
            return

        if np.all(kin == 0):
            message = 'The wave vector cannot be null.'
            statusBar.showMessage(message, timeout)
            self.kinLineEdit.setVector(c.kin)
            return
        else:
            c.kin = kin

        # No need for a try/except block. The polarization vector must be
        # correct.
        ein = self.einLineEdit.getVector()

        # Check if the wave and polarization vectors are perpendicular.
        if np.dot(kin, ein) != 0:
            # Determine a possible perpendicular vector.
            if kin[2] != 0 or (-kin[0] - kin[1]) != 0:
                ein = np.array([kin[2], kin[2], -kin[0] - kin[1]])
            else:
                ein = np.array([-kin[2] - kin[1], kin[0], kin[0]])

        c.ein = ein
        self.einLineEdit.setVector(ein)

    def updateIncidentPolarizationVector(self):
        c = self.calculation
        statusBar = self.parent().statusBar()
        timeout = 4000

        try:
            ein = self.einLineEdit.getVector()
        except ValueError:
            message = ('Wrong expression given for the polarization vector. '
                       'Resetting the previous value.')
            statusBar.showMessage(message, timeout)
            self.einLineEdit.setVector(c.ein)
            return

        kin = c.kin

        if np.all(ein == 0):
            message = 'The polarization vector cannot be null.'
            statusBar.showMessage(message, timeout)
            self.einLineEdit.setVector(c.ein)
            return
        elif np.dot(kin, ein) != 0:
            message = ('The wave and polarization vectors need to be '
                       'perpendicular.')
            statusBar.showMessage(message, timeout)
            self.einLineEdit.setVector(c.ein)
            return
        else:
            c.ein = ein

    def updateScalingFactors(self):
        c = self.calculation
        c.hamiltonianData = self.hamiltonianModel.getModelData()

        c.fk = self.fkLineEdit.getValue()
        c.gk = self.gkLineEdit.getValue()
        c.zeta = self.zetaLineEdit.getValue()

        terms = c.hamiltonianData

        for term in terms:
            if 'Atomic' not in term:
                continue
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
        self.hamiltonianModel.updateModelData(c.hamiltonianData)
        # No idea why this is needed. Both views should update after the above
        # function call.
        self.hamiltonianParametersView.viewport().repaint()
        self.hamiltonianTermsView.viewport().repaint()

    def updateNPsisLineEditState(self):
        nPsisMax = self.calculation.nPsisMax

        if self.nPsisAutoCheckBox.isChecked():
            self.nPsisLineEdit.setEnabled(False)
            self.nPsisLineEdit.setText(nPsisMax)
        else:
            self.nPsisLineEdit.setEnabled(True)

    def updateSyncParametersState(self, flag):
        self.hamiltonianModel.setSyncState(flag)

    def updateConfigurations(self, *args):
        c = self.calculation
        nConfigurations = self.nConfigurationsLineEdit.getValue()

        if args:
            index, state = args
            if '{}-Ligands Hybridization'.format(c.block) in index.data():
                if state == 0:
                    nConfigurations = 1
                    self.nConfigurationsLineEdit.setEnabled(False)
                elif state == 2:
                    nConfigurations = 2
                    self.nConfigurationsLineEdit.setEnabled(True)
        else:
            if 'd' in c.block:
                nConfigurationsMax = 10 - c.nElectrons + 1
            elif 'f' in c.block:
                nConfigurationsMax = 14 - c.nElectrons + 1
            if nConfigurations > nConfigurationsMax:
                nConfigurations = nConfigurationsMax

        c.nConfigurations = nConfigurations
        self.nConfigurationsLineEdit.setValue(nConfigurations)

    def saveInput(self):
        self.updateCalculation()
        statusBar = self.parent().statusBar()
        try:
            self.calculation.saveInput()
        except (IOError, OSError) as e:
            message = 'Cannot write the Quanty input file.'
            statusBar.showMessage(message)
            return

    def saveInputAs(self):
        c = self.calculation
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Quanty Input',
            os.path.join(self.settings['currentPath'], '{}.lua'.format(
                c.baseName)), 'Quanty Input File (*.lua)')

        if path:
            self.updateSettings('currentPath', os.path.dirname(path))
            self.calculation.baseName, _ = os.path.splitext(
                    os.path.basename(path))
            self.updateMainWindowTitle()
            os.chdir(os.path.dirname(path))
            self.saveInput()

    def saveCalculationsAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Calculations',
            os.path.join(self.settings['currentPath'], 'untitled.pkl'),
            'Pickle File (*.pkl)')

        if path:
            self.updateSettings('currentPath', os.path.dirname(path))
            os.chdir(os.path.dirname(path))
            calculations = copy.deepcopy(self.resultsModel.getData())
            calculations.reverse()
            with open(path, 'wb') as p:
                pickle.dump(calculations, p, pickle.HIGHEST_PROTOCOL)

    def saveSelectedCalculationsAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Calculations',
            os.path.join(self.settings['currentPath'], 'untitled.pkl'),
            'Pickle File (*.pkl)')

        if path:
            self.updateSettings('currentPath', os.path.dirname(path))
            os.chdir(os.path.dirname(path))
            calculations = self.selectedCalculations()
            calculations.reverse()
            with open(path, 'wb') as p:
                pickle.dump(calculations, p, pickle.HIGHEST_PROTOCOL)

    def updateCalculation(self):
        c = copy.deepcopy(self.calculation)

        c.temperature = self.temperatureLineEdit.getValue()
        c.magneticField = self.magneticFieldLineEdit.getValue()

        c.calculateIso = int(self.calculateIsoCheckBox.isChecked())
        c.calculateCD = int(self.calculateCDCheckBox.isChecked())
        c.calculateLD = int(self.calculateLDCheckBox.isChecked())

        c.e1Min = self.e1MinLineEdit.getValue()
        c.e1Max = self.e1MaxLineEdit.getValue()
        c.e1NPoints = self.e1NPointsLineEdit.getValue()
        c.e1Lorentzian = self.e1LorentzianLineEdit.getList()
        c.e1Gaussian = self.e1GaussianLineEdit.getValue()

        c.kin = self.kinLineEdit.getVector()
        c.ein = self.einLineEdit.getVector()

        if 'RIXS' in c.experiment:
            c.e2Min = self.e2MinLineEdit.getValue()
            c.e2Max = self.e2MaxLineEdit.getValue()
            c.e2NPoints = self.e2NPointsLineEdit.getValue()
            c.e2Lorentzian = self.e2LorentzianLineEdit.getList()
            c.e2Gaussian = self.e2GaussianLineEdit.getValue()

        c.nPsis = self.nPsisLineEdit.getValue()
        c.nPsisAuto = int(self.nPsisAutoCheckBox.isChecked())
        c.nConfigurations = self.nConfigurationsLineEdit.getValue()

        c.hamiltonianData = self.hamiltonianModel.getModelData()
        c.hamiltonianState = self.hamiltonianModel.getNodesCheckState()

        c.spectra = dict()

        c.verbosity = self.preferencesDialog.verbosityLineEdit.text()

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

    def removeCalculations(self):
        self.resultsModel.reset()
        self.parent().plotWidget.reset()

    def loadCalculations(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Load Calculations',
            self.settings['currentPath'], 'Pickle File (*.pkl)')

        if path:
            self.updateSettings('currentPath', os.path.dirname(path))
            with open(path, 'rb') as p:
                self.resultsModel.appendItems(pickle.load(p))
            self.updateResultsViewSelection()
            self.updateMainWindowTitle()
            self.quantyToolBox.setCurrentWidget(self.resultsPage)

    def setQuantyPath(self):
        if not self.settings['quantyPath']:
            quantyPath = os.path.expanduser('~')
        else:
            quantyPath = self.settings['quantyPath']

        path, _ = QFileDialog.getOpenFileName(
            self, 'Select File', quantyPath)

        if path:
            path = os.path.dirname(path)
            self.updateSettings('quantyPath', path)
            self.preferencesDialog.pathLineEdit.setText(path)

    def getQuantyPath(self):
        if self.settings['quantyPath']:
            return

        # Check if Quanty is in the paths defined in the $PATH.
        path = QStandardPaths.findExecutable(self.settings['quantyExecutable'])
        if path:
            self.settings['quantyPath'] = os.path.dirname(path)
            self.updateSettings('quantyPath', os.path.dirname(path))
            return

        # Check if Quanty is bundled with Crispy.
        path = QStandardPaths.findExecutable(
            self.settings['quantyExecutable'],
            [resourceFileName(
                'crispy:' + os.path.join('modules', 'quanty', 'bin'))])
        if path:
            self.settings['quantyPath'] = os.path.dirname(path)
            self.updateSettings('quantyPath', os.path.dirname(path))
            return

    def runCalculation(self):
        self.getQuantyPath()

        statusBar = self.parent().statusBar()
        if not self.settings['quantyPath']:
            message = 'The path of the Quanty executable is not set.'
            statusBar.showMessage(message)
            return

        command = os.path.join(
            self.settings['quantyPath'], self.settings['quantyExecutable'])

        # Test the executable.
        with open(os.devnull, 'w') as f:
            try:
                subprocess.call(command, stdout=f, stderr=f)
            except OSError as e:
                if e.errno == os.errno.ENOENT:
                    message = 'The Quanty executable was not found.'
                    statusBar.showMessage(message)
                    return
                else:
                    raise

        # Change to the working directory.
        os.chdir(self.settings['currentPath'])

        # Write the input file to disk.
        self.saveInput()

        self.parent().splitter.setSizes((450, 150))

        # Disable the UI while the calculation is running.
        self.enableUi(False)

        c = self.calculation
        c.startingTime = datetime.datetime.now()

        if not hasattr(self, 'counter'):
            self.counter = 1

        # Run Quanty using QProcess.
        self.process = QProcess()

        self.process.start(command, (c.baseName + '.lua', ))
        message = (
            'Running "{} {}" in {}.'.format(
                self.settings['quantyExecutable'],
                c.baseName + '.lua', os.getcwd()))
        statusBar.showMessage(message)

        if sys.platform in 'win32' and self.process.waitForStarted():
            self.updateCalculationPushButton()
        else:
            self.process.started.connect(self.updateCalculationPushButton)
        self.process.readyReadStandardOutput.connect(self.handleOutputLogging)
        self.process.finished.connect(self.processCalculation)

    def updateCalculationPushButton(self, type='stop'):
        types = {
            'stop': {
                'iconName': 'stop.svg',
                'buttonText': 'Stop',
                'buttonToolTip': 'Stop Quanty.'},
            'run': {
                'iconName': 'play.svg',
                'buttonText': 'Run',
                'buttonToolTip': 'Run Quanty.'},
        }

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', types[type]['iconName'])))
        self.calculationPushButton.setIcon(icon)

        self.calculationPushButton.setText(types[type]['buttonText'])
        self.calculationPushButton.setToolTip(types[type]['buttonToolTip'])

        self.calculationPushButton.disconnect()
        if type == 'stop':
            self.calculationPushButton.clicked.connect(self.stopCalculation)
        elif type == 'run':
            self.calculationPushButton.clicked.connect(self.runCalculation)
        else:
            pass

    def stopCalculation(self):
        self.process.kill()
        self.enableUi(True)

    def processCalculation(self):
        c = self.calculation

        # When did I finish?
        c.endingTime = datetime.datetime.now()

        # Reset the calculation button.
        self.updateCalculationPushButton('run')

        # Re-enable the UI if the calculation has finished.
        self.enableUi(True)

        # Evaluate the exit code and status of the process.
        exitStatus = self.process.exitStatus()
        exitCode = self.process.exitCode()
        timeout = 8000
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
            message = (
                'Quanty has finished unsuccessfully. '
                'Check the logging window for more details.')
            statusBar.showMessage(message, timeout)
            return
        # exitCode is platform dependent; exitStatus is always 1.
        elif exitStatus == 1:
            message = 'Quanty was stopped.'
            statusBar.showMessage(message, timeout)
            return

        c.label = '#{} | {} | {} | {} | {} | {}'.format(
            self.counter, c.element, c.charge, c.symmetry, c.experiment,
            c.edge)

        self.counter += 1

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
            except IOError as e:
                continue

            if 'RIXS' in c.experiment:
                c.spectra[spectrum] = -data[:, 2::2]
            else:
                c.spectra[spectrum] = -data[:, 2::2][:, 0]

        # Store the calculation in the model.
        self.resultsModel.appendItems([c])

        # Should this be a signal?
        self.updateResultsViewSelection()

        # If the "Hamiltonian Setup" page is currently selected, when the
        # current widget is set to the "Results Page", the former is not
        # displayed. To avoid this I switch first to the "General Setup" page.
        self.quantyToolBox.setCurrentWidget(self.generalPage)
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
            # Keep the aspect ratio for RIXS plots.
            plotWidget.setKeepDataAspectRatio(flag=True)
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
            plotWidget.setKeepDataAspectRatio(flag=False)
            # Check if the data is valid.
            if np.max(np.abs(data)) < np.finfo(np.float32).eps:
                message = 'The {} spectrum has very low intensity.'.format(
                    spectrumName)
                statusBar.showMessage(message)

            plotWidget.setGraphXLabel('Absorption Energy (eV)')
            plotWidget.setGraphYLabel('Absorption Cross Section (a.u.)')

            legend = '{} | {} | {}'.format(
                c.label.split()[0], spectrumName, c.uuid)
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

    def selectedHamiltonianTermChanged(self):
        index = self.hamiltonianTermsView.currentIndex()
        self.hamiltonianParametersView.setRootIndex(index)

    def showResultsContextMenu(self, position):
        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'save.svg')))
        self.saveSelectedCalculationsAsAction = QAction(
            icon, 'Save Selected Calculations As...', self,
            triggered=self.saveSelectedCalculationsAs)
        self.saveCalculationsAsAction = QAction(
            icon, 'Save Calculations As...', self,
            triggered=self.saveCalculationsAs)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'trash.svg')))
        self.removeSelectedCalculationsAction = QAction(
            icon, 'Remove Selected Calculations', self,
            triggered=self.removeSelectedCalculations)
        self.removeCalculationsAction = QAction(
            icon, 'Remove Calculations', self,
            triggered=self.removeCalculations)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'folder-open.svg')))
        self.loadCalculationsAction = QAction(
            icon, 'Load Calculations', self,
            triggered=self.loadCalculations)

        self.resultsContextMenu = QMenu('Results Context Menu', self)
        self.resultsContextMenu.addAction(
            self.saveSelectedCalculationsAsAction)
        self.resultsContextMenu.addAction(
            self.removeSelectedCalculationsAction)
        self.resultsContextMenu.addSeparator()
        self.resultsContextMenu.addAction(self.saveCalculationsAsAction)
        self.resultsContextMenu.addAction(self.removeCalculationsAction)
        self.resultsContextMenu.addAction(self.loadCalculationsAction)

        if not self.resultsView.selectedIndexes():
            self.removeSelectedCalculationsAction.setEnabled(False)
            self.saveSelectedCalculationsAsAction.setEnabled(False)

        if not self.resultsModel.getData():
            self.saveCalculationsAsAction.setEnabled(False)
            self.removeCalculationsAction.setEnabled(False)

        self.resultsContextMenu.exec_(self.resultsView.mapToGlobal(position))

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
        # Update available actions in the main menu.
        if not self.resultsModel.getData():
            self.parent().updateMenuModulesQuanty(False)
        else:
            self.parent().updateMenuModulesQuanty(True)

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

    def getAppConfigLocation(self):
        root = QStandardPaths.standardLocations(
            QStandardPaths.GenericConfigLocation)[0]

        if sys.platform in ('win32', 'darwin'):
            path = os.path.join(root, 'Crispy')
        else:
            path = os.path.join(root, 'crispy')

        return path

    def saveSettings(self):
        if not hasattr(self, 'settings'):
            return

        path = self.getAppConfigLocation()

        try:
            os.makedirs(path, mode=0o755)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        settingsPath = os.path.join(path, 'settings.json')

        with open(settingsPath, 'w') as p:
            json.dump(self.settings, p)

    def loadSettings(self):
        settingsPath = os.path.join(
            self.getAppConfigLocation(), 'settings.json')

        try:
            with open(settingsPath, 'r') as p:
                self.settings = json.loads(
                    p.read(), object_pairs_hook=odict)
        except IOError as e:
            self.settings = odict()
            self.settings['quantyPath'] = None
            self.settings['currentPath'] = os.path.expanduser('~')
            if sys.platform in 'win32':
                self.settings['quantyExecutable'] = 'Quanty.exe'
            else:
                self.settings['quantyExecutable'] = 'Quanty'

    def updateSettings(self, setting, value):
        self.settings[setting] = value
        self.saveSettings()

    def openPreferencesDialog(self):
        quantyPath = self.settings['quantyPath']
        self.preferencesDialog.pathLineEdit.setText(quantyPath)
        self.preferencesDialog.show()


class QuantyPreferencesDialog(QDialog):

    def __init__(self, parent=None):
        super(QuantyPreferencesDialog, self).__init__()

        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'quanty', 'preferences.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')


if __name__ == '__main__':
    pass
