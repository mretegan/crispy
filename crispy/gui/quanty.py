# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2019 European Synchrotron Radiation Facility
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
__date__ = '01/02/2019'


import copy
import datetime
import gzip
import json
import glob
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
    QItemSelectionModel, QProcess, Qt, QPoint, QStandardPaths, QSize)
from PyQt5.QtGui import QIcon, QFontDatabase
from PyQt5.QtWidgets import (
    QDockWidget, QFileDialog, QAction, QMenu, QWidget,
    QDialog, QDialogButtonBox)
from PyQt5.uic import loadUi
from silx.resources import resource_filename as resourceFileName

from .config import Config
from .models import HamiltonianModel, ResultsModel, SpectraModel
from ..utils.broaden import broaden
from ..utils.odict import odict
from ..utils.profiling import timeit # noqa
from ..version import version


class Spectrum(object):

    _defaults = {
        'xLabel': None,
        'yLabel': None,
        'xScale': None,
        'yScale': None,
        'axesScale': None,
        'origin': None,
        'name': None,
        'shortName': None,
        'legend': None,
    }

    def __init__(self, x, y, **kwargs):
        self.x = x
        self.y = y
        self.__dict__.update(self._defaults)
        self.__dict__.update(kwargs)

    @property
    def xScale(self):
        if self.x is None:
            return None
        return np.abs(self.x.min() - self.x.max()) / self.x.shape[0]

    @property
    def yScale(self):
        if self.y is None:
            return None
        return np.abs(self.y.min() - self.y.max()) / self.y.shape[0]

    @property
    def axesScale(self):
        return (self.xScale, self.yScale)

    @property
    def origin(self):
        if self.x is None or self.y is None:
            return (None, None)
        return (self.x.min(), self.y.min())


class Spectrum1D(Spectrum):

    def __init__(self, x, y, **kwargs):
        super(Spectrum1D, self).__init__(x, y, **kwargs)
        self._y = y

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, values):
        if values is None:
            return
        # Check for very small values.
        valuesMax = np.max(np.abs(values))
        if valuesMax < np.finfo(np.float32).eps:
            values = np.zeros_like(values)
        self._y = values

    def broaden(self, broadenings):
        for kind in broadenings:
            if kind == 'gaussian':
                fwhm, = broadenings[kind]
                fwhm = fwhm / self.xScale
                self.y = broaden(self.y, fwhm, kind)

    def shift(self, values):
        if self.x is None or values is None:
            return
        value, _ = values
        self.x = self.x + value

    def scale(self, value):
        if self.y is None or value is None:
            return
        self.y = self.y * value

    def normalize(self, value):
        if value == 'None' or self.y is None:
            return
        elif value == 'Maximum':
            yMax = np.abs(self.y).max()
            self.y = self.y / yMax
        elif value == 'Area':
            area = np.abs(np.trapz(self.y, self.x))
            self.y = self.y / area

    def plot(self, plotWidget=None):
        if plotWidget is None:
            return
        plotWidget.setGraphXLabel(self.xLabel)
        plotWidget.setGraphYLabel(self.yLabel)
        plotWidget.addCurve(self.x, self.y, legend=self.legend)


class Spectrum2D(Spectrum):

    def __init__(self, x, y, z, **kwargs):
        super(Spectrum2D, self).__init__(x, y, **kwargs)
        self.z = z

    def broaden(self, broadenings):
        if self.z is None or broadenings is None:
            return
        for kind in broadenings:
            if kind == 'gaussian':
                xFwhm, yFwhm = broadenings[kind]
                xFwhm = xFwhm / self.xScale
                yFwhm = yFwhm / self.yScale
                self.z = broaden(self.z, [xFwhm, yFwhm], kind)

    def shift(self, values):
        if self.x is None or self.y is None or values is None:
            return
        xValue, yValue = values
        self.x = self.x + xValue
        self.y = self.y + yValue

    def scale(self, value):
        if self.z is None or value is None:
            return
        self.z = self.z * value

    def normalize(self, value):
        if value == 'None' or self.z is None:
            return
        elif value == 'Maximum':
            zMax = np.abs(self.z).max()
            self.z = self.z / zMax

    def plot(self, plotWidget=None):
        if plotWidget is None:
            return
        plotWidget.setGraphXLabel(self.xLabel)
        plotWidget.setGraphYLabel(self.yLabel)
        plotWidget.addImage(
            self.z, origin=self.origin, scale=self.axesScale)


class QuantySpectra(object):

    _defaults = {
        'scale': 1.0,
        'shift': [0.0, 0.0],
        'broadenings': dict(),
        'normalization': 'None',
        'toCalculateChecked': None,
        '_toCalculateChecked': None,
        'toPlotChecked': None,
        '_toPlotChecked': None,
        'toPlot': None,
    }

    def __init__(self):
        self.__dict__.update(self._defaults)

        self.aliases = {
            'Isotropic': 'Isotropic',
            'Circular Dichroism': 'Circular Dichroism (R-L)',
            'Linear Dichroism': 'Linear Dichroism (V-H)',
        }

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
            spectrum.normalize(self.normalization)

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

            if calculation.experiment in ['XAS', 'XPS', 'XES']:

                xMin = calculation.xMin
                xMax = calculation.xMax
                xNPoints = calculation.xNPoints

                if calculation.experiment == 'XES':
                    x = np.linspace(xMin, xMax, xNPoints + 1)
                    x = x[::-1]
                    y = data[:, 2]
                    y = y / np.abs(y.max())
                else:
                    x = np.linspace(xMin, xMax, xNPoints + 1)
                    y = data[:, 2::2].flatten()

                spectrum = Spectrum1D(x, y)
                spectrum.name = spectrumName
                if len(suffix) > 2:
                    spectrum.shortName = suffix.title()
                else:
                    spectrum.shortName = suffix.upper()

                if calculation.experiment in ['XAS', ]:
                    spectrum.xLabel = 'Absorption Energy (eV)'
                elif calculation.experiment in ['XPS', ]:
                    spectrum.xLabel = 'Binding Energy (eV)'
                elif calculation.experiment in ['XES', ]:
                    spectrum.xLabel = 'Emission Energy (eV)'
                spectrum.yLabel = 'Intensity (a.u.)'

                self.broadenings = {'gaussian': (calculation.xGaussian, ), }
            else:
                xMin = calculation.xMin
                xMax = calculation.xMax
                xNPoints = calculation.xNPoints

                yMin = calculation.yMin
                yMax = calculation.yMax
                yNPoints = calculation.yNPoints

                x = np.linspace(xMin, xMax, xNPoints + 1)
                y = np.linspace(yMin, yMax, yNPoints + 1)
                z = data[:, 2::2]

                spectrum = Spectrum2D(x, y, z)
                spectrum.name = spectrumName
                if len(suffix) > 2:
                    spectrum.shortName = suffix.title()
                else:
                    spectrum.shortName = suffix.upper()

                spectrum.xLabel = 'Incident Energy (eV)'
                spectrum.yLabel = 'Energy Transfer (eV)'

                self.broadenings = {'gaussian': (calculation.xGaussian,
                                                 calculation.yGaussian), }

            self.raw.append(spectrum)

        # Process the spectra once they where read from disk.
        self.process()


class ExperimentalData(object):

    _defaults = {
        'baseName': None,
        'isChecked': True,
    }

    def __init__(self, path, **kwargs):
        self.path = path
        self.__dict__.update(self._defaults)
        self.__dict__.update(kwargs)

        self.baseName, _ = os.path.splitext(os.path.basename(self.path))
        self.load()

    def load(self):
        try:
            x, y = np.loadtxt(self.path, unpack=True)
        except ValueError:
            self.spectra = None
        else:
            self.spectra = dict()
            spectrum = Spectrum1D(x, y, normalize='None')
            self.spectra['Expt'] = spectrum


