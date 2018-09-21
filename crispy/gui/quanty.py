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
__date__ = '21/09/2018'


import copy
import datetime
import gzip
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

from PyQt5.QtCore import (
    QItemSelectionModel, QProcess, Qt, QPoint, QStandardPaths)
from PyQt5.QtGui import QIcon, QFontDatabase
from PyQt5.QtWidgets import (
    QDockWidget, QFileDialog, QAction, QMenu, QWidget,
    QDialog, QDialogButtonBox)
from PyQt5.uic import loadUi
from silx.resources import resource_filename as resourceFileName

from .models import HamiltonianModel, ResultsModel, SpectraModel
from ..utils.broaden import broaden
from ..utils.odict import odict
from ..version import version
from ..utils.profiling import timeit # noqa


class Spectrum1D(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, values):
        # Check for very small values.
        valuesMax = np.max(np.abs(values))
        if valuesMax < np.finfo(np.float32).eps:
            values = np.zeros_like(values)
        self._y = values

    @property
    def xScale(self):
        return np.abs(self.x.min() - self.x.max()) / self.x.shape[0]

    def broaden(self, broadenings):
        for kind in broadenings:
            if kind == 'gaussian':
                fwhm, = broadenings[kind]
                fwhm = fwhm / self.xScale
                self.y = broaden(self.y, fwhm, kind)

    def shift(self, values):
        value, _ = values
        self.x = self.x + value

    def scale(self, value):
        self.y = self.y * value

    def normalization(self, value):
        if value == 'None':
            return
        elif value == 'Maximum':
            maximum = np.abs(self.y).max()
            self.y = self.y / maximum
        elif value == 'Area':
            area = np.trapz(self.y, self.x)
            self.y = self.y / area


class QuantySpectra(object):

    aliases = {'Isotropic': 'Isotropic',
               'Circular Dichroism': 'Circular Dichroism (R-L)',
               'Linear Dichroism': 'Linear Dichroism (V-H)'}

    _defaults = {
        'scale': 1.0,
        'shift': (0.0, 0.0),
        'broadenings': dict(),
        'normalization': 'None',
    }

    def __init__(self):
        self._toCalculateChecked = None
        self._toPlotChecked = None

        self.__dict__.update(self._defaults)

    @property
    def toPlot(self):
        spectraNames = list()
        for spectrum in self.toCalculateChecked:
            if spectrum == 'Isotropic':
                spectraNames.append(self.aliases[spectrum])
            if spectrum == 'Circular Dichroism':
                spectraNames.append(self.aliases[spectrum])
                spectraNames.append('Right Polarized (R)')
                spectraNames.append('Left Polarized (L)')
            elif spectrum == 'Linear Dichroism':
                spectraNames.append(self.aliases[spectrum])
                spectraNames.append('Vertical Polarized (V)')
                spectraNames.append('Horizontal Polarized (H)')
        return spectraNames

    @property
    def toCalculateChecked(self):
        return self._toCalculateChecked

    @toCalculateChecked.setter
    def toCalculateChecked(self, values):
        self._toCalculateChecked = values
        spectraNames = list()
        for spectrum in values:
            if spectrum in (
                    'Isotropic', 'Circular Dichroism', 'Linear Dichroism'):
                spectraNames.append(self.aliases[spectrum])
            self.toPlotChecked = spectraNames

    @property
    def toPlotChecked(self):
        return self._toPlotChecked

    @toPlotChecked.setter
    def toPlotChecked(self, values):
        self._toPlotChecked = values

    def process(self):
        try:
            self.processed = copy.deepcopy(self.raw)
        except AttributeError:
            return

        for spectrum in self.processed:
            if self.broadenings:
                spectrum.broaden(self.broadenings)
            if self.scale != self._defaults['scale']:
                spectrum.scale(self.scale)
            if self.shift != self._defaults['shift']:
                spectrum.shift(self.shift)
            spectrum.normalization(self.normalization)

    def loadFromDisk(self, calculation):
        """
        Read the spectra from the files generated by Quanty and store them
        as a list of spectum objects.
        """

        suffixes = {
            'Isotropic': 'iso',
            'Circular Dichroism (R-L)': 'cd',
            'Right Polarized (R)': 'r',
            'Left Polarized (L)': 'l',
            'Linear Dichroism (V-H)': 'ld',
            'Vertical Polarized (V)': 'v',
            'Horizontal Polarized (H)': 'h',
        }

        self.raw = list()
        for spectrumName in self.toPlot:
            suffix = suffixes[spectrumName]
            path = '{}_{}.spec'.format(calculation.baseName, suffix)

            try:
                data = np.loadtxt(path, skiprows=5)
            except (OSError, IOError) as e:
                raise e

            rows, columns = data.shape

            if calculation.experiment in ('XAS', 'XPS'):
                xMin = calculation.xMin
                xMax = calculation.xMax
                xNPoints = calculation.xNPoints

                x = np.linspace(xMin, xMax, xNPoints + 1)
                y = data[:, 2::2].flatten()

                spectrum = Spectrum1D(x, y)

                spectrum.name = spectrumName
                if len(suffix) > 2:
                    spectrum.shortName = suffix.title()
                else:
                    spectrum.shortName = suffix.upper()

                if calculation.experiment == 'XAS':
                    spectrum.xLabel = 'Absorption Energy (eV)'
                elif calculation.experiment == 'XPS':
                    spectrum.xLabel = 'Binding Energy (eV)'
                spectrum.yLabel = 'Intensity (a.u.)'

                self.broadenings = {'gaussian': (calculation.xGaussian, ), }
            else:
                pass
                # return data[:, 2::2][:, 0]
            self.raw.append(spectrum)

        # Process the spectra once they where read from disk.
        self.process()
        self.__dict__.update(self._defaults)


class QuantyCalculation(object):

    _defaults = odict(
        [
            ('version', version),
            ('element', 'Ni'),
            ('charge', '2+'),
            ('symmetry', 'D4h'),
            ('experiment', 'XAS'),
            ('edge', 'K (1s)'),
            ('temperature', 10.0),
            ('magneticField', 0.0),
            ('xMin', None),
            ('xMax', None),
            ('xNPoints', None),
            ('xLorentzian', None),
            ('xGaussian', None),
            ('k1', [0, 0, 1]),
            ('eps11', [0, 1, 0]),
            ('eps12', [1, 0, 0]),
            ('yMin', None),
            ('yMax', None),
            ('yNPoints', None),
            ('yLorentzian', None),
            ('yGaussian', None),
            ('k2', [0, 0, 0]),
            ('eps21', [0, 0, 0]),
            ('eps22', [0, 0, 0]),
            ('spectra', None),
            ('nPsisAuto', 1),
            ('nConfigurations', 1),
            ('fk', 0.8),
            ('gk', 0.8),
            ('zeta', 1.0),
            ('hamiltonianData', None),
            ('hamiltonianState', None),
            ('baseName', 'untitled'),
            ('spectrum', None),
            ('startingTime', None),
            ('endingTime', None),
            ('verbosity', None),
            ('isChecked', True),
            ('input', None),
            ('output', None),
        ]
    )

    # Make the parameters a class attribute. This speeds up the creation
    # of a new calculation object; significantly.
    path = resourceFileName(
        'crispy:' + os.path.join('modules', 'quanty', 'parameters',
                                 'parameters.json.gz'))

    with gzip.open(path, 'rb') as p:
        parameters = json.loads(
            p.read().decode('utf-8'), object_pairs_hook=odict)

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        self.__dict__.update(kwargs)

        parameters = self.parameters

        branch = parameters['elements']
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
        self.hamiltonianTerms = branch['hamiltonian terms']

        self.xLabel = branch['axes'][0][0]
        self.xMin = branch['axes'][0][1]
        self.xMax = branch['axes'][0][2]
        self.xNPoints = branch['axes'][0][3]
        self.xEdge = branch['axes'][0][4]
        self.xLorentzian = branch['axes'][0][5]
        self.xGaussian = branch['axes'][0][6]

        if self.experiment == 'RIXS':
            self.yLabel = branch['axes'][1][0]
            self.yMin = branch['axes'][1][1]
            self.yMax = branch['axes'][1][2]
            self.yNPoints = branch['axes'][1][3]
            self.yEdge = branch['axes'][1][4]
            self.yLorentzian = branch['axes'][1][5]
            self.yGaussian = branch['axes'][1][6]

        self.spectra = QuantySpectra()

        if self.experiment == 'XAS':
            self.spectra.toCalculate = [
                'Isotropic', 'Circular Dichroism', 'Linear Dichroism']
        else:
            self.spectra.toCalculate = ['Isotropic']
        self.spectra.toCalculateChecked = ['Isotropic']

        if self.hamiltonianData is None:
            self.hamiltonianData = odict()

        if self.hamiltonianState is None:
            self.hamiltonianState = odict()

        self.fixedTermsParameters = odict()

        branch = parameters['elements'][self.element]['charges'][self.charge]

        for label, configuration in self.configurations:
            label = '{} Hamiltonian'.format(label)
            terms = branch['configurations'][configuration]['terms']

            for term in self.hamiltonianTerms:
                if term in ('Atomic', 'Magnetic Field', 'Exchange Field'):
                    node = terms[term]
                else:
                    node = terms[term]['symmetries'][self.symmetry]

                parameters = node['parameters']['variable']
                for parameter in parameters:
                    if 'Atomic' in term or 'Hybridization' in term:
                        if parameter[0] in ('F', 'G'):
                            scaleFactor = 0.8
                            data = [parameters[parameter], scaleFactor]
                        elif parameter[0] == 'ζ':
                            scaleFactor = 1.0
                            data = [parameters[parameter], scaleFactor]
                        else:
                            data = parameters[parameter]
                    else:
                        data = parameters[parameter]

                    self.hamiltonianData[term][label][parameter] = data

                parameters = terms[term]['parameters']['fixed']
                for parameter in parameters:
                    value = parameters[parameter]
                    self.fixedTermsParameters[term][parameter] = value

                if term in ('Atomic', 'Crystal Field'):
                    self.hamiltonianState[term] = 2
                else:
                    self.hamiltonianState[term] = 0

    def term_suffix(self, term):
        return term.lower().replace(' ', '_').replace('-', '_')

    def saveInput(self):
        templatePath = resourceFileName(
            'crispy:' + os.path.join('modules', 'quanty', 'templates',
                                     '{}'.format(self.templateName)))

        with open(templatePath) as p:
            self.template = p.read()

        self.input = copy.deepcopy(self.template)

        replacements = odict()

        # TODO: Make this an object attribute when saving the .pkl file
        # doesn't brake compatibility.
        replacements['$DenseBorder'] = self.denseBorder
        replacements['$Verbosity'] = self.verbosity
        replacements['$NConfigurations'] = self.nConfigurations

        subshell = self.configurations[0][1][:2]
        subshell_occupation = self.configurations[0][1][2:]
        replacements['$NElectrons_{}'.format(subshell)] = subshell_occupation

        replacements['$T'] = self.temperature

        replacements['$Emin1'] = self.xMin
        replacements['$Emax1'] = self.xMax
        replacements['$NE1'] = self.xNPoints
        replacements['$Eedge1'] = self.xEdge

        if len(self.xLorentzian) == 1:
            replacements['$Gamma1'] = 0.1
            replacements['$Gmin1'] = self.xLorentzian[0]
            replacements['$Gmax1'] = self.xLorentzian[0]
            replacements['$Egamma1'] = (self.xMin + self.xMax) / 2
        else:
            replacements['$Gamma1'] = 0.1
            replacements['$Gmin1'] = self.xLorentzian[0]
            replacements['$Gmax1'] = self.xLorentzian[1]
            if len(self.xLorentzian) == 2:
                replacements['$Egamma1'] = (self.xMin + self.xMax) / 2
            else:
                replacements['$Egamma1'] = self.xLorentzian[2]

        s = '{{{0:.8g}, {1:.8g}, {2:.8g}}}'

        u = np.array(self.k1)
        u = u / np.linalg.norm(u)
        replacements['$k1'] = s.format(u[0], u[1], u[2])

        v = np.array(self.eps11)
        v = v / np.linalg.norm(v)
        replacements['$eps11'] = s.format(v[0], v[1], v[2])

        w = np.array(self.eps12)
        w = w / np.linalg.norm(w)
        replacements['$eps12'] = s.format(w[0], w[1], w[2])

        replacements['$spectra'] = ', '.join(
            '\'{}\''.format(p) for p in self.spectra.toCalculateChecked)

        if self.experiment == 'RIXS':
            # The Lorentzian broadening along the incident axis cannot be
            # changed in the interface, and must therefore be set to the
            # final value before the start of the calculation.
            # replacements['$Gamma1'] = self.xLorentzian
            replacements['$Emin2'] = self.yMin
            replacements['$Emax2'] = self.yMax
            replacements['$NE2'] = self.yNPoints
            replacements['$Eedge2'] = self.yEdge
            replacements['$Gamma2'] = self.yLorentzian[0]

        replacements['$NPsisAuto'] = self.nPsisAuto
        replacements['$NPsis'] = self.nPsis

        for term in self.hamiltonianData:
            configurations = self.hamiltonianData[term]
            for configuration, parameters in configurations.items():
                if 'Initial' in configuration:
                    suffix = 'i'
                elif 'Intermediate' in configuration:
                    suffix = 'm'
                elif 'Final' in configuration:
                    suffix = 'f'
                for parameter, data in parameters.items():
                    # Convert to parameters name from Greek letters.
                    parameter = parameter.replace('ζ', 'zeta')
                    parameter = parameter.replace('Δ', 'Delta')
                    parameter = parameter.replace('σ', 'sigma')
                    parameter = parameter.replace('τ', 'tau')
                    parameter = parameter.replace('μ', 'mu')
                    parameter = parameter.replace('ν', 'nu')

                    scaleFactor = None
                    try:
                        value, scaleFactor = data
                    except TypeError:
                        value = data

                    key = '${}_{}_value'.format(parameter, suffix)
                    replacements[key] = '{}'.format(value)

                    if scaleFactor is not None:
                        key = '${}_{}_scaling'.format(parameter, suffix)
                        replacements[key] = '{}'.format(scaleFactor)

            checkState = self.hamiltonianState[term]
            if checkState > 0:
                checkState = 1

            term_suffix = self.term_suffix(term)
            replacements['$H_{}'.format(term_suffix)] = checkState

            try:
                parameters = self.fixedTermsParameters[term]
            except KeyError:
                pass
            else:
                for parameter in parameters:
                    value = parameters[parameter]
                    replacements['${}'.format(parameter)] = value

        replacements['$Experiment'] = self.experiment
        replacements['$BaseName'] = self.baseName

        for replacement in replacements:
            self.input = self.input.replace(
                replacement, str(replacements[replacement]))

        with open(self.baseName + '.lua', 'w') as f:
            f.write(self.input)

        self.output = str()