class QuantyCalculation(object):

    _defaults = {
        'version': version,
        'element': 'Ni',
        'charge': '2+',
        'symmetry': 'Oh',
        'experiment': 'XAS',
        'edge': 'L2,3 (2p)',
        'temperature': 10.0,
        'magneticField': 0.0,
        'xMin': None,
        'xMax': None,
        'xNPoints': None,
        'xLorentzian': None,
        'xGaussian': None,
        'k1': [0, 0, 1],
        'eps11': [0, 1, 0],
        'eps12': [1, 0, 0],
        'yMin': None,
        'yMax': None,
        'yNPoints': None,
        'yLorentzian': None,
        'yGaussian': None,
        'k2': [0, 0, 0],
        'eps21': [0, 0, 0],
        'eps22': [0, 0, 0],
        'spectra': None,
        'nPsisAuto': 1,
        'nConfigurations': 1,
        'nConfigurationsMax': 1,
        'fk': 0.8,
        'gk': 0.8,
        'zeta': 1.0,
        'hamiltonianData': None,
        'hamiltonianState': None,
        'baseName': None,
        'templateName': None,
        'startingTime': None,
        'endingTime': None,
        'verbosity': None,
        'denseBorder': None,
        'isChecked': True,
        'input': None,
        'output': None,
    }

    # Make the parameters a class attribute. This speeds up the creation
    # of a new calculation object; significantly.
    path = resourceFileName('quanty:parameters/parameters.json.gz')

    with gzip.open(path, 'rb') as _parametersFile:
        _parameters = json.loads(
            _parametersFile.read().decode('utf-8'), object_pairs_hook=odict)

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        self.__dict__.update(kwargs)

        branch = self._parameters['elements']
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

        if self.experiment in ['RIXS', 'XES']:
            shortEdge = self.edge[-5:-1]
        else:
            shortEdge = self.edge[-3:-1]

        self.baseName = '{}{}_{}_{}_{}'.format(
            self.element, self.charge, self.symmetry, shortEdge,
            self.experiment)

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

        if self.experiment in ['RIXS', ]:
            self.yLabel = branch['axes'][1][0]
            self.yMin = branch['axes'][1][1]
            self.yMax = branch['axes'][1][2]
            self.yNPoints = branch['axes'][1][3]
            self.yEdge = branch['axes'][1][4]
            self.yLorentzian = branch['axes'][1][5]
            self.yGaussian = branch['axes'][1][6]

        self.spectra = QuantySpectra()
        if self.experiment in ['XAS', ]:
            self.spectra.toCalculate = [
                'Isotropic', 'Circular Dichroism', 'Linear Dichroism']
        else:
            self.spectra.toCalculate = ['Isotropic', ]
        self.spectra.toCalculateChecked = ['Isotropic', ]

        if self.hamiltonianData is None:
            self.hamiltonianData = odict()

        if self.hamiltonianState is None:
            self.hamiltonianState = odict()

        self.fixedTermsParameters = odict()

        branch = self._parameters['elements'][self.element]['charges'][self.charge] # noqa

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

                if term in ('Atomic', 'Crystal Field', 'Magnetic Field'):
                    self.hamiltonianState[term] = 2
                else:
                    self.hamiltonianState[term] = 0

    def termSuffix(self, term):
        term = term.lower()
        replacements = [(' ', '_'), ('-', '_'), ('(', ''), (')', '')]
        for replacement in replacements:
            term = term.replace(*replacement)
        return term

    def saveInput(self):
        templatePath = resourceFileName(
            'quanty:' + os.path.join('templates',
                                     '{}'.format(self.templateName)))

        with open(templatePath) as p:
            self.template = p.read()

        self.input = copy.deepcopy(self.template)

        replacements = odict()

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

        if self.experiment == 'XES':
            replacements['$Emin1'] = self.xMin + 20
            replacements['$Emax1'] = self.xMax + 20

        if len(self.xLorentzian) == 1:
            replacements['$Gamma1'] = 0.1
            replacements['$Gmin1'] = self.xLorentzian[0]
            replacements['$Gmax1'] = self.xLorentzian[0]
            replacements['$Egamma1'] = (self.xMin + self.xMax) / 2
            if self.experiment == 'XES':
                replacements['$Gamma1'] = self.xLorentzian[0]
        else:
            replacements['$Gamma1'] = 0.1
            replacements['$Gmin1'] = self.xLorentzian[0]
            replacements['$Gmax1'] = self.xLorentzian[1]
            if len(self.xLorentzian) == 2:
                replacements['$Egamma1'] = (self.xMin + self.xMax) / 2
            else:
                replacements['$Egamma1'] = self.xLorentzian[2]

        s = '{{{0:.8g}, {1:.8g}, {2:.8g}}}'

        k1 = np.array(self.k1)
        k1 = k1 / np.linalg.norm(k1)
        replacements['$k1'] = s.format(k1[0], k1[1], k1[2])

        eps11 = np.array(self.eps11)
        eps11 = eps11 / np.linalg.norm(eps11)
        replacements['$eps11'] = s.format(eps11[0], eps11[1], eps11[2])

        eps12 = np.array(self.eps12)
        eps12 = eps12 / np.linalg.norm(eps12)
        replacements['$eps12'] = s.format(eps12[0], eps12[1], eps12[2])

        replacements['$spectra'] = ', '.join(
            '\'{}\''.format(p) for p in self.spectra.toCalculateChecked)

        if self.experiment in ['RIXS', ]:
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

                    if self.magneticField == 0:
                        small = np.finfo(np.float32).eps  # ~1.19e-7
                        if parameter == 'Bx':
                            value = k1[0] * small
                        elif parameter == 'By':
                            value = k1[1] * small
                        elif parameter == 'Bz':
                            value = k1[2] * small

                    key = '${}_{}_value'.format(parameter, suffix)
                    replacements[key] = '{}'.format(value)

                    if scaleFactor is not None:
                        key = '${}_{}_scale'.format(parameter, suffix)
                        replacements[key] = '{}'.format(scaleFactor)

            checkState = self.hamiltonianState[term]
            if checkState > 0:
                checkState = 1

            termSuffix = self.termSuffix(term)
            replacements['$H_{}'.format(termSuffix)] = checkState

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

        # with open('{}.json'.format(self.baseName), 'w') as f:
        #     json.dump(replacements, f, indent=2)

        with open(self.baseName + '.lua', 'w') as f:
            f.write(self.input)

        self.output = str()


class QuantyDockWidget(QDockWidget):

    def __init__(self, parent=None):
        super(QuantyDockWidget, self).__init__(parent=parent)

        # Load the external .ui file for the widget.
        path = resourceFileName('uis:quanty/main.ui')
        loadUi(path, baseinstance=self, package='crispy.gui')

        # Load the settings from file.
        config = Config()
        self.settings = config.read()

        # Set the state object
        self.state = QuantyCalculation()
        self.populateWidget()
        self.activateWidget()

        self.timeout = 4000
        self.hamiltonianSplitter.setSizes((150, 300, 10))

    def populateWidget(self):
        """
        Populate the widget using data stored in the state
        object. The order in which the individual widgets are populated
        follows their arrangment.

        The models are recreated every time the function is called.
        This might seem to be an overkill, but in practice it is very fast.
        Don't try to move the model creation outside this function; is not
        worth the effort, and there is nothing to gain from it.
        """
        self.elementComboBox.setItems(self.state._elements, self.state.element)
        self.chargeComboBox.setItems(self.state._charges, self.state.charge)
        self.symmetryComboBox.setItems(
            self.state._symmetries, self.state.symmetry)
        self.experimentComboBox.setItems(
            self.state._experiments, self.state.experiment)
        self.edgeComboBox.setItems(self.state._edges, self.state.edge)

        self.temperatureLineEdit.setValue(self.state.temperature)
        self.magneticFieldLineEdit.setValue(self.state.magneticField)

        self.axesTabWidget.setTabText(0, str(self.state.xLabel))
        self.xMinLineEdit.setValue(self.state.xMin)
        self.xMaxLineEdit.setValue(self.state.xMax)
        self.xNPointsLineEdit.setValue(self.state.xNPoints)
        self.xLorentzianLineEdit.setList(self.state.xLorentzian)
        self.xGaussianLineEdit.setValue(self.state.xGaussian)

        self.k1LineEdit.setVector(self.state.k1)
        self.eps11LineEdit.setVector(self.state.eps11)
        self.eps12LineEdit.setVector(self.state.eps12)

        if self.state.experiment in ['RIXS', ]:
            if self.axesTabWidget.count() == 1:
                tab = self.axesTabWidget.findChild(QWidget, 'yTab')
                self.axesTabWidget.addTab(tab, tab.objectName())
                self.axesTabWidget.setTabText(1, self.state.yLabel)
            self.yMinLineEdit.setValue(self.state.yMin)
            self.yMaxLineEdit.setValue(self.state.yMax)
            self.yNPointsLineEdit.setValue(self.state.yNPoints)
            self.yLorentzianLineEdit.setList(self.state.yLorentzian)
            self.yGaussianLineEdit.setValue(self.state.yGaussian)
            self.k2LineEdit.setVector(self.state.k2)
            self.eps21LineEdit.setVector(self.state.eps21)
            self.eps22LineEdit.setVector(self.state.eps22)
            text = self.eps11Label.text()
            text = re.sub('>[vσ]', '>σ', text)
            self.eps11Label.setText(text)
            text = self.eps12Label.text()
            text = re.sub('>[hπ]', '>π', text)
            self.eps12Label.setText(text)
        else:
            self.axesTabWidget.removeTab(1)
            text = self.eps11Label.text()
            text = re.sub('>[vσ]', '>v', text)
            self.eps11Label.setText(text)
            text = self.eps12Label.text()
            text = re.sub('>[hπ]', '>h', text)
            self.eps12Label.setText(text)

        # Create the spectra selection model.
        self.spectraModel = SpectraModel(parent=self)
        self.spectraModel.setModelData(
            self.state.spectra.toCalculate,
            self.state.spectra.toCalculateChecked)
        self.spectraModel.checkStateChanged.connect(
            self.updateSpectraCheckState)
        self.spectraListView.setModel(self.spectraModel)
        self.spectraListView.selectionModel().setCurrentIndex(
            self.spectraModel.index(0, 0), QItemSelectionModel.Select)

        self.fkLineEdit.setValue(self.state.fk)
        self.gkLineEdit.setValue(self.state.gk)
        self.zetaLineEdit.setValue(self.state.zeta)

        # Create the Hamiltonian model.
        self.hamiltonianModel = HamiltonianModel(parent=self)
        self.hamiltonianModel.setModelData(self.state.hamiltonianData)
        self.hamiltonianModel.setNodesCheckState(self.state.hamiltonianState)
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

        self.nPsisLineEdit.setValue(self.state.nPsis)
        self.nPsisAutoCheckBox.setChecked(self.state.nPsisAuto)
        self.nConfigurationsLineEdit.setValue(self.state.nConfigurations)

        self.nConfigurationsLineEdit.setEnabled(False)
        name = '{}-Ligands Hybridization'.format(self.state.block)
        for termName in self.state.hamiltonianData:
            if name in termName:
                termState = self.state.hamiltonianState[termName]
                if termState == 0:
                    continue
                else:
                    self.nConfigurationsLineEdit.setEnabled(True)

        if not hasattr(self, 'resultsModel'):
            # Create the results model.
            self.resultsModel = ResultsModel(parent=self)
            self.resultsModel.itemNameChanged.connect(
                self.updateCalculationName)
            self.resultsModel.itemCheckStateChanged.connect(
                self.updatePlotWidget)
            self.resultsModel.dataChanged.connect(self.updatePlotWidget)
            self.resultsModel.dataChanged.connect(self.updateResultsView)

            # Assign the results model to the results view.
            self.resultsView.setModel(self.resultsModel)
            self.resultsView.selectionModel().selectionChanged.connect(
                self.selectedResultsChanged)
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

        self.updateMainWindowTitle(self.state.baseName)

    def activateWidget(self):
        self.elementComboBox.currentTextChanged.connect(self.resetState)
        self.chargeComboBox.currentTextChanged.connect(self.resetState)
        self.symmetryComboBox.currentTextChanged.connect(self.resetState)
        self.experimentComboBox.currentTextChanged.connect(
            self.resetState)
        self.edgeComboBox.currentTextChanged.connect(self.resetState)

        self.temperatureLineEdit.returnPressed.connect(
            self.updateTemperature)
        self.magneticFieldLineEdit.returnPressed.connect(
            self.updateMagneticField)

        self.xMinLineEdit.returnPressed.connect(self.updateXMin)
        self.xMaxLineEdit.returnPressed.connect(self.updateXMax)
        self.xNPointsLineEdit.returnPressed.connect(self.updateXNPoints)
        self.xLorentzianLineEdit.returnPressed.connect(
            self.updateXLorentzian)
        self.xGaussianLineEdit.returnPressed.connect(self.updateXGaussian)
        self.k1LineEdit.returnPressed.connect(self.updateIncidentWaveVector)
        self.eps11LineEdit.returnPressed.connect(
            self.updateIncidentPolarizationVectors)

        self.yMinLineEdit.returnPressed.connect(self.updateYMin)
        self.yMaxLineEdit.returnPressed.connect(self.updateYMax)
        self.yNPointsLineEdit.returnPressed.connect(self.updateYNPoints)
        self.yLorentzianLineEdit.returnPressed.connect(
            self.updateYLorentzian)
        self.yGaussianLineEdit.returnPressed.connect(self.updateYGaussian)

        self.fkLineEdit.returnPressed.connect(self.updateScaleFactors)
        self.gkLineEdit.returnPressed.connect(self.updateScaleFactors)
        self.zetaLineEdit.returnPressed.connect(self.updateScaleFactors)

        self.syncParametersCheckBox.toggled.connect(self.updateSyncParameters)

        self.nPsisAutoCheckBox.toggled.connect(self.updateNPsisAuto)
        self.nPsisLineEdit.returnPressed.connect(self.updateNPsis)
        self.nConfigurationsLineEdit.returnPressed.connect(
            self.updateConfigurations)

        self.saveInputAsPushButton.clicked.connect(self.saveInputAs)
        self.calculationPushButton.clicked.connect(self.runCalculation)

    def enableWidget(self, flag=True, result=None):
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

        self.spectraListView.setEnabled(flag)

        self.fkLineEdit.setEnabled(flag)
        self.gkLineEdit.setEnabled(flag)
        self.zetaLineEdit.setEnabled(flag)

        self.syncParametersCheckBox.setEnabled(flag)

        self.nPsisAutoCheckBox.setEnabled(flag)
        if self.nPsisAutoCheckBox.isChecked():
            self.nPsisLineEdit.setEnabled(False)
        else:
            self.nPsisLineEdit.setEnabled(flag)

        self.hamiltonianTermsView.setEnabled(flag)
        self.hamiltonianParametersView.setEnabled(flag)
        self.resultsView.setEnabled(flag)

        self.saveInputAsPushButton.setEnabled(flag)

        if result is None or isinstance(result, QuantyCalculation):
            self.nConfigurationsLineEdit.setEnabled(flag)
            self.resultsView.setEnabled(flag)
            self.calculationPushButton.setEnabled(True)
            self.resultDetailsDialog.enableWidget(flag)
        else:
            self.nConfigurationsLineEdit.setEnabled(False)
            self.calculationPushButton.setEnabled(flag)
            self.resultsView.setEnabled(True)
            self.resultDetailsDialog.enableWidget(False)

    def updateTemperature(self):
        temperature = self.temperatureLineEdit.getValue()

        if temperature < 0:
            message = 'The temperature cannot be negative.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.temperatureLineEdit.setValue(self.state.temperature)
            return
        elif temperature == 0:
            self.nPsisAutoCheckBox.setChecked(False)
            self.updateNPsisAuto()
            self.nPsisLineEdit.setValue(1)
            self.updateNPsis()

        self.state.temperature = temperature

    def updateMagneticField(self):
        magneticField = self.magneticFieldLineEdit.getValue()

        TESLA_TO_EV = 5.788e-05

        # Normalize the current incident vector.
        k1 = np.array(self.state.k1)
        k1 = k1 / np.linalg.norm(k1)

        configurations = self.state.hamiltonianData['Magnetic Field']
        for configuration in configurations:
            parameters = configurations[configuration]
            for i, parameter in enumerate(parameters):
                value = float(magneticField * np.abs(k1[i]) * TESLA_TO_EV)
                if abs(value) == 0.0:
                        value = 0.0
                configurations[configuration][parameter] = value
        self.hamiltonianModel.updateModelData(self.state.hamiltonianData)

        self.state.magneticField = magneticField

    def updateXMin(self):
        xMin = self.xMinLineEdit.getValue()

        if xMin > self.state.xMax:
            message = ('The lower energy limit cannot be larger than '
                       'the upper limit.')
            self.getStatusBar().showMessage(message, self.timeout)
            self.xMinLineEdit.setValue(self.state.xMin)
            return

        self.state.xMin = xMin

    def updateXMax(self):
        xMax = self.xMaxLineEdit.getValue()

        if xMax < self.state.xMin:
            message = ('The upper energy limit cannot be smaller than '
                       'the lower limit.')
            self.getStatusBar().showMessage(message, self.timeout)
            self.xMaxLineEdit.setValue(self.state.xMax)
            return

        self.state.xMax = xMax

    def updateXNPoints(self):
        xNPoints = self.xNPointsLineEdit.getValue()

        xMin = self.state.xMin
        xMax = self.state.xMax
        xLorentzianMin = float(self.state.xLorentzian[0])

        xNPointsMin = int(np.floor((xMax - xMin) / xLorentzianMin))
        if xNPoints < xNPointsMin:
            message = ('The number of points must be greater than '
                       '{}.'.format(xNPointsMin))
            self.getStatusBar().showMessage(message, self.timeout)
            self.xNPointsLineEdit.setValue(self.state.xNPoints)
            return

        self.state.xNPoints = xNPoints

    def updateXLorentzian(self):
        try:
            xLorentzian = self.xLorentzianLineEdit.getList()
        except ValueError:
            message = 'Invalid data for the Lorentzian brodening.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.xLorentzianLineEdit.setList(self.state.xLorentzian)
            return

        # Do some validation of the input value.
        if len(xLorentzian) > 3:
            message = 'The broadening can have at most three elements.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.xLorentzianLineEdit.setList(self.state.xLorentzian)
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
                    self.state.xLorentzian)
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
                    self.state.xLorentzian)

        try:
            xLorentzianPivotEnergy = float(xLorentzian[2])
        except IndexError:
            pass
        else:
            xMin = self.state.xMin
            xMax = self.state.xMax

            if not (xMin < xLorentzianPivotEnergy < xMax):
                message = ('The transition point must lie between the upper '
                           'and lower energy limits.')
                self.getStatusBar().showMessage(message, self.timeout)
                self.xLorentzianLineEdit.setList(
                    self.state.xLorentzian)
                return

        self.state.xLorentzian = xLorentzian

    def updateXGaussian(self):
        xGaussian = self.xGaussianLineEdit.getValue()

        if xGaussian < 0:
            message = 'The broadening cannot be negative.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.xGaussianLineEdit.setValue(self.state.xGaussian)
            return

        self.state.xGaussian = xGaussian

    def updateIncidentWaveVector(self):
        try:
            k1 = self.k1LineEdit.getVector()
        except ValueError:
            message = 'Invalid data for the wave vector.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.k1LineEdit.setVector(self.state.k1)
            return

        if np.all(np.array(k1) == 0):
            message = 'The wave vector cannot be null.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.k1LineEdit.setVector(self.state.k1)
            return

        # The k1 value should be fine; save it.
        self.state.k1 = k1

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
        self.state.eps11 = eps11

        # Generate a second, perpendicular, polarization vector to the plane
        # defined by the wave vector and the first polarization vector.
        eps12 = np.cross(np.array(eps11), np.array(k1))
        eps12 = eps12.tolist()

        self.eps12LineEdit.setVector(eps12)
        self.state.eps12 = eps12

        # Update the magnetic field.
        self.updateMagneticField()

    def updateIncidentPolarizationVectors(self):
        try:
            eps11 = self.eps11LineEdit.getVector()
        except ValueError:
            message = 'Invalid data for the polarization vector.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.eps11LineEdit.setVector(self.state.eps11)
            return

        if np.all(np.array(eps11) == 0):
            message = 'The polarization vector cannot be null.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.eps11LineEdit.setVector(self.state.eps11)
            return

        k1 = self.state.k1
        if np.dot(np.array(k1), np.array(eps11)) != 0:
            message = ('The wave and polarization vectors need to be '
                       'perpendicular.')
            self.getStatusBar().showMessage(message, self.timeout)
            self.eps11LineEdit.setVector(self.state.eps11)
            return

        self.state.eps11 = eps11

        # Generate a second, perpendicular, polarization vector to the plane
        # defined by the wave vector and the first polarization vector.
        eps12 = np.cross(np.array(eps11), np.array(k1))
        eps12 = eps12.tolist()

        self.eps12LineEdit.setVector(eps12)
        self.state.eps12 = eps12

    def updateYMin(self):
        yMin = self.yMinLineEdit.getValue()

        if yMin > self.state.yMax:
            message = ('The lower energy limit cannot be larger than '
                       'the upper limit.')
            self.getStatusBar().showMessage(message, self.timeout)
            self.yMinLineEdit.setValue(self.state.yMin)
            return

        self.state.yMin = yMin

    def updateYMax(self):
        yMax = self.yMaxLineEdit.getValue()

        if yMax < self.state.yMin:
            message = ('The upper energy limit cannot be smaller than '
                       'the lower limit.')
            self.getStatusBar().showMessage(message, self.timeout)
            self.yMaxLineEdit.setValue(self.state.yMax)
            return

        self.state.yMax = yMax

    def updateYNPoints(self):
        yNPoints = self.yNPointsLineEdit.getValue()

        yMin = self.state.yMin
        yMax = self.state.yMax
        yLorentzianMin = float(self.state.yLorentzian[0])

        yNPointsMin = int(np.floor((yMax - yMin) / yLorentzianMin))
        if yNPoints < yNPointsMin:
            message = ('The number of points must be greater than '
                       '{}.'.format(yNPointsMin))
            self.getStatusBar().showMessage(message, self.timeout)
            self.yNPointsLineEdit.setValue(self.state.yNPoints)
            return

        self.state.yNPoints = yNPoints

    def updateYLorentzian(self):
        try:
            yLorentzian = self.yLorentzianLineEdit.getList()
        except ValueError:
            message = 'Invalid data for the Lorentzian brodening.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.yLorentzianLineEdit.setList(self.state.yLorentzian)
            return

        # Do some validation of the input value.
        if len(yLorentzian) > 3:
            message = 'The broadening can have at most three elements.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.yLorentzianLineEdit.setList(self.state.yLorentzian)
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
                    self.state.yLorentzian)
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
                    self.state.yLorentzian)

        try:
            yLorentzianPivotEnergy = float(yLorentzian[2])
        except IndexError:
            pass
        else:
            yMin = self.state.yMin
            yMax = self.state.yMax

            if not (yMin < yLorentzianPivotEnergy < yMax):
                message = ('The transition point must lie between the upper '
                           'and lower energy limits.')
                self.getStatusBar().showMessage(message, self.timeout)
                self.yLorentzianLineEdit.setList(
                    self.state.yLorentzian)
                return

        self.state.yLorentzian = list(map(float, yLorentzian))

    def updateYGaussian(self):
        yGaussian = self.yGaussianLineEdit.getValue()

        if yGaussian < 0:
            message = 'The broadening cannot be negative.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.yGaussianLineEdit.setValue(self.state.yGaussian)
            return

        self.state.yGaussian = yGaussian

    def updateSpectraCheckState(self, checkedItems):
        self.state.spectra.toCalculateChecked = checkedItems

    def updateScaleFactors(self):
        fk = self.fkLineEdit.getValue()
        gk = self.gkLineEdit.getValue()
        zeta = self.zetaLineEdit.getValue()

        if fk < 0 or gk < 0 or zeta < 0:
            message = 'The scale factors cannot be negative.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.fkLineEdit.setValue(self.state.fk)
            self.gkLineEdit.setValue(self.state.gk)
            self.zetaLineEdit.setValue(self.state.zeta)
            return

        self.state.fk = fk
        self.state.gk = gk
        self.state.zeta = zeta

        # TODO: This should be already updated to the most recent data.
        # self.state.hamiltonianData = self.hamiltonianModel.getModelData()
        terms = self.state.hamiltonianData

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
        self.hamiltonianModel.updateModelData(self.state.hamiltonianData)
        # I have no idea why this is needed. Both views should update after
        # the above function call.
        self.hamiltonianTermsView.viewport().repaint()
        self.hamiltonianParametersView.viewport().repaint()

    def updateNPsisAuto(self):
        nPsisAuto = int(self.nPsisAutoCheckBox.isChecked())

        if nPsisAuto:
            self.nPsisLineEdit.setValue(self.state.nPsisMax)
            self.nPsisLineEdit.setEnabled(False)
        else:
            self.nPsisLineEdit.setEnabled(True)

        self.state.nPsisAuto = nPsisAuto

    def updateNPsis(self):
        nPsis = self.nPsisLineEdit.getValue()

        if nPsis <= 0:
            message = 'The number of states must be larger than zero.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.nPsisLineEdit.setValue(self.state.nPsis)
            return

        if nPsis > self.state.nPsisMax:
            message = 'The selected number of states exceeds the maximum.'
            self.getStatusBar().showMessage(message, self.timeout)
            self.nPsisLineEdit.setValue(self.state.nPsisMax)
            nPsis = self.state.nPsisMax

        self.state.nPsis = nPsis

    def updateSyncParameters(self, flag):
        self.hamiltonianModel.setSyncState(flag)

    def updateHamiltonianData(self):
        self.state.hamiltonianData = self.hamiltonianModel.getModelData()

    def updateHamiltonianNodeCheckState(self, index, state):
        toggledTerm = index.data()
        states = self.hamiltonianModel.getNodesCheckState()

        # Allow only one type of hybridization with the ligands, either
        # LMCT or MLCT.
        for term in states:
            if 'LMCT' in term and 'MLCT' in toggledTerm:
                states[term] = 0
            elif 'MLCT' in term and 'LMCT' in toggledTerm:
                states[term] = 0

        self.state.hamiltonianState = states
        self.hamiltonianModel.setNodesCheckState(states)

        # Determine the maximum number of allowed configurations.
        if 'LMCT' in toggledTerm:
            if 'd' in self.state.block:
                self.state.nConfigurationsMax = 10 - self.state.nElectrons + 1
            elif 'f' in self.state.block:
                self.state.nConfigurationsMax = 14 - self.state.nElectrons + 1
        elif 'MLCT' in toggledTerm:
            self.state.nConfigurationsMax = self.state.nElectrons + 1

        term = '{}-Ligands Hybridization'.format(self.state.block)
        if term in index.data():
            if state == 0:
                nConfigurations = 1
                self.nConfigurationsLineEdit.setEnabled(False)
            elif state == 2:
                if self.state.nConfigurationsMax == 1:
                    nConfigurations = 1
                else:
                    nConfigurations = 2
                self.nConfigurationsLineEdit.setEnabled(True)

            self.nConfigurationsLineEdit.setValue(nConfigurations)
            self.state.nConfigurations = nConfigurations

    def updateConfigurations(self, *args):
        nConfigurations = self.nConfigurationsLineEdit.getValue()

        if nConfigurations > self.state.nConfigurationsMax:
            message = 'The maximum number of configurations is {}.'.format(
                self.state.nConfigurationsMax)
            self.getStatusBar().showMessage(message, self.timeout)
            self.nConfigurationsLineEdit.setValue(
                self.state.nConfigurationsMax)
            nConfigurations = self.state.nConfigurationsMax

        self.state.nConfigurations = nConfigurations

    def saveInput(self):
        # TODO: If the user changes a value in a widget without pressing Return
        # before running the calculation, the values are not updated.

        self.state.verbosity = self.getVerbosity()
        self.state.denseBorder = self.getDenseBorder()

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
            self.state.saveInput()
        except (IOError, OSError) as e:
            message = 'Failed to write the Quanty input file.'
            self.getStatusBar().showMessage(message, self.timeout)
            raise e

    def saveInputAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Quanty Input',
            os.path.join(self.getCurrentPath(), '{}.lua'.format(
                self.state.baseName)), 'Quanty Input File (*.lua)')

        if path:
            basename = os.path.basename(path)
            self.state.baseName, _ = os.path.splitext(basename)
            self.setCurrentPath(path)
            try:
                self.saveInput()
            except (IOError, OSError):
                return
            self.updateMainWindowTitle(self.state.baseName)

    def saveAllResultsAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Results',
            os.path.join(self.getCurrentPath(), '{}.pkl'.format(
                'untitled')), 'Pickle File (*.pkl)')

        if path:
            self.setCurrentPath(path)
            results = self.resultsModel.getAllItems()
            results.reverse()
            with open(path, 'wb') as p:
                pickle.dump(results, p, pickle.HIGHEST_PROTOCOL)

    def saveSelectedResultsAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Results',
            os.path.join(self.getCurrentPath(), '{}.pkl'.format(
                'untitled')), 'Pickle File (*.pkl)')

        if path:
            self.setCurrentPath(path)
            indexes = self.resultsView.selectedIndexes()
            results = self.resultsModel.getSelectedItems(indexes)
            results.reverse()
            with open(path, 'wb') as p:
                pickle.dump(results, p, pickle.HIGHEST_PROTOCOL)

    def resetState(self):
        element = self.elementComboBox.currentText()
        charge = self.chargeComboBox.currentText()
        symmetry = self.symmetryComboBox.currentText()
        experiment = self.experimentComboBox.currentText()
        edge = self.edgeComboBox.currentText()

        self.state = QuantyCalculation(
            element=element, charge=charge, symmetry=symmetry,
            experiment=experiment, edge=edge)

        self.resultsView.selectionModel().clearSelection()
        self.populateWidget()
        self.updateMainWindowTitle(self.state.baseName)
        self.resultDetailsDialog.clear()

    def removeSelectedCalculations(self):
        indexes = self.resultsView.selectedIndexes()
        if not indexes:
            self.getPlotWidget().reset()
            return
        self.resultsModel.removeItems(indexes)
        # self.resultsView.reset()

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
            self.updateMainWindowTitle(self.state.baseName)
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
                               'properly. Is the PATH set correctly?')
                    self.getStatusBar().showMessage(message, 2 * self.timeout)
                    return
                else:
                    raise e

        # Write the input file to disk.
        try:
            self.saveInput()
        except (IOError, OSError):
            return

        # Disable the widget while the calculation is running.
        self.enableWidget(False)

        self.state.startingTime = datetime.datetime.now()

        # Run Quanty using QProcess.
        self.process = QProcess()

        self.process.start(command, (self.state.baseName + '.lua', ))
        message = (
            'Running "Quanty {}" in {}.'.format(
                self.state.baseName + '.lua', os.getcwd()))
        self.getStatusBar().showMessage(message)

        if sys.platform == 'win32' and self.process.waitForStarted():
            self.updateCalculationPushButton()
        else:
            self.process.started.connect(self.updateCalculationPushButton)
        self.process.readyReadStandardOutput.connect(self.handleOutputLogging)
        self.process.finished.connect(self.processCalculation)

    def updateCalculationPushButton(self, kind='stop'):
        self.calculationPushButton.disconnect()

        if kind == 'run':
            icon = QIcon(resourceFileName('icons:play.svg'))
            self.calculationPushButton.setIcon(icon)
            self.calculationPushButton.setText('Run')
            self.calculationPushButton.setToolTip('Run Quanty.')

            self.calculationPushButton.clicked.connect(self.runCalculation)
        elif kind == 'stop':
            icon = QIcon(resourceFileName('icons:stop.svg'))
            self.calculationPushButton.setIcon(icon)
            self.calculationPushButton.setText('Stop')
            self.calculationPushButton.setToolTip('Stop Quanty.')
            self.calculationPushButton.clicked.connect(self.stopCalculation)
        else:
            pass

    def stopCalculation(self):
        self.process.kill()

    def processCalculation(self, *args):
        startingTime = self.state.startingTime

        # When did I finish?
        endingTime = datetime.datetime.now()
        self.state.endingTime = endingTime

        # Re-enable the widget when the calculation has finished.
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

        # Scroll to the bottom of the logger widget.
        scrollBar = self.getLoggerWidget().verticalScrollBar()
        scrollBar.setValue(scrollBar.maximum())

        # Load the spectra from disk.
        self.state.spectra.loadFromDisk(self.state)

        # If the calculated spectrum is an image, uncheck all the other
        # calculations. This way the current result can be disaplyed in the
        # plot widget.
        if self.state.experiment in ['RIXS', ]:
            self.resultsModel.uncheckAllItems()

        # Once all processing is done, store the state in the
        # results model. Upon finishing this, a signal is emitted by the
        # model which triggers some updates to be performed.
        self.state.isChecked = True
        self.resultsModel.appendItems(self.state)

        # If the "Hamiltonian Setup" page is currently selected, when the
        # current widget is set to the "Results Page", the former is not
        # displayed. To avoid this I switch first to the "General Setup" page.
        self.quantyToolBox.setCurrentWidget(self.generalPage)
        self.quantyToolBox.setCurrentWidget(self.resultsPage)
        self.resultsView.setFocus()

        # Remove files if requested.
        if self.doRemoveFiles():
            os.remove('{}.lua'.format(self.state.baseName))
            spectra = glob.glob('{}_*.spec'.format(self.state.baseName))
            for spectrum in spectra:
                os.remove(spectrum)

    def selectedHamiltonianTermChanged(self):
        index = self.hamiltonianTermsView.currentIndex()
        self.hamiltonianParametersView.setRootIndex(index)

    def showResultsContextMenu(self, position):
        icon = QIcon(resourceFileName('icons:clipboard.svg'))
        self.showDetailsAction = QAction(
            icon, 'Show Details', self, triggered=self.showResultDetailsDialog)

        icon = QIcon(resourceFileName('icons:save.svg'))
        self.saveSelectedResultsAsAction = QAction(
            icon, 'Save Selected Results As...', self,
            triggered=self.saveSelectedResultsAs)
        self.saveAllResultsAsAction = QAction(
            icon, 'Save All Results As...', self,
            triggered=self.saveAllResultsAs)

        icon = QIcon(resourceFileName('icons:trash.svg'))
        self.removeSelectedResultsAction = QAction(
            icon, 'Remove Selected Results', self,
            triggered=self.removeSelectedCalculations)
        self.removeAllResultsAction = QAction(
            icon, 'Remove All Results', self, triggered=self.removeAllResults)

        icon = QIcon(resourceFileName('icons:folder-open.svg'))
        self.loadResultsAction = QAction(
            icon, 'Load Results', self, triggered=self.loadResults)

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
        the index. This should be the last index of the model. Finally updade
        the context menu.

        The selectionChanged signal is used to trigger the update of
        the Quanty dock widget and result details dialog.

        :param index: Index of the last item of the model.
        :type index: QModelIndex
        """

        flags = (QItemSelectionModel.Clear | QItemSelectionModel.Rows |
                 QItemSelectionModel.Select)
        self.resultsView.selectionModel().select(index, flags)
        self.resultsView.resizeColumnsToContents()
        self.resultsView.setFocus()

    def getLastSelectedResultsModelIndex(self):
        rows = self.resultsView.selectionModel().selectedRows()
        try:
            index = rows[-1]
        except IndexError:
            index = None
        return index

    def selectedResultsChanged(self):
        indexes = self.resultsView.selectedIndexes()
        if len(indexes) > 1:
            return

        index = self.getLastSelectedResultsModelIndex()
        if index is None:
            result = None
        else:
            result = self.resultsModel.getItem(index)

        if isinstance(result, QuantyCalculation):
            self.enableWidget(True, result)
            self.state = result
            self.populateWidget()
            self.resultDetailsDialog.populateWidget()
        elif isinstance(result, ExperimentalData):
            self.enableWidget(False, result)
            self.updateMainWindowTitle(result.baseName)
            self.resultDetailsDialog.clear()
        else:
            self.enableWidget(True, result)
            self.resetState()

    def updateResultsModelData(self):
        index = self.getLastSelectedResultsModelIndex()
        if index is None:
            return
        self.resultsModel.updateItem(index, self.state)
        self.resultsView.viewport().repaint()

    def updatePlotWidget(self):
        """Updating the plotting widget should not require any information
        about the current state of the widget."""
        pw = self.getPlotWidget()
        pw.reset()

        results = self.resultsModel.getCheckedItems()

        for result in results:
            if isinstance(result, ExperimentalData):
                spectrum = result.spectra['Expt']
                spectrum.legend = '{}-{}'.format(result.index, 'Expt')
                spectrum.xLabel = 'X'
                spectrum.yLabel = 'Y'
                spectrum.plot(plotWidget=pw)
            else:
                if len(results) > 1 and result.experiment in ['RIXS', ]:
                    continue
                for spectrum in result.spectra.processed:
                    spectrum.legend = '{}-{}'.format(
                        result.index, spectrum.shortName)
                    if spectrum.name in result.spectra.toPlotChecked:
                        spectrum.plot(plotWidget=pw)

    def showResultDetailsDialog(self):
        self.resultDetailsDialog.show()
        self.resultDetailsDialog.raise_()

    def updateCalculationName(self, name):
        self.state.baseName = name
        self.updateMainWindowTitle(name)
        self.resultDetailsDialog.updateTitle(name)
        if isinstance(self.state, QuantyCalculation):
            self.resultDetailsDialog.updateSummary()

    def loadExperimentalData(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Load Experimental Data',
            self.getCurrentPath(), 'Data File (*.dat)')

        if path:
            result = ExperimentalData(path)
            if result.spectra is not None:
                self.resultsModel.appendItems([result])
            else:
                message = ('Failed to read experimental data. Please check '
                           'that the file is properly formatted.')
                self.getStatusBar().showMessage(message, self.timeout)

    def handleOutputLogging(self):
        self.process.setReadChannel(QProcess.StandardOutput)
        data = self.process.readAllStandardOutput().data()
        data = data.decode('utf-8').rstrip()
        self.getLoggerWidget().appendPlainText(data)
        self.state.output = self.state.output + data

    def handleErrorLogging(self):
        self.process.setReadChannel(QProcess.StandardError)
        data = self.process.readAllStandardError().data()
        self.getLoggerWidget().appendPlainText(data.decode('utf-8'))

    def updateMainWindowTitle(self, name=None):
        if name is None:
            title = 'Crispy'
        else:
            title = 'Crispy - {}'.format(name)
        self.setMainWindowTitle(title)

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
        path = self.settings.value('CurrentPath')
        if path is None:
            path = os.path.expanduser('~')
        return path

    def getQuantyPath(self):
        return self.settings.value('Quanty/Path')

    def getVerbosity(self):
        return self.settings.value('Quanty/Verbosity')

    def getDenseBorder(self):
        return self.settings.value('Quanty/DenseBorder')

    def doRemoveFiles(self):
        return self.settings.value('Quanty/RemoveFiles', True, type=bool)


class QuantyPreferencesDialog(QDialog):

    def __init__(self, parent):
        super(QuantyPreferencesDialog, self).__init__(parent)

        path = resourceFileName('uis:quanty/preferences.ui')
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.pathBrowsePushButton.clicked.connect(self.setExecutablePath)

        ok = self.buttonBox.button(QDialogButtonBox.Ok)
        ok.clicked.connect(self.acceptSettings)

        cancel = self.buttonBox.button(QDialogButtonBox.Cancel)
        cancel.clicked.connect(self.rejectSettings)

        # Loading and saving the settings is needed here, due to the
        # call to _findExecutable.
        self.loadSettings()
        self.saveSettings()

    def showEvent(self, event):
        self.loadSettings()
        super(QuantyPreferencesDialog, self).showEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super(QuantyPreferencesDialog, self).closeEvent(event)

    def _findExecutable(self):
        if sys.platform == 'win32':
            executable = 'Quanty.exe'
        else:
            executable = 'Quanty'

        envPath = QStandardPaths.findExecutable(executable)
        localPath = QStandardPaths.findExecutable(
            executable, [resourceFileName('quanty:bin')])

        # Check if Quanty is in the paths defined in the $PATH.
        if envPath:
            path = envPath
        # Check if Quanty is bundled with Crispy.
        elif localPath:
            path = localPath
        else:
            path = None

        return path

    def loadSettings(self):
        config = Config()
        self.settings = config.read()

        if self.settings is None:
            return

        self.settings.beginGroup('Quanty')

        size = self.settings.value('Size')
        if size is not None:
            self.resize(QSize(size))

        pos = self.settings.value('Position')
        if pos is not None:
            self.move(QPoint(pos))

        path = self.settings.value('Path')
        # In the future remove some settings if there is an version update.
        if version <= '0.7.2':
            path = None
        if path is None or not path:
            path = self._findExecutable()
        self.pathLineEdit.setText(path)

        verbosity = self.settings.value('Verbosity')
        if verbosity is None:
            verbosity = '0x0000'
        self.verbosityLineEdit.setText(verbosity)

        denseBorder = self.settings.value('DenseBorder')
        if denseBorder is None:
            denseBorder = '2000'
        self.denseBorderLineEdit.setText(denseBorder)

        removeFiles = self.settings.value('RemoveFiles', True, type=bool)
        if removeFiles is None:
            removeFiles = False
        self.removeFilesCheckBox.setChecked(removeFiles)

        self.settings.endGroup()

    def saveSettings(self):
        if self.settings is None:
            return

        self.settings.beginGroup('Quanty')
        self.settings.setValue('Path', self.pathLineEdit.text())
        self.settings.setValue('Verbosity', self.verbosityLineEdit.text())
        self.settings.setValue('DenseBorder', self.denseBorderLineEdit.text())
        self.settings.setValue(
            'RemoveFiles', self.removeFilesCheckBox.isChecked())
        self.settings.setValue('Size', self.size())
        self.settings.setValue('Position', self.pos())
        self.settings.endGroup()
        self.settings.sync()

    def acceptSettings(self):
        self.saveSettings()
        self.close()

    def rejectSettings(self):
        self.loadSettings()
        self.close()

    def setExecutablePath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Select File', os.path.expanduser('~'))

        if path:
            self.pathLineEdit.setText(path)


class QuantyResultDetailsDialog(QDialog):

    def __init__(self, parent=None):
        super(QuantyResultDetailsDialog, self).__init__(parent=parent)

        path = resourceFileName('uis:quanty/details.ui')
        loadUi(path, baseinstance=self, package='crispy.gui')

        self.activateWidget()

    def showEvent(self, event):
        self.loadSettings()
        super(QuantyResultDetailsDialog, self).showEvent(event)

    def closeEvent(self, event):
        self.saveSettings()
        super(QuantyResultDetailsDialog, self).closeEvent(event)

    def activateWidget(self):
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        if sys.platform == 'darwin':
            font.setPointSize(font.pointSize() + 1)

        self.spectraModel = SpectraModel(parent=self)
        self.spectraListView.setModel(self.spectraModel)
        self.spectraModel.checkStateChanged.connect(
            self.updateSpectraCheckState)

        self.scaleLineEdit.returnPressed.connect(self.updateScale)
        self.normalizationComboBox.addItems(['None', 'Maximum', 'Area'])
        self.normalizationComboBox.currentTextChanged.connect(
            self.updateNormalization)

        self.xShiftLineEdit.returnPressed.connect(self.updateShift)
        self.yShiftLineEdit.returnPressed.connect(self.updateShift)
        self.xGaussianLineEdit.returnPressed.connect(self.updateBroadening)
        self.yGaussianLineEdit.returnPressed.connect(self.updateBroadening)

        self.summaryPlainTextEdit.setFont(font)
        self.inputPlainTextEdit.setFont(font)
        self.outputPlainTextEdit.setFont(font)

        self.closePushButton.setAutoDefault(False)
        self.closePushButton.clicked.connect(self.close)

    def populateWidget(self):
        self.state = self.parent().state

        self.spectraModel.setModelData(
            self.state.spectra.toPlot, self.state.spectra.toPlotChecked)
        self.spectraListView.selectionModel().setCurrentIndex(
            self.spectraModel.index(0, 0), QItemSelectionModel.Select)

        self.scaleLineEdit.setValue(self.state.spectra.scale)
        self.normalizationComboBox.blockSignals(True)
        self.normalizationComboBox.setCurrentText(
            self.state.spectra.normalization)
        self.normalizationComboBox.blockSignals(False)

        if self.state.experiment in ['RIXS', ]:
            if self.axesTabWidget.count() == 1:
                tab = self.axesTabWidget.findChild(QWidget, 'yTab')
                self.axesTabWidget.addTab(tab, tab.objectName())
                self.axesTabWidget.setTabText(1, self.state.yLabel)
            self.scaleLineEdit.setEnabled(False)
            self.normalizationComboBox.setEnabled(False)
        else:
            self.axesTabWidget.removeTab(1)
            self.axesTabWidget.setTabText(0, self.state.xLabel)
            self.scaleLineEdit.setEnabled(True)
            self.normalizationComboBox.setEnabled(True)

        xShift, yShift = self.state.spectra.shift
        self.xShiftLineEdit.setValue(xShift)
        self.yShiftLineEdit.setValue(yShift)

        self.xGaussianLineEdit.setValue(self.state.xGaussian)
        self.xLorentzianLineEdit.setList(self.state.xLorentzian)
        self.yGaussianLineEdit.setValue(self.state.yGaussian)
        self.yLorentzianLineEdit.setList(self.state.yLorentzian)

        self.inputPlainTextEdit.setPlainText(self.state.input)
        self.outputPlainTextEdit.setPlainText(self.state.output)

        self.updateTitle(self.state.baseName)
        self.updateSummary()

    def updateTitle(self, name=None):
        if name is None:
            title = 'Details'
        else:
            title = 'Details for {}'.format(name)
        self.setWindowTitle(title)

    def updateSummary(self):
        # TODO: Add the wave vector to the summary.
        summary = str()
        summary += 'Name: {}\n'.format(self.state.baseName)
        summary += 'Started: {}\n'.format(self.state.startingTime)
        summary += 'Finished: {}\n'.format(self.state.endingTime)
        summary += '\n'
        summary += 'Element: {}\n'.format(self.state.element)
        summary += 'Charge: {}\n'.format(self.state.charge)
        summary += 'Symmetry: {}\n'.format(self.state.symmetry)
        summary += 'Experiment: {}\n'.format(self.state.experiment)
        summary += 'Edge: {}\n'.format(self.state.edge)
        summary += '\n'
        summary += 'Temperature: {} K\n'.format(self.state.temperature)
        summary += 'Magnetic Field: {} T\n'.format(self.state.magneticField)
        summary += '\n'
        summary += 'Scale Factors:\n'
        summary += '    Fk: {}\n'.format(self.state.fk)
        summary += '    Gk: {}\n'.format(self.state.gk)
        summary += '    ζ: {}\n'.format(self.state.zeta)
        summary += '\n'
        summary += 'Hamiltonian Terms:\n'
        for term in self.state.hamiltonianData:
            summary += '    {}:\n'.format(term)
            configurations = self.state.hamiltonianData[term]
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

    def updateResultsModelData(self):
        self.parent().updateResultsModelData()

    def updateSpectraCheckState(self, checkedItems):
        self.state.spectra.toPlotChecked = checkedItems
        self.updateResultsModelData()

    def updateScale(self):
        scale = self.scaleLineEdit.getValue()
        self.state.spectra.scale = scale
        self.state.spectra.process()
        self.updateResultsModelData()

    def updateNormalization(self):
        normalization = self.normalizationComboBox.currentText()
        # In experimental data is spectrum, not spectra. Change this!
        self.state.spectra.normalization = normalization
        self.state.spectra.process()
        self.updateResultsModelData()

    def updateShift(self):
        xShift = self.xShiftLineEdit.getValue()
        yShift = self.yShiftLineEdit.getValue()
        self.state.spectra.shift = (xShift, yShift)
        self.state.spectra.process()
        self.updateResultsModelData()

    def updateBroadening(self):
        self.updateXGaussian()

        if self.state.experiment in ['RIXS', ]:
            self.updateYGaussian()
            broadenings = {
                'gaussian': (
                    self.state.xGaussian,
                    self.state.yGaussian),
                'lorentzian': (
                    self.state.xLorentzian,
                    self.state.yLorentzian)}
        else:
            broadenings = {
                'gaussian': (
                    self.state.xGaussian, ),
                'lorentzian': (
                    self.state.xLorentzian, )}

        self.state.spectra.broadenings = copy.deepcopy(broadenings)
        self.state.spectra.process()
        self.updateResultsModelData()

    def updateXGaussian(self):
        parent = self.parent()
        xGaussian = self.xGaussianLineEdit.getValue()

        if xGaussian < 0:
            message = 'The broadening cannot be negative.'
            parent.getStatusBar().showMessage(message, parent.timeout)
            self.xGaussianLineEdit.setValue(self.state.xGaussian)
            return

        parent.xGaussianLineEdit.setValue(xGaussian)
        self.state.xGaussian = xGaussian

    def updateYGaussian(self):
        parent = self.parent()
        yGaussian = self.yGaussianLineEdit.getValue()

        if yGaussian < 0:
            message = 'The broadening cannot be negative.'
            parent.getStatusBar().showMessage(message, parent.timeout)
            self.yGaussianLineEdit.setValue(self.state.yGaussian)
            return

        parent.yGaussianLineEdit.setValue(yGaussian)
        self.state.yGaussian = yGaussian

    def enableWidget(self, flag):
        self.summaryPlainTextEdit.setEnabled(flag)
        self.spectraListView.setEnabled(flag)
        self.scaleLineEdit.setEnabled(flag)
        self.normalizationComboBox.setEnabled(flag)
        self.xShiftLineEdit.setEnabled(flag)
        self.yShiftLineEdit.setEnabled(flag)
        self.xGaussianLineEdit.setEnabled(flag)
        self.yGaussianLineEdit.setEnabled(flag)
        self.inputPlainTextEdit.setEnabled(flag)
        self.outputPlainTextEdit.setEnabled(flag)

    def clear(self):
        self.summaryPlainTextEdit.clear()
        self.spectraModel.clear()
        self.scaleLineEdit.clear()
        self.normalizationComboBox.blockSignals(True)
        self.normalizationComboBox.setCurrentText('None')
        self.normalizationComboBox.blockSignals(False)
        self.xShiftLineEdit.clear()
        self.yShiftLineEdit.clear()
        self.xGaussianLineEdit.clear()
        self.xLorentzianLineEdit.clear()
        self.yGaussianLineEdit.clear()
        self.yLorentzianLineEdit.clear()
        self.inputPlainTextEdit.clear()
        self.outputPlainTextEdit.clear()
        self.updateTitle()

    def loadSettings(self):
        config = Config()
        self.settings = config.read()

        if self.settings is None:
            return

        self.settings.beginGroup('DetailsDialog')

        size = self.settings.value('Size')
        if size is not None:
            self.resize(QSize(size))

        pos = self.settings.value('Position')
        if pos is not None:
            self.move(QPoint(pos))

        self.settings.endGroup()

    def saveSettings(self):
        if self.settings is None:
            return

        self.settings.beginGroup('DetailsDialog')
        self.settings.setValue('Size', self.size())
        self.settings.setValue('Position', self.pos())
        self.settings.endGroup()

        self.settings.sync()


if __name__ == '__main__':
    pass