class QuantyDockWidget(QDockWidget):

    def __init__(self, parent=None, settings=None):
        super(QuantyDockWidget, self).__init__(parent=parent)
        self.settings = settings

        # Load the external .ui file for the widget.
        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'quanty', 'main.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.calculation = QuantyCalculation()
        self.populateWidget()
        self.activateWidget()

        self.timeout = 4000

        self.hamiltonianSplitter.setSizes((150, 300, 10))

    def activateWidget(self):
        self.elementComboBox.currentTextChanged.connect(self.resetCalculation)
        self.chargeComboBox.currentTextChanged.connect(self.resetCalculation)
        self.symmetryComboBox.currentTextChanged.connect(self.resetCalculation)
        self.experimentComboBox.currentTextChanged.connect(
            self.resetCalculation)
        self.edgeComboBox.currentTextChanged.connect(self.resetCalculation)

        self.temperatureLineEdit.editingFinished.connect(
            self.updateTemperature)
        self.magneticFieldLineEdit.editingFinished.connect(
            self.updateMagneticField)

        self.xMinLineEdit.editingFinished.connect(self.updateXMin)
        self.xMaxLineEdit.editingFinished.connect(self.updateXMax)
        self.xNPointsLineEdit.editingFinished.connect(self.updateXNPoints)
        self.xLorentzianLineEdit.editingFinished.connect(
            self.updateXLorentzian)
        self.xGaussianLineEdit.editingFinished.connect(self.updateXGaussian)
        self.k1LineEdit.editingFinished.connect(self.updateIncidentWaveVector)
        self.eps11LineEdit.editingFinished.connect(
            self.updateIncidentPolarizationVectors)

        self.yMinLineEdit.editingFinished.connect(self.updateYMin)
        self.yMaxLineEdit.editingFinished.connect(self.updateYMax)
        self.yNPointsLineEdit.editingFinished.connect(self.updateYNPoints)
        self.yLorentzianLineEdit.editingFinished.connect(
            self.updateYLorentzian)
        self.yGaussianLineEdit.editingFinished.connect(self.updateYGaussian)

        self.fkLineEdit.editingFinished.connect(self.updateScaleFactors)
        self.gkLineEdit.editingFinished.connect(self.updateScaleFactors)
        self.zetaLineEdit.editingFinished.connect(self.updateScaleFactors)

        self.syncParametersCheckBox.toggled.connect(self.updateSyncParameters)

        self.nPsisAutoCheckBox.toggled.connect(self.updateNPsisAuto)
        self.nPsisLineEdit.editingFinished.connect(self.updateNPsis)
        self.nConfigurationsLineEdit.editingFinished.connect(
            self.updateConfigurations)

        self.saveInputAsPushButton.clicked.connect(self.saveInputAs)
        self.calculationPushButton.clicked.connect(self.runCalculation)

    def populateWidget(self):
        """
        Populate the widget using data stored in the calculation
        object. The order in which the individual widgets are populated
        follows the way they are arranged.

        The models are recreated every time the function is called.
        This might seem to be an overkill, but in practice it is very fast.
        Don't try to move the model creation outside this function; is not
        worth the effort, and there is nothing to gain from it.
        """
        c = self.calculation

        self.elementComboBox.setItems(c.elements, c.element)
        self.chargeComboBox.setItems(c.charges, c.charge)
        self.symmetryComboBox.setItems(c.symmetries, c.symmetry)
        self.experimentComboBox.setItems(c.experiments, c.experiment)
        self.edgeComboBox.setItems(c.edges, c.edge)

        self.temperatureLineEdit.setValue(c.temperature)
        self.magneticFieldLineEdit.setValue(c.magneticField)

        self.energiesTabWidget.setTabText(0, str(c.xLabel))
        self.xMinLineEdit.setValue(c.xMin)
        self.xMaxLineEdit.setValue(c.xMax)
        self.xNPointsLineEdit.setValue(c.xNPoints)
        self.xLorentzianLineEdit.setList(c.xLorentzian)
        self.xGaussianLineEdit.setValue(c.xGaussian)

        self.k1LineEdit.setVector(c.k1)
        self.eps11LineEdit.setVector(c.eps11)
        self.eps12LineEdit.setVector(c.eps12)

        if c.experiment == 'RIXS':
            if self.energiesTabWidget.count() == 1:
                tab = self.energiesTabWidget.findChild(QWidget, 'yTab')
                self.energiesTabWidget.addTab(tab, tab.objectName())
                self.energiesTabWidget.setTabText(1, c.yLabel)
            self.yMinLineEdit.setValue(c.yMin)
            self.yMaxLineEdit.setValue(c.yMax)
            self.yNPointsLineEdit.setValue(c.yNPoints)
            self.yLorentzianLineEdit.setList(c.yLorentzian)
            self.yGaussianLineEdit.setValue(c.yGaussian)
            self.k2LineEdit.setVector(c.k2)
            self.eps21LineEdit.setVector(c.eps21)
            self.eps22LineEdit.setVector(c.eps22)
            text = self.eps11Label.text()
            text = re.sub('>[vσ]', '>σ', text)
            self.eps11Label.setText(text)
            text = self.eps12Label.text()
            text = re.sub('>[hπ]', '>π', text)
            self.eps12Label.setText(text)
        else:
            self.energiesTabWidget.removeTab(1)
            text = self.eps11Label.text()
            text = re.sub('>[vσ]', '>v', text)
            self.eps11Label.setText(text)
            text = self.eps12Label.text()
            text = re.sub('>[hπ]', '>h', text)
            self.eps12Label.setText(text)

        # Create the spectra selection model.
        self.spectraModel = SpectraModel(parent=self)
        self.spectraModel.setModelData(
            c.spectra.toCalculate, c.spectra.toCalculateChecked)
        self.spectraModel.checkStateChanged.connect(
            self.updateSpectraCheckState)
        self.spectraListView.setModel(self.spectraModel)
        self.spectraListView.selectionModel().setCurrentIndex(
            self.spectraModel.index(0, 0), QItemSelectionModel.Select)

        self.fkLineEdit.setValue(c.fk)
        self.gkLineEdit.setValue(c.gk)
        self.zetaLineEdit.setValue(c.zeta)

        # Create the Hamiltonian model.
        self.hamiltonianModel = HamiltonianModel(parent=self)
        self.hamiltonianModel.setModelData(c.hamiltonianData)
        self.hamiltonianModel.setNodesCheckState(c.hamiltonianState)
        if self.syncParametersCheckBox.isChecked():
            self.hamiltonianModel.setSyncState(True)
        else:
            self.hamiltonianModel.setSyncState(False)
        self.hamiltonianModel.dataChanged.connect(self.updateHamiltonianData)
        self.hamiltonianModel.itemCheckStateChanged.connect(
            self.updateHamiltonianNodeCheckState)

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

        self.nPsisLineEdit.setValue(c.nPsis)
        self.nPsisAutoCheckBox.setChecked(c.nPsisAuto)
        self.nConfigurationsLineEdit.setValue(c.nConfigurations)

        self.nConfigurationsLineEdit.setEnabled(False)
        termName = '{}-Ligands Hybridization'.format(c.block)
        if termName in c.hamiltonianData:
            termState = c.hamiltonianState[termName]
            if termState != 0:
                self.nConfigurationsLineEdit.setEnabled(True)

        if not hasattr(self, 'resultsModel'):
            # Create the results model.
            self.resultsModel = ResultsModel(parent=self)
            self.resultsModel.itemNameChanged.connect(
                self.updateCalculationName)
            self.resultsModel.itemCheckStateChanged.connect(
                self.updatePlotWidget)
            self.resultsModel.modelDataUpdated.connect(self.updatePlotWidget)
            self.resultsModel.modelDataChanged.connect(self.updatePlotWidget)
            self.resultsModel.modelDataChanged.connect(self.updateResultsView)

            # Assign the results model to the results view.
            self.resultsView.setModel(self.resultsModel)
            self.resultsView.selectionModel().selectionChanged.connect(
                self.updateWidget)
            self.resultsView.resizeColumnsToContents()
            self.resultsView.horizontalHeader().setSectionsMovable(False)
            self.resultsView.horizontalHeader().setSectionsClickable(False)
            if sys.platform == 'darwin':
                self.resultsView.horizontalHeader().setMaximumHeight(17)

            # Add a context menu to the view.
            self.resultsView.setContextMenuPolicy(Qt.CustomContextMenu)
            self.resultsView.customContextMenuRequested[QPoint].connect(
                self.showResultsContextMenu)

        if not hasattr(self, 'resultDetailsDialog'):
            self.resultDetailsDialog = QuantyResultDetailsDialog(parent=self)
        self.resultDetailsDialog.calculation = c

    def enableWidget(self, flag=True):
        self.elementComboBox.setEnabled(flag)
        self.chargeComboBox.setEnabled(flag)
        self.symmetryComboBox.setEnabled(flag)
        self.experimentComboBox.setEnabled(flag)
        self.edgeComboBox.setEnabled(flag)

        self.temperatureLineEdit.setEnabled(flag)
        self.magneticFieldLineEdit.setEnabled(flag)

        self.xMinLineEdit.setEnabled(flag)
        self.xMaxLineEdit.setEnabled(flag)
        self.xNPointsLineEdit.setEnabled(flag)
        self.xLorentzianLineEdit.setEnabled(flag)
        self.xGaussianLineEdit.setEnabled(flag)
        self.k1LineEdit.setEnabled(flag)
        self.eps11LineEdit.setEnabled(flag)

        self.yMinLineEdit.setEnabled(flag)
        self.yMaxLineEdit.setEnabled(flag)
        self.yNPointsLineEdit.setEnabled(flag)
        self.yLorentzianLineEdit.setEnabled(flag)
        self.yGaussianLineEdit.setEnabled(flag)

        self.fkLineEdit.setEnabled(flag)
        self.gkLineEdit.setEnabled(flag)
        self.zetaLineEdit.setEnabled(flag)

        self.syncParametersCheckBox.setEnabled(flag)

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

    def updateTemperature(self):
        temperature = self.temperatureLineEdit.getValue()

        if temperature < 0:
            message = 'The temperature cannot be negative.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.temperatureLineEdit.setValue(self.calculation.temperature)
            return
        elif temperature == 0:
            self.nPsisAutoCheckBox.setChecked(False)
            self.updateNPsisAuto()
            self.nPsisLineEdit.setValue(1)
            self.updateNPsis()

        self.calculation.temperature = temperature

    def updateMagneticField(self):
        magneticField = self.magneticFieldLineEdit.getValue()

        if magneticField == 0:
            self.calculation.hamiltonianState['Magnetic Field'] = 0
        else:
            self.calculation.hamiltonianState['Magnetic Field'] = 2
        self.hamiltonianModel.setNodesCheckState(
            self.calculation.hamiltonianState)

        TESLA_TO_EV = 5.788e-05

        # Normalize the current incident vector.
        k1 = np.array(self.calculation.k1)
        k1 = k1 / np.linalg.norm(k1)

        configurations = self.calculation.hamiltonianData['Magnetic Field']
        for configuration in configurations:
            parameters = configurations[configuration]
            for i, parameter in enumerate(parameters):
                value = float(magneticField * np.abs(k1[i]) * TESLA_TO_EV)
                if abs(value) == 0.0:
                    value = 0.0
                configurations[configuration][parameter] = value
        self.hamiltonianModel.updateModelData(self.calculation.hamiltonianData)

        self.calculation.magneticField = magneticField

    def updateXMin(self):
        xMin = self.xMinLineEdit.getValue()

        if xMin > self.calculation.xMax:
            message = ('The lower energy limit cannot be larger than '
                       'the upper limit.')
            self.getStatusBar().showMessage(message, self.timeout)
            self.xMinLineEdit.setValue(self.calculation.xMin)
            return

        self.calculation.xMin = xMin

    def updateXMax(self):
        xMax = self.xMaxLineEdit.getValue()

        if xMax < self.calculation.xMin:
            message = ('The upper energy limit cannot be smaller than '
                       'the lower limit.')
            self.getStatusBar().showMessage(message, self.timeout)
            self.xMaxLineEdit.setValue(self.calculation.xMax)
            return

        self.calculation.xMax = xMax

    def updateXNPoints(self):
        xNPoints = self.xNPointsLineEdit.getValue()

        xMin = self.calculation.xMin
        xMax = self.calculation.xMax
        xLorentzianMin = float(self.calculation.xLorentzian[0])

        xNPointsMin = int(np.floor((xMax - xMin) / xLorentzianMin))
        if xNPoints < xNPointsMin:
            message = ('The number of points must be greater than '
                       '{}.'.format(xNPointsMin))
            self.getStatusBar().showMessage(message, self.timeout)
            self.xNPointsLineEdit.setValue(self.calculation.xNPoints)
            return

        self.calculation.xNPoints = xNPoints

    def updateXLorentzian(self):
        try:
            xLorentzian = self.xLorentzianLineEdit.getList()
        except ValueError:
            message = 'Invalid data for the Lorentzian brodening.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.xLorentzianLineEdit.setList(self.calculation.xLorentzian)
            return

        # Do some validation of the input value.
        if len(xLorentzian) > 3:
            message = 'The broadening can have at most three elements.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.xLorentzianLineEdit.setList(self.calculation.xLorentzian)
            return

        try:
            xLorentzianMin = float(xLorentzian[0])
        except IndexError:
            pass
        else:
            if xLorentzianMin < 0.1:
                message = 'The broadening cannot be smaller than 0.1.'
                self.getStatusBar().showMessage(message, self.timeout)
                self.xLorentzianLineEdit.setList(
                    self.calculation.xLorentzian)
                return

        try:
            xLorentzianMax = float(xLorentzian[1])
        except IndexError:
            pass
        else:
            if xLorentzianMax < 0.1:
                message = 'The broadening cannot be smaller than 0.1.'
                self.getStatusBar().showMessage(message, self.timeout)
                self.xLorentzianLineEdit.setList(
                    self.calculation.xLorentzian)

        try:
            xLorentzianPivotEnergy = float(xLorentzian[2])
        except IndexError:
            pass
        else:
            xMin = self.calculation.xMin
            xMax = self.calculation.xMax

            if not (xMin < xLorentzianPivotEnergy < xMax):
                message = ('The transition point must lie between the upper '
                           'and lower energy limits.')
                self.getStatusBar().showMessage(message, self.timeout)
                self.xLorentzianLineEdit.setList(
                    self.calculation.xLorentzian)
                return

        self.calculation.xLorentzian = xLorentzian

    def updateXGaussian(self):
        xGaussian = self.xGaussianLineEdit.getValue()

        if xGaussian < 0:
            message = 'The broadening cannot be negative.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.xGaussianLineEdit.setValue(self.calculation.xGaussian)
            return

        self.calculation.xGaussian = xGaussian

    def updateIncidentWaveVector(self):
        try:
            k1 = self.k1LineEdit.getVector()
        except ValueError:
            message = 'Invalid data for the wave vector.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.k1LineEdit.setVector(self.calculation.k1)
            return

        if np.all(np.array(k1) == 0):
            message = 'The wave vector cannot be null.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.k1LineEdit.setVector(self.calculation.k1)
            return

        # The k1 value should be fine; save it.
        self.calculation.k1 = k1

        # The polarization vector must be correct.
        eps11 = self.eps11LineEdit.getVector()

        # If the wave and polarization vectors are not perpendicular, select a
        # new perpendicular vector for the polarization.
        if np.dot(np.array(k1), np.array(eps11)) != 0:
            if k1[2] != 0 or (-k1[0] - k1[1]) != 0:
                eps11 = (k1[2], k1[2], -k1[0] - k1[1])
            else:
                eps11 = (-k1[2] - k1[1], k1[0], k1[0])

        self.eps11LineEdit.setVector(eps11)
        self.calculation.eps11 = eps11

        # Generate a second, perpendicular, polarization vector to the plane
        # defined by the wave vector and the first polarization vector.
        eps12 = np.cross(np.array(eps11), np.array(k1))
        eps12 = eps12.tolist()

        self.eps12LineEdit.setVector(eps12)
        self.calculation.eps12 = eps12

        self.updateMagneticField()

    def updateIncidentPolarizationVectors(self):
        try:
            eps11 = self.eps11LineEdit.getVector()
        except ValueError:
            message = 'Invalid data for the polarization vector.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.eps11LineEdit.setVector(self.calculation.eps11)
            return

        if np.all(np.array(eps11) == 0):
            message = 'The polarization vector cannot be null.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.eps11LineEdit.setVector(self.calculation.eps11)
            return

        k1 = self.calculation.k1
        if np.dot(np.array(k1), np.array(eps11)) != 0:
            message = ('The wave and polarization vectors need to be '
                       'perpendicular.')
            self.getStatusBar().showMessage(message, self.timeout)
            self.eps11LineEdit.setVector(self.calculation.eps11)
            return

        self.calculation.eps11 = eps11

        # Generate a second, perpendicular, polarization vector to the plane
        # defined by the wave vector and the first polarization vector.
        eps12 = np.cross(np.array(eps11), np.array(k1))
        eps12 = eps12.tolist()

        self.eps12LineEdit.setVector(eps12)
        self.calculation.eps12 = eps12

    def updateYMin(self):
        yMin = self.yMinLineEdit.getValue()

        if yMin > self.calculation.yMax:
            message = ('The lower energy limit cannot be larger than '
                       'the upper limit.')
            self.getStatusBar().showMessage(message, self.timeout)
            self.yMinLineEdit.setValue(self.calculation.yMin)
            return

        self.calculation.yMin = yMin

    def updateYMax(self):
        yMax = self.yMaxLineEdit.getValue()

        if yMax < self.calculation.yMin:
            message = ('The upper energy limit cannot be smaller than '
                       'the lower limit.')
            self.getStatusBar().showMessage(message, self.timeout)
            self.yMaxLineEdit.setValue(self.calculation.yMax)
            return

        self.calculation.yMax = yMax

    def updateYNPoints(self):
        yNPoints = self.yNPointsLineEdit.getValue()

        yMin = self.calculation.yMin
        yMax = self.calculation.yMax
        yLorentzianMin = float(self.calculation.yLorentzian[0])

        yNPointsMin = int(np.floor((yMax - yMin) / yLorentzianMin))
        if yNPoints < yNPointsMin:
            message = ('The number of points must be greater than '
                       '{}.'.format(yNPointsMin))
            self.getStatusBar().showMessage(message, self.timeout)
            self.yNPointsLineEdit.setValue(self.calculation.yNPoints)
            return

        self.calculation.yNPoints = yNPoints

    def updateYLorentzian(self):
        try:
            yLorentzian = self.yLorentzianLineEdit.getList()
        except ValueError:
            message = 'Invalid data for the Lorentzian brodening.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.yLorentzianLineEdit.setList(self.calculation.yLorentzian)
            return

        # Do some validation of the input value.
        if len(yLorentzian) > 3:
            message = 'The broadening can have at most three elements.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.yLorentzianLineEdit.setList(self.calculation.yLorentzian)
            return

        try:
            yLorentzianMin = float(yLorentzian[0])
        except IndexError:
            pass
        else:
            if yLorentzianMin < 0.1:
                message = 'The broadening cannot be smaller than 0.1.'
                self.getStatusBar().showMessage(message, self.timeout)
                self.yLorentzianLineEdit.setList(
                    self.calculation.yLorentzian)
                return

        try:
            yLorentzianMax = float(yLorentzian[1])
        except IndexError:
            pass
        else:
            if yLorentzianMax < 0.1:
                message = 'The broadening cannot be smaller than 0.1.'
                self.getStatusBar().showMessage(message, self.timeout)
                self.yLorentzianLineEdit.setList(
                    self.calculation.yLorentzian)

        try:
            yLorentzianPivotEnergy = float(yLorentzian[2])
        except IndexError:
            pass
        else:
            yMin = self.calculation.yMin
            yMax = self.calculation.yMax

            if not (yMin < yLorentzianPivotEnergy < yMax):
                message = ('The transition point must lie between the upper '
                           'and lower energy limits.')
                self.getStatusBar().showMessage(message, self.timeout)
                self.yLorentzianLineEdit.setList(
                    self.calculation.yLorentzian)
                return

        self.calculation.yLorentzian = list(map(float, yLorentzian))

    def updateYGaussian(self):
        yGaussian = self.yGaussianLineEdit.getValue()

        if yGaussian < 0:
            message = 'The broadening cannot be negative.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.yGaussianLineEdit.setValue(self.calculation.yGaussian)
            return

        self.calculation.yGaussian = yGaussian

    def updateSpectraCheckState(self, checkedItems):
        self.calculation.spectra.toCalculateChecked = checkedItems

    def updateScaleFactors(self):
        fk = self.fkLineEdit.getValue()
        gk = self.gkLineEdit.getValue()
        zeta = self.zetaLineEdit.getValue()

        if fk < 0 or gk < 0 or zeta < 0:
            message = 'The scale factors cannot be negative.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.fkLineEdit.setValue(self.calculation.fk)
            self.gkLineEdit.setValue(self.calculation.gk)
            self.zetaLineEdit.setValue(self.calculation.zeta)
            return

        self.calculation.fk = fk
        self.calculation.gk = gk
        self.calculation.zeta = zeta

        # TODO: This should be already updated to the most recent data.
        # self.calculation.hamiltonianData = self.hamiltonianModel.getModelData() # noqa
        terms = self.calculation.hamiltonianData

        for term in terms:
            if not ('Atomic' in term or 'Hybridization' in term):
                continue
            configurations = terms[term]
            for configuration in configurations:
                parameters = configurations[configuration]
                for parameter in parameters:
                    # Change the scale factors if the parameter has one.
                    try:
                        value, _ = parameters[parameter]
                    except TypeError:
                        continue
                    if parameter.startswith('F'):
                        terms[term][configuration][parameter] = [value, fk]
                    elif parameter.startswith('G'):
                        terms[term][configuration][parameter] = [value, gk]
                    elif parameter.startswith('ζ'):
                        terms[term][configuration][parameter] = [value, zeta]
        self.hamiltonianModel.updateModelData(self.calculation.hamiltonianData)
        # I have no idea why this is needed. Both views should update after
        # the above function call.
        self.hamiltonianTermsView.viewport().repaint()
        self.hamiltonianParametersView.viewport().repaint()

    def updateNPsisAuto(self):
        nPsisAuto = int(self.nPsisAutoCheckBox.isChecked())

        if nPsisAuto:
            self.nPsisLineEdit.setValue(self.calculation.nPsisMax)
            self.nPsisLineEdit.setEnabled(False)
        else:
            self.nPsisLineEdit.setEnabled(True)

        self.calculation.nPsisAuto = nPsisAuto

    def updateNPsis(self):
        nPsis = self.nPsisLineEdit.getValue()

        if nPsis <= 0:
            message = 'The number of states must be larger than zero.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.nPsisLineEdit.setValue(self.calculation.nPsis)
            return

        if nPsis > self.calculation.nPsisMax:
            message = 'The selected number of states exceeds the maximum.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.nPsisLineEdit.setValue(self.calculation.nPsisMax)
            nPsis = self.calculation.nPsisMax

        self.calculation.nPsis = nPsis

    def updateSyncParameters(self, flag):
        self.hamiltonianModel.setSyncState(flag)

    def updateHamiltonianData(self):
        self.calculation.hamiltonianData = self.hamiltonianModel.getModelData()

    def updateHamiltonianNodeCheckState(self, index, state):
        hamiltonianState = self.hamiltonianModel.getNodesCheckState()
        self.calculation.hamiltonianState = hamiltonianState

        # If needed, enable the configurations.
        term = '{}-Ligands Hybridization'.format(self.calculation.block)
        if term in index.data():
            if state == 0:
                nConfigurations = 1
                self.nConfigurationsLineEdit.setEnabled(False)
            elif state == 2:
                nConfigurations = 2
                self.nConfigurationsLineEdit.setEnabled(True)

            self.nConfigurationsLineEdit.setValue(nConfigurations)
            self.calculation.nConfigurations = nConfigurations

    def updateConfigurations(self, *args):
        nConfigurations = self.nConfigurationsLineEdit.getValue()

        if 'd' in self.calculation.block:
            nConfigurationsMax = 10 - self.calculation.nElectrons + 1
        elif 'f' in self.calculation.block:
            nConfigurationsMax = 14 - self.calculation.nElectrons + 1
        else:
            return

        if nConfigurations > nConfigurationsMax:
            message = 'The maximum number of configurations is {}.'.format(
                nConfigurationsMax)
            self.getStatusBar().showMessage(message, self.timeout)
            self.nConfigurationsLineEdit.setValue(nConfigurationsMax)
            nConfigurations = nConfigurationsMax

        self.calculation.nConfigurations = nConfigurations

    def saveInput(self):
        # TODO: If the user changes a value in a widget without pressing Return
        # or without interacting with another part of the GUI before running
        # the calculation, the values are not updated.

        # Set the verbosity of the calculation.
        self.calculation.verbosity = self.getVerbosity()
        self.calculation.denseBorder = self.getDenseBorder()

        path = self.getCurrentPath()
        try:
            os.chdir(path)
        except OSError as e:
            message = ('The specified folder doesn\'t exist. Use the \'Save '
                       'Input As...\' button to save the input file to an '
                       'alternative location.')
            self.getStatusBar().showMessage(message, 2 * self.timeout)
            raise e

        # The folder might exist, but is not writable.
        try:
            self.calculation.saveInput()
        except (IOError, OSError) as e:
            message = 'Failed to write the Quanty input file.'
            self.getStatusBar().showMessage(message, self.timeout)
            raise e

    def saveInputAs(self):
        # Update the self.calculation
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Quanty Input',
            os.path.join(self.getCurrentPath(), '{}.lua'.format(
                self.calculation.baseName)), 'Quanty Input File (*.lua)')

        if path:
            basename = os.path.basename(path)
            self.calculation.baseName, _ = os.path.splitext(basename)
            self.setCurrentPath(path)
            try:
                self.saveInput()
            except (IOError, OSError) as e:
                return
            self.updateMainWindowTitle()

    def saveAllResultsAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Results',
            os.path.join(self.getCurrentPath(), '{}.pkl'.format(
                self.calculation.baseName)), 'Pickle File (*.pkl)')

        if path:
            self.setCurrentPath(path)
            calculations = self.resultsModel.getModelData()
            calculations.reverse()
            with open(path, 'wb') as p:
                pickle.dump(calculations, p, pickle.HIGHEST_PROTOCOL)

    def saveSelectedResultsAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Results',
            os.path.join(self.getCurrentPath(), '{}.pkl'.format(
                self.calculation.baseName)), 'Pickle File (*.pkl)')

        if path:
            self.setCurrentPath(path)
            indexes = self.resultsView.selectedIndexes()
            calculations = self.resultsModel.getSelectedItems(indexes)
            calculations.reverse()
            with open(path, 'wb') as p:
                pickle.dump(calculations, p, pickle.HIGHEST_PROTOCOL)

    def resetCalculation(self):
        element = self.elementComboBox.currentText()
        charge = self.chargeComboBox.currentText()
        symmetry = self.symmetryComboBox.currentText()
        experiment = self.experimentComboBox.currentText()
        edge = self.edgeComboBox.currentText()

        self.calculation = QuantyCalculation(
            element=element, charge=charge, symmetry=symmetry,
            experiment=experiment, edge=edge)

        self.populateWidget()
        self.updateMainWindowTitle()
        self.getPlotWidget().reset()
        self.resultsView.selectionModel().clearSelection()
        self.resultDetailsDialog.populateWidget()

    def removeSelectedCalculations(self):
        indexes = self.resultsView.selectedIndexes()
        if not indexes:
            self.getPlotWidget().reset()
            return
        self.resultsModel.removeItems(indexes)

    def removeAllResults(self):
        self.resultsModel.reset()
        self.getPlotWidget().reset()

    def loadResults(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Load Results',
            self.getCurrentPath(), 'Pickle File (*.pkl)')

        if path:
            self.setCurrentPath(path)
            with open(path, 'rb') as p:
                self.resultsModel.appendItems(pickle.load(p))
            self.updateMainWindowTitle()
            self.quantyToolBox.setCurrentWidget(self.resultsPage)

    def runCalculation(self):
        path = self.getQuantyPath()

        if path:
            command = path
        else:
            message = ('The path to the Quanty executable is not set. '
                       'Please use the preferences menu to set it.')
            self.getStatusBar().showMessage(message, 2 * self.timeout)
            return

        # Test the executable.
        with open(os.devnull, 'w') as f:
            try:
                subprocess.call(command, stdout=f, stderr=f)
            except OSError as e:
                if e.errno == os.errno.ENOENT:
                    message = ('The Quanty executable is not working '
                               'properly. Is the path set correctly?')
                    self.getStatusBar().showMessage(message, 2 * self.timeout)
                    return
                else:
                    raise e

        # Write the input file to disk.
        try:
            self.saveInput()
        except (IOError, OSError) as e:
            return

        # Disable the UI while the calculation is running.
        self.enableWidget(False)

        self.calculation.startingTime = datetime.datetime.now()

        # Run Quanty using QProcess.
        self.process = QProcess()

        self.process.start(command, (self.calculation.baseName + '.lua', ))
        message = (
            'Running "Quanty {}" in {}.'.format(
                self.calculation.baseName + '.lua', os.getcwd()))
        self.getStatusBar().showMessage(message)

        if sys.platform == 'win32' and self.process.waitForStarted():
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
        self.enableWidget(True)

    def processCalculation(self, *args):
        startingTime = self.calculation.startingTime

        # When did I finish?
        endingTime = datetime.datetime.now()
        self.calculation.endingTime = endingTime

        # Re-enable the UI if the calculation has finished.
        self.enableWidget(True)

        # Reset the calculation button.
        self.updateCalculationPushButton('run')

        # Evaluate the exit code and status of the process.
        exitStatus = self.process.exitStatus()
        exitCode = self.process.exitCode()

        if exitStatus == 0 and exitCode == 0:
            message = ('Quanty has finished successfully in ')
            delta = (endingTime - startingTime).total_seconds()
            hours, reminder = divmod(delta, 3600)
            minutes, seconds = divmod(reminder, 60)
            seconds = round(seconds, 2)
            if hours > 0:
                message += '{} hours {} minutes and {} seconds.'.format(
                    hours, minutes, seconds)
            elif minutes > 0:
                message += '{} minutes and {} seconds.'.format(
                    minutes, seconds)
            else:
                message += '{} seconds.'.format(seconds)
            self.getStatusBar().showMessage(message, self.timeout)
        elif exitStatus == 0 and exitCode == 1:
            self.handleErrorLogging()
            message = (
                'Quanty has finished unsuccessfully. '
                'Check the logging window for more details.')
            self.getStatusBar().showMessage(message, self.timeout)
            return
        # exitCode is platform dependent; exitStatus is always 1.
        elif exitStatus == 1:
            message = 'Quanty was stopped.'
            self.getStatusBar().showMessage(message, self.timeout)
            return

        scrollBar = self.getLoggerWidget().verticalScrollBar()
        scrollBar.setValue(scrollBar.maximum())

        # Load the spectra from disk.
        self.calculation.spectra.loadFromDisk(self.calculation)

        # Once all processing is done, store the calculation in the
        # results model. Upon finishing this, a signal is emitted by the
        # model which triggers some updates to be performed.
        self.resultsModel.appendItems(self.calculation)

        # If the "Hamiltonian Setup" page is currently selected, when the
        # current widget is set to the "Results Page", the former is not
        # displayed. To avoid this I switch first to the "General Setup" page.
        self.quantyToolBox.setCurrentWidget(self.generalPage)
        self.quantyToolBox.setCurrentWidget(self.resultsPage)
        self.resultsView.setFocus()

    def plotSpectrum(self, spectrum):
        # Spectrum object must have ALL information required to do the stuff
        # below. ALL!!!

        pw = self.getPlotWidget()

        if self.calculation.experiment == 'RIXS':
            self.getPlotWidget().setGraphXLabel('Incident Energy (eV)')
            self.getPlotWidget().setGraphYLabel('Energy Transfer (eV)')

            xMin = self.calculation.xMin
            xMax = self.calculation.xMax
            xNPoints = self.calculation.xNPoints

            yMin = self.calculation.yMin
            yMax = self.calculation.yMax
            yNPoints = self.calculation.yNPoints

            xScale = (xMax - xMin) / xNPoints
            yScale = (yMax - yMin) / yNPoints
            scale = (xScale, yScale)

            xOrigin = xMin
            yOrigin = yMin
            origin = (xOrigin, yOrigin)

            z = spectrum.z

            xGaussian = self.calculation.xGaussian
            yGaussian = self.calculation.yGaussian

            if xGaussian > 0 and yGaussian > 0:
                xFwhm = xGaussian / xScale
                yFwhm = yGaussian / yScale

                fwhm = [xFwhm, yFwhm]
                z = broaden(z, fwhm, 'gaussian')

            self.getPlotWidget().addImage(
                z, origin=origin, scale=scale, reset=False)

        else:
            pw.setGraphXLabel(spectrum.xLabel)
            pw.setGraphYLabel(spectrum.yLabel)

            try:
                pw.addCurve(spectrum.x, spectrum.y, spectrum.legend)
            except AssertionError:
                message = 'The x and y arrays have different lengths.'
                self.getStatusBar().showMessage(message)

    def selectedHamiltonianTermChanged(self):
        index = self.hamiltonianTermsView.currentIndex()
        self.hamiltonianParametersView.setRootIndex(index)

    def showResultsContextMenu(self, position):
        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'clipboard.svg')))
        self.showDetailsAction = QAction(
            icon, 'Show Details', self, triggered=self.showResultDetailsDialog)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'save.svg')))
        self.saveSelectedResultsAsAction = QAction(
            icon, 'Save Selected As...', self,
            triggered=self.saveSelectedResultsAs)
        self.saveAllResultsAsAction = QAction(
            icon, 'Save All As...', self, triggered=self.saveAllResultsAs)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'trash.svg')))
        self.removeSelectedResultsAction = QAction(
            icon, 'Remove Selected', self,
            triggered=self.removeSelectedCalculations)
        self.removeAllResultsAction = QAction(
            icon, 'Remove All', self, triggered=self.removeAllResults)

        icon = QIcon(resourceFileName(
            'crispy:' + os.path.join('gui', 'icons', 'folder-open.svg')))
        self.loadResultsAction = QAction(
            icon, 'Load', self, triggered=self.loadResults)

        self.resultsContextMenu = QMenu('Results Context Menu', self)
        self.resultsContextMenu.addAction(self.showDetailsAction)
        self.resultsContextMenu.addSeparator()
        self.resultsContextMenu.addAction(self.saveSelectedResultsAsAction)
        self.resultsContextMenu.addAction(self.removeSelectedResultsAction)
        self.resultsContextMenu.addSeparator()
        self.resultsContextMenu.addAction(self.saveAllResultsAsAction)
        self.resultsContextMenu.addAction(self.removeAllResultsAction)
        self.resultsContextMenu.addSeparator()
        self.resultsContextMenu.addAction(self.loadResultsAction)

        if not self.resultsView.selectedIndexes():
            self.removeSelectedResultsAction.setEnabled(False)
            self.saveSelectedResultsAsAction.setEnabled(False)

        if not self.resultsModel.modelData:
            self.showDetailsAction.setEnabled(False)
            self.saveAllResultsAsAction.setEnabled(False)
            self.removeAllResultsAction.setEnabled(False)

        self.resultsContextMenu.exec_(self.resultsView.mapToGlobal(position))

    def updateResultsView(self, index):
        """
        Update the selection to contain only the result specified by
        the index (this should be the last index of the model). Also
        update the context menu.

        The selectionChanged signal which is emited after the select
        method is called will be used to update some of the widgets.

        :param index: Index of the last item of the model.
        :type index: QModelIndex
        """

        flags = (QItemSelectionModel.Clear | QItemSelectionModel.Rows |
                 QItemSelectionModel.Select)
        self.resultsView.selectionModel().select(index, flags)
        self.resultsView.resizeColumnsToContents()
        self.resultsView.setFocus()
        if not self.resultsModel.modelData:
            self.updateResultsContextMenu(False)
        else:
            self.updateResultsContextMenu(True)

    def getLastSelectedResultsModelIndex(self):
        rows = self.resultsView.selectionModel().selectedRows()
        try:
            index = rows[-1]
        except IndexError:
            index = None
        return index

    def updateWidget(self):
        index = self.getLastSelectedResultsModelIndex()
        if index is None:
            self.resultDetailsDialog.clear()
            return
        self.calculation = self.resultsModel.getItem(index)

        self.populateWidget()
        self.updateMainWindowTitle()

        if self.resultDetailsDialog.isVisible():
            self.updateResultDetailsDialog()

    def updateResultsModelData(self):
        index = self.getLastSelectedResultsModelIndex()
        if index is None:
            return
        self.resultsModel.updateItem(index, self.calculation)
        self.resultsView.viewport().repaint()

    def updatePlotWidget(self):
        # import time
        # start = time.time()
        self.getPlotWidget().reset()

        calculations = self.resultsModel.getCheckedItems()
        for calculation in calculations:
            if not calculation.isChecked:
                continue
            if len(calculations) > 1 and calculation.experiment == 'RIXS':
                continue
            for spectrum in calculation.spectra.processed:
                spectrum.legend = '{}-{}'.format(
                    calculation.index, spectrum.shortName)
                if spectrum.name in calculation.spectra.toPlotChecked:
                    self.plotSpectrum(spectrum)
        # stop = time.time()
        # print('Updating the plot took {:.3g} seconds.'.format((stop - start)))

    def showResultDetailsDialog(self):
        self.updateResultDetailsDialog()
        self.resultDetailsDialog.show()

    def updateResultDetailsDialog(self):
        self.resultDetailsDialog.populateWidget()

    def updateCalculationName(self, name):
        self.resultsView.resizeColumnsToContents()
        self.calculation.baseName = name
        self.updateMainWindowTitle()
        self.resultDetailsDialog.updateTitle()
        self.resultDetailsDialog.updateSummary()

    def handleOutputLogging(self):
        self.process.setReadChannel(QProcess.StandardOutput)
        data = self.process.readAllStandardOutput().data()
        data = data.decode('utf-8').rstrip()
        self.getLoggerWidget().appendPlainText(data)
        self.calculation.output = self.calculation.output + data

    def handleErrorLogging(self):
        self.process.setReadChannel(QProcess.StandardError)
        data = self.process.readAllStandardError().data()
        self.getLoggerWidget().appendPlainText(data.decode('utf-8'))

    def updateMainWindowTitle(self):
        if not self.calculation.baseName:
            title = 'Crispy'
        else:
            title = 'Crispy - {}'.format(self.calculation.baseName)
        self.setMainWindowTitle(title)

    def updateResultsContextMenu(self, flag):
        self.parent().quantyMenuUpdate(flag)

    def setMainWindowTitle(self, title):
        self.parent().setWindowTitle(title)

    def getStatusBar(self):
        return self.parent().statusBar()

    def getPlotWidget(self):
        return self.parent().plotWidget

    def getLoggerWidget(self):
        return self.parent().loggerWidget

    def setCurrentPath(self, path):
        path = os.path.dirname(path)
        self.settings.setValue('CurrentPath', path)

    def getCurrentPath(self):
        return self.settings.value('CurrentPath')

    def getQuantyPath(self):
        return self.settings.value('Quanty/Path')

    def getVerbosity(self):
        return self.settings.value('Quanty/Verbosity')

    def getDenseBorder(self):
        return self.settings.value('Quanty/DenseBorder')


class QuantyPreferencesDialog(QDialog):

    def __init__(self, parent, settings=None):
        super(QuantyPreferencesDialog, self).__init__(parent)

        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'quanty', 'preferences.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.pathBrowsePushButton.clicked.connect(self.setExecutablePath)

        ok = self.buttonBox.button(QDialogButtonBox.Ok)
        ok.clicked.connect(self.acceptSettings)

        cancel = self.buttonBox.button(QDialogButtonBox.Cancel)
        cancel.clicked.connect(self.rejectSettings)

        self.settings = settings
        self.restoreSettings()
        self.saveSettings()

    def _findExecutable(self):
        if sys.platform == 'win32':
            executable = 'Quanty.exe'
        else:
            executable = 'Quanty'

        envPath = QStandardPaths.findExecutable(executable)
        localPath = QStandardPaths.findExecutable(
            executable, [resourceFileName(
                'crispy:' + os.path.join('modules', 'quanty', 'bin'))])

        # Check if Quanty is in the paths defined in the $PATH.
        if envPath:
            path = envPath
        # Check if Quanty is bundled with Crispy.
        elif localPath:
            path = localPath
        else:
            path = None

        return path

    def restoreSettings(self):
        settings = self.settings
        if settings is None:
            return

        settings.beginGroup('Quanty')

        path = settings.value('Path')
        if path is None or not path:
            path = self._findExecutable()
        self.pathLineEdit.setText(path)

        verbosity = settings.value('Verbosity')
        if verbosity is None:
            verbosity = '0x0000'
        self.verbosityLineEdit.setText(verbosity)

        denseBorder = settings.value('DenseBorder')
        if denseBorder is None:
            denseBorder = '50000'
        self.denseBorderLineEdit.setText(denseBorder)

        settings.endGroup()

    def saveSettings(self):
        settings = self.settings
        if settings is None:
            return

        settings.beginGroup('Quanty')
        settings.setValue('Path', self.pathLineEdit.text())
        settings.setValue('Verbosity', self.verbosityLineEdit.text())
        settings.setValue('DenseBorder', self.denseBorderLineEdit.text())
        settings.endGroup()

        settings.sync()

    def acceptSettings(self):
        self.saveSettings()
        self.close()

    def rejectSettings(self):
        self.restoreSettings()
        self.close()

    def setExecutablePath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Select File', os.path.expanduser('~'))

        if path:
            self.pathLineEdit.setText(path)


class QuantyResultDetailsDialog(QDialog):

    def __init__(self, parent=None):
        super(QuantyResultDetailsDialog, self).__init__(parent=parent)

        path = resourceFileName(
            'crispy:' + os.path.join('gui', 'uis', 'quanty', 'details.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.activateWidget()

    def activateWidget(self):
        self.spectraModel = SpectraModel(parent=self)
        self.spectraListView.setModel(self.spectraModel)
        self.spectraModel.checkStateChanged.connect(
            self.updateSpectraCheckState)
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        if sys.platform == 'darwin':
            font.setPointSize(font.pointSize() + 1)
        self.scaleLineEdit.returnPressed.connect(self.updateScale)
        self.xShiftLineEdit.returnPressed.connect(self.updateShift)
        self.yShiftLineEdit.returnPressed.connect(self.updateShift)
        self.xGaussianLineEdit.returnPressed.connect(self.updateBroadening)
        self.yGaussianLineEdit.returnPressed.connect(self.updateBroadening)
        self.inputPlainTextEdit.setFont(font)
        self.outputPlainTextEdit.setFont(font)
        self.closePushButton.setAutoDefault(False)
        self.closePushButton.clicked.connect(self.accept)
        self.normalizationComboBox.addItems(['None', 'Maximum', 'Area'])
        self.normalizationComboBox.currentTextChanged.connect(
            self.updateNormalization)

    def populateWidget(self):
        c = self.calculation
        if c.experiment == 'RIXS':
            if self.axesTabWidget.count() == 1:
                tab = self.axesTabWidget.findChild(QWidget, 'yTab')
                self.axesTabWidget.addTab(tab, tab.objectName())
                self.axesTabWidget.setTabText(1, c.yLabel)
        else:
            self.axesTabWidget.removeTab(1)
            self.axesTabWidget.setTabText(0, c.xLabel)

        self.spectraModel.setModelData(
            c.spectra.toPlot, c.spectra.toPlotChecked)
        self.spectraListView.selectionModel().setCurrentIndex(
            self.spectraModel.index(0, 0), QItemSelectionModel.Select)

        self.scaleLineEdit.setValue(c.spectra.scale)
        self.normalizationComboBox.setCurrentText(c.spectra.normalization)

        xShift, yShift = c.spectra.shift
        self.xShiftLineEdit.setValue(xShift)
        self.yShiftLineEdit.setValue(yShift)

        self.xGaussianLineEdit.setValue(c.xGaussian)
        self.xLorentzianLineEdit.setList(c.xLorentzian)
        self.yGaussianLineEdit.setValue(c.yGaussian)
        self.yLorentzianLineEdit.setList(c.yLorentzian)

        self.inputPlainTextEdit.setPlainText(c.input)
        self.outputPlainTextEdit.setPlainText(c.output)

        self.updateTitle()
        self.updateSummary()

    def updateTitle(self):
        if not self.calculation.baseName:
            title = 'Details'
        else:
            title = 'Details for {}'.format(self.calculation.baseName)
        self.setWindowTitle(title)

    def updateSummary(self):
        c = self.calculation

        summary = str()
        summary += 'Name: {}\n'.format(c.baseName)
        summary += 'Started: {}\n'.format(c.startingTime)
        summary += 'Finished: {}\n'.format(c.endingTime)
        summary += '\n'
        summary += 'Element: {}\n'.format(c.element)
        summary += 'Charge: {}\n'.format(c.charge)
        summary += 'Symmetry: {}\n'.format(c.symmetry)
        summary += 'Experiment: {}\n'.format(c.experiment)
        summary += 'Edge: {}\n'.format(c.edge)
        summary += '\n'
        summary += 'Temperature: {} K\n'.format(c.temperature)
        summary += 'Magnetic Field: {} T\n'.format(c.magneticField)
        summary += '\n'
        summary += 'Scale Factors:\n'
        summary += '    Fk: {}\n'.format(c.fk)
        summary += '    Gk: {}\n'.format(c.gk)
        summary += '    ζ: {}\n'.format(c.zeta)
        summary += '\n'
        summary += 'Hamiltonian Terms:\n'
        for term in c.hamiltonianData:
            summary += '    {}:\n'.format(term)
            configurations = c.hamiltonianData[term]
            for configuration in configurations:
                summary += '        {}:\n'.format(configuration)
                parameters = configurations[configuration]
                for parameter in parameters:
                    value = parameters[parameter]
                    if isinstance(value, list):
                        value = round(value[0] * value[1], 4)
                    indent = 12 * ' '
                    summary += '{}{}: {}\n'.format(indent, parameter, value)

        self.summaryPlainTextEdit.setPlainText(summary)

    def updateSpectraCheckState(self, checkedItems):
        self.calculation.spectra.toPlotChecked = checkedItems
        self.parent().updateResultsModelData()

    def updateScale(self):
        scale = self.scaleLineEdit.getValue()
        self.calculation.spectra.scale = scale
        self.calculation.spectra.process()
        self.parent().updateResultsModelData()

    def updateNormalization(self):
        normalization = self.normalizationComboBox.currentText()
        self.calculation.spectra.normalization = normalization
        self.calculation.spectra.process()
        self.parent().updateResultsModelData()

    def updateShift(self):
        xShift = self.xShiftLineEdit.getValue()
        yShift = self.yShiftLineEdit.getValue()
        self.calculation.spectra.shift = (xShift, yShift)
        self.calculation.spectra.process()
        self.parent().updateResultsModelData()

    def updateBroadening(self):
        self.updateXGaussian()
        if self.calculation.experiment == 'RIXS':
            self.updateYGaussian()
            broadenings = {
                'gaussian': (
                    self.calculation.xGaussian,
                    self.calculation.yGaussian),
                'lorentzian': (
                    self.calculation.xLorentzian,
                    self.calculation.yLorentzian)}
        else:
            broadenings = {
                'gaussian': (
                    self.calculation.xGaussian, ),
                'lorentzian': (
                    self.calculation.xLorentzian, )}

        self.calculation.spectra.broadenings = copy.deepcopy(broadenings)
        self.calculation.spectra.process()
        self.parent().updateResultsModelData()

    def updateXGaussian(self):
        parent = self.parent()
        xGaussian = self.xGaussianLineEdit.getValue()

        if xGaussian < 0:
            message = 'The broadening cannot be negative.'
            parent.getStatusBar().showMessage(message, parent.timeout)
            self.xGaussianLineEdit.setValue(self.calculation.xGaussian)
            return

        parent.xGaussianLineEdit.setValue(xGaussian)
        self.calculation.xGaussian = xGaussian

    def updateYGaussian(self):
        parent = self.parent()
        yGaussian = self.yGaussianLineEdit.getValue()

        if yGaussian < 0:
            message = 'The broadening cannot be negative.'
            parent.getStatusBar().showMessage(message, parent.timeout)
            self.yGaussianLineEdit.setValue(self.calculation.yGaussian)
            return

        parent.yGaussianLineEdit.setValue(yGaussian)
        self.calculation.yGaussian = yGaussian

    def clear(self):
        self.summaryPlainTextEdit.clear()
        self.spectraModel.clear()
        self.scaleLineEdit.clear()
        self.normalizationComboBox.setCurrentText('None')
        self.xShiftLineEdit.clear()
        self.yShiftLineEdit.clear()
        self.xGaussianLineEdit.clear()
        self.xLorentzianLineEdit.clear()
        self.yGaussianLineEdit.clear()
        self.yLorentzianLineEdit.clear()
        self.inputPlainTextEdit.clear()
        self.outputPlainTextEdit.clear()
        self.setWindowTitle('')


if __name__ == '__main__':
    pass
