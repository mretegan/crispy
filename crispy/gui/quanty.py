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
__date__ = '02/06/2017'


import collections
import copy
import datetime
import glob
import json
import math
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
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import (
    QAbstractItemView, QDockWidget, QFileDialog, QAction, QMenu, QListView,
    QDoubleSpinBox, QWidget)
from PyQt5.uic import loadUi

from .models.treemodel import TreeModel
from .models.listmodel import ListModel
from .views.treeview import TreeView
from ..resources import resourceFileName


class OrderedDict(collections.OrderedDict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


class QuantyDockWidget(QDockWidget):

    _defaults = {
        'element': 'Ni',
        'charge': '2+',
        'symmetry': 'Oh',
        'experiment': 'XAS',
        'edge': 'L2,3 (2p)',
        'temperature': 10.0,
        'magneticField': (0.0, 0.0, 0.0),
        'shells': None,
        'nPsis': None,
        'energies': None,
        'hamiltonianParameters': None,
        'hamiltonianTermsCheckState': None,
        'spectra': None,
        'templateName': None,
        'baseName': 'untitled',
        'label': None,
        'uuid': None,
        'startingTime': None,
        'endingTime': None,
        }

    def __init__(self):
        super(QuantyDockWidget, self).__init__()
        self.__dict__.update(self._defaults)

        # Load the external .ui file for the widget.
        path = resourceFileName(os.path.join('gui', 'uis', 'quanty.ui'))
        loadUi(path, baseinstance=self, package='crispy.gui')

        # Remove macOS focus border.
        for child in self.findChildren((QListView, TreeView, QDoubleSpinBox)):
            child.setAttribute(Qt.WA_MacShowFocusRect, False)

        self.setParameters()
        self.activateUi()

    def setParameters(self):
        # Load the external parameters.
        path = resourceFileName(os.path.join(
            'modules', 'quanty', 'parameters', 'ui.json'))

        with open(path) as p:
            uiParameters = json.loads(
                p.read(), object_pairs_hook=collections.OrderedDict)

        self.elements = uiParameters['elements']
        if self.element not in self.elements:
            self.element = tuple(self.elements)[0]

        self.charges = self.elements[self.element]['charges']
        if self.charge not in self.charges:
            self.charge = tuple(self.charges)[0]

        self.symmetries = self.charges[self.charge]['symmetries']
        if self.symmetry not in self.symmetries:
            self.symmetry = tuple(self.symmetries)[0]

        self.experiments = self.symmetries[self.symmetry]['experiments']
        if self.experiment not in self.experiments:
            self.experiment = tuple(self.experiments)[0]

        self.edges = self.experiments[self.experiment]['edges']
        if self.edge not in self.edges:
            self.edge = tuple(self.edges)[0]

        branch = self.edges[self.edge]

        self.shells = branch['shells']
        self.nPsis = branch['nPsis']
        self.energies = branch['energies']
        self.templateName = branch['template name']
        self.hamiltonians = branch['configurations']

        path = resourceFileName(os.path.join(
            'modules', 'quanty', 'parameters', 'hamiltonian.json'))

        with open(path) as p:
            hamiltonianParameters = json.loads(
                p.read(), object_pairs_hook=collections.OrderedDict)

        self.hamiltonianParameters = OrderedDict()
        self.hamiltonianTermsCheckState = collections.OrderedDict()

        for hamiltonian in self.hamiltonians:
            label = '{} Hamiltonian'.format(hamiltonian[0])
            configuration = hamiltonian[1]

            terms = (hamiltonianParameters['elements']
                     [self.element]['charges'][self.charge]['configurations']
                     [configuration]['Hamiltonian Terms'])

            for term in terms:
                if ('Coulomb' in term) or ('Spin-Orbit Coupling' in term):
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
                    self.hamiltonianParameters[term][label][parameter] = (
                        parameters[parameter], scaling)

                if 'Hybridization' in term:
                    self.hamiltonianTermsCheckState[term] = 0
                else:
                    self.hamiltonianTermsCheckState[term] = 2

        self.setUi()

    def updateParameters(self):
        self.element = self.elementComboBox.currentText()
        self.charge = self.chargeComboBox.currentText()
        self.symmetry = self.symmetryComboBox.currentText()
        self.experiment = self.experimentComboBox.currentText()
        self.edge = self.edgeComboBox.currentText()

        self.baseName = self._defaults['baseName']
        self.updateMainWindowTitle()

        self.setParameters()

    def setUi(self):
        # Set the values for the combo boxes.
        self.elementComboBox.setItems(self.elements, self.element)
        self.chargeComboBox.setItems(self.charges, self.charge)
        self.symmetryComboBox.setItems(self.symmetries, self.symmetry)
        self.experimentComboBox.setItems(self.experiments, self.experiment)
        self.edgeComboBox.setItems(self.edges, self.edge)

        # Set the temperature spin box.
        self.temperatureDoubleSpinBox.setValue(self.temperature)

        # Set the magnetic field spin boxes.
        self.magneticFieldXDoubleSpinBox.setValue(self.magneticField[0])
        self.magneticFieldYDoubleSpinBox.setValue(self.magneticField[1])
        self.magneticFieldZDoubleSpinBox.setValue(self.magneticField[2])

        # Set the labels, ranges, etc.
        self.energiesTabWidget.setTabText(0, self.energies[0][0])
        self.e1MinDoubleSpinBox.setValue(self.energies[0][1])
        self.e1MaxDoubleSpinBox.setValue(self.energies[0][2])
        self.e1NPointsDoubleSpinBox.setValue(self.energies[0][3])
        self.e1LorentzianBroadeningDoubleSpinBox.setValue(self.energies[0][4])

        if 'RIXS' in self.experiment:
            tab = self.energiesTabWidget.findChild(QWidget, 'e2Tab')
            self.energiesTabWidget.addTab(tab, tab.objectName())
            self.energiesTabWidget.setTabText(1, self.energies[1][0])
            self.e2MinDoubleSpinBox.setValue(self.energies[1][1])
            self.e2MaxDoubleSpinBox.setValue(self.energies[1][2])
            self.e2NPointsDoubleSpinBox.setValue(self.energies[1][3])
            self.e2LorentzianBroadeningDoubleSpinBox.setValue(
                self.energies[1][4])
            self.e1GaussianBroadeningDoubleSpinBox.setEnabled(False)
            self.e2GaussianBroadeningDoubleSpinBox.setEnabled(False)
        else:
            self.energiesTabWidget.removeTab(1)
            self.e1GaussianBroadeningDoubleSpinBox.setEnabled(True)
            self.e2GaussianBroadeningDoubleSpinBox.setEnabled(True)

        self.nPsisDoubleSpinBox.setValue(self.nPsis)

        # Create the Hamiltonian model.
        self.hamiltonianModel = TreeModel(
            ('Parameter', 'Value', 'Scaling'), self.hamiltonianParameters)
        self.hamiltonianModel.setNodesCheckState(
            self.hamiltonianTermsCheckState)

        # Assign the Hamiltonian model to the Hamiltonian terms view.
        self.hamiltonianTermsView.setModel(self.hamiltonianModel)
        self.hamiltonianTermsView.selectionModel().setCurrentIndex(
            self.hamiltonianModel.index(0, 0), QItemSelectionModel.Select)

        # Assign the Hamiltonian model to the Hamiltonian parameters view, and
        # set some properties.
        self.hamiltonianParametersView.setModel(self.hamiltonianModel)
        self.hamiltonianParametersView.expandAll()
        self.hamiltonianParametersView.resizeAllColumnsToContents()
        self.hamiltonianParametersView.setColumnWidth(0, 160)
        self.hamiltonianParametersView.setAlternatingRowColors(True)

        index = self.hamiltonianTermsView.currentIndex()
        self.hamiltonianParametersView.setRootIndex(index)

        self.hamiltonianTermsView.selectionModel().selectionChanged.connect(
            self.selectedHamiltonianTermChanged)

        # Set the sizes of the two views.
        self.hamiltonianSplitter.setSizes((120, 300))

        # Create the results model and assign it to the view.
        if not hasattr(self, 'resultsModel'):
            self.resultsModel = ListModel()
            self.resultsView.setSelectionMode(
                QAbstractItemView.ExtendedSelection)
            self.resultsView.setModel(self.resultsModel)
            self.resultsView.selectionModel().selectionChanged.connect(
                self.selectedCalculationsChanged)
            # Add a context menu
            self.resultsView.setContextMenuPolicy(Qt.CustomContextMenu)
            self.resultsView.customContextMenuRequested[QPoint].connect(
                self.createContextMenu)
            self.resultsView.setAlternatingRowColors(True)

    def activateUi(self):
        self.elementComboBox.currentTextChanged.connect(
            self.updateParameters)
        self.chargeComboBox.currentTextChanged.connect(
            self.updateParameters)
        self.symmetryComboBox.currentTextChanged.connect(
            self.updateParameters)
        self.experimentComboBox.currentTextChanged.connect(
            self.updateParameters)
        self.edgeComboBox.currentTextChanged.connect(
            self.updateParameters)

        self.saveInputAsPushButton.clicked.connect(self.saveInputAs)
        self.calculationPushButton.clicked.connect(self.runCalculation)

        self.e1GaussianBroadeningDoubleSpinBox.valueChanged.connect(
                self.replot)
        self.e1LorentzianBroadeningDoubleSpinBox.valueChanged.connect(
                self.replot)

    def getParameters(self):
        self.element = self.elementComboBox.currentText()
        self.charge = self.chargeComboBox.currentText()
        self.symmetry = self.symmetryComboBox.currentText()
        self.experiment = self.experimentComboBox.currentText()
        self.edge = self.edgeComboBox.currentText()

        self.temperature = self.temperatureDoubleSpinBox.value()
        self.magneticField = (
            self.magneticFieldXDoubleSpinBox.value(),
            self.magneticFieldYDoubleSpinBox.value(),
            self.magneticFieldZDoubleSpinBox.value(),
            )

        self.nPsis = int(self.nPsisDoubleSpinBox.value())

        if 'RIXS' in self.experiment:
            self.energies = ((self.energiesTabWidget.tabText(0),
                              self.e1MinDoubleSpinBox.value(),
                              self.e1MaxDoubleSpinBox.value(),
                              int(self.e1NPointsDoubleSpinBox.value()),
                              self.e1LorentzianBroadeningDoubleSpinBox.value(),
                              self.e1GaussianBroadeningDoubleSpinBox.value()),
                             (self.energiesTabWidget.tabText(1),
                              self.e2MinDoubleSpinBox.value(),
                              self.e2MaxDoubleSpinBox.value(),
                              int(self.e2NPointsDoubleSpinBox.value()),
                              self.e2LorentzianBroadeningDoubleSpinBox.value(),
                              self.e2GaussianBroadeningDoubleSpinBox.value()))
        else:
            self.energies = ((self.energiesTabWidget.tabText(0),
                              self.e1MinDoubleSpinBox.value(),
                              self.e1MaxDoubleSpinBox.value(),
                              int(self.e1NPointsDoubleSpinBox.value()),
                              self.e1LorentzianBroadeningDoubleSpinBox.value(),
                              self.e1GaussianBroadeningDoubleSpinBox.value()),)

        self.hamiltonianParameters = self.hamiltonianModel.getModelData()
        self.hamiltonianTermsCheckState = (
            self.hamiltonianModel.getNodesCheckState())

    def saveParameters(self):
        for key in self._defaults:
            try:
                self.calculation[key] = copy.deepcopy(self.__dict__[key])
            except KeyError:
                self.calculation[key] = None

    def loadParameters(self, dictionary):
        for key in self._defaults:
            try:
                self.__dict__[key] = copy.deepcopy(dictionary[key])
            except KeyError:
                self.__dict__[key] = None

    def createContextMenu(self, position):
        icon = QIcon(resourceFileName(os.path.join(
            'gui', 'icons', 'save.svg')))
        self.saveSelectedCalculationsAsAction = QAction(
            icon, 'Save Selected Calculations As...', self,
            triggered=self.saveSelectedCalculationsAs)

        icon = QIcon(resourceFileName(os.path.join(
            'gui', 'icons', 'trash.svg')))
        self.removeCalculationsAction = QAction(
            icon, 'Remove Selected Calculations', self,
            triggered=self.removeSelectedCalculations)
        self.removeAllCalculationsAction = QAction(
            icon, 'Remove All Calculations', self,
            triggered=self.removeAllCalculations)

        icon = QIcon(resourceFileName(os.path.join(
            'gui', 'icons', 'folder-open.svg')))
        self.loadCalculationsAction = QAction(
            icon, 'Load Calculations', self,
            triggered=self.loadCalculations)

        selection = self.resultsView.selectionModel().selection()
        selectedItemsRegion = self.resultsView.visualRegionForSelection(
            selection)
        cursorPosition = self.resultsView.mapFromGlobal(QCursor.pos())

        if selectedItemsRegion.contains(cursorPosition):
            contextMenu = QMenu('Items Context Menu', self)
            contextMenu.addAction(self.saveSelectedCalculationsAsAction)
            contextMenu.addAction(self.removeCalculationsAction)
            contextMenu.exec_(self.resultsView.mapToGlobal(position))
        else:
            contextMenu = QMenu('View Context Menu', self)
            contextMenu.addAction(self.loadCalculationsAction)
            contextMenu.addAction(self.removeAllCalculationsAction)
            contextMenu.exec_(self.resultsView.mapToGlobal(position))

    def saveSelectedCalculationsAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Calculations', 'untitled', 'Pickle File (*.pkl)')

        if path:
            os.chdir(os.path.dirname(path))
            calculations = list(self.selectedCalculations())
            calculations.reverse()
            with open(path, 'wb') as p:
                pickle.dump(calculations, p)

    def removeSelectedCalculations(self):
        indexes = self.resultsView.selectedIndexes()
        self.resultsModel.removeItems(indexes)

    def removeAllCalculations(self):
        self.resultsModel.reset()

    def loadCalculations(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Load Calculations', '', 'Pickle File (*.pkl)')

        if path:
            with open(path, 'rb') as p:
                self.resultsModel.appendItems(pickle.load(p))

        self.resultsView.selectionModel().setCurrentIndex(
            self.resultsModel.index(0, 0), QItemSelectionModel.Select)

    def saveInput(self):
        # Load the template file specific to the requested calculation.
        path = resourceFileName(
            os.path.join('modules', 'quanty', 'templates',
                         '{}'.format(self.templateName)))

        try:
            with open(path) as p:
                template = p.read()
        except IOError as e:
            self.parent().statusBar().showMessage(
                'Could not find template file: {}.' .format(self.templateName))
            raise e

        self.getParameters()

        replacements = collections.OrderedDict()

        for shell in self.shells:
            replacements['$NElectrons_{}'.format(shell[0])] = shell[1]

        replacements['$T'] = self.temperature

        # If all components of the magnetic field are zero, 
        # add a small contribution in the y-direction to make the simulation
        # converge faster.
        if all(value == 0.0 for value in self.magneticField):
            self.magneticField = (0.0, 0.00001, 0.0)

        replacements['$Bx'] = self.magneticField[0]
        replacements['$By'] = self.magneticField[1]
        replacements['$Bz'] = self.magneticField[2]

        replacements['$Emin1'] = self.energies[0][1]
        replacements['$Emax1'] = self.energies[0][2]
        replacements['$NE1'] = self.energies[0][3]
        # Broadening is done in the interface.
        value = self.e1LorentzianBroadeningDoubleSpinBox.minimum()
        replacements['$Gamma1'] = value

        if 'RIXS' in self.experiment:
            replacements['$Emin2'] = self.energies[1][1]
            replacements['$Emax2'] = self.energies[1][2]
            replacements['$NE2'] = self.energies[1][3]
            replacements['$Gamma1'] = self.energies[0][4]
            replacements['$Gamma2'] = self.energies[1][4]

        replacements['$NPsis'] = self.nPsis

        for term in self.hamiltonianParameters:
            if 'Coulomb' in term:
                name = 'H_coulomb'
            elif 'Spin-Orbit Coupling' in term:
                name = 'H_soc'
            elif 'Crystal Field' in term:
                name = 'H_cf'
            elif '3d-Ligands Hybridization' in term:
                name = 'H_3d_Ld_hybridization'
            elif '3d-4p Hybridization' in term:
                name = 'H_3d_4p_hybridization'

            configurations = self.hamiltonianParameters[term]
            for configuration, parameters in configurations.items():
                if 'Initial' in configuration:
                    suffix = 'i'
                elif 'Intermediate' in configuration:
                    suffix = 'm'
                elif 'Final' in configuration:
                    suffix = 'f'
                for parameter, (value, scaling) in parameters.items():
                    key = '${}_{}_value'.format(parameter, suffix)
                    replacements[key] = '{}'.format(value)
                    key = '${}_{}_scaling'.format(parameter, suffix)
                    replacements[key] = '{}'.format(scaling)

            checkState = self.hamiltonianTermsCheckState[term]
            if checkState > 0:
                checkState = 1

            replacements['${}'.format(name)] = checkState

        replacements['$baseName'] = self.baseName

        for replacement in replacements:
            template = template.replace(
                replacement, str(replacements[replacement]))

        with open(self.baseName + '.lua', 'w') as f:
            f.write(template)

    def saveInputAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Quanty Input', '{}'.format(self.baseName + '.lua'),
            'Quanty Input File (*.lua)')

        if path:
            self.baseName, _ = os.path.splitext(os.path.basename(path))
            self.updateMainWindowTitle()
            os.chdir(os.path.dirname(path))
            try:
                self.saveInput()
            except IOError:
                return

    def runCalculation(self):
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
        try:
            self.saveInput()
        except FileNotFoundError:
            return

        # You are about to run; I will give you a label, a unique identifier,
        # and a starting time.
        self.label = '{} | {} | {} | {} | {}'.format(
            self.element, self.charge, self.symmetry,
            self.experiment, self.edge)
        self.uuid = uuid.uuid4().hex
        self.startingTime = datetime.datetime.now()

        self.calculation = collections.OrderedDict()
        self.saveParameters()

        # Run Quanty using QProcess.
        self.process = QProcess()

        self.process.start(self.command, (self.baseName + '.lua', ))
        self.parent().statusBar().showMessage(
            'Running {} {} in {}.'.format(
                self.command, self.baseName + '.lua', os.getcwd()))

        self.process.readyReadStandardOutput.connect(self.handleOutputLogging)
        self.process.started.connect(self.updateCalculationPushButton)
        self.process.finished.connect(self.processCalculation)

    def updateCalculationPushButton(self):
        icon = QIcon(resourceFileName(os.path.join(
            'gui', 'icons', 'stop.svg')))
        self.calculationPushButton.setIcon(icon)

        self.calculationPushButton.setText('Stop')
        self.calculationPushButton.setToolTip('Stop Quanty')

        self.calculationPushButton.disconnect()
        self.calculationPushButton.clicked.connect(self.stopCalculation)

    def resetCalculationPushButton(self):
        icon = QIcon(resourceFileName(os.path.join(
            'gui', 'icons', 'play.svg')))
        self.calculationPushButton.setIcon(icon)

        self.calculationPushButton.setText('Run')
        self.calculationPushButton.setToolTip('Run Quanty')

        self.calculationPushButton.disconnect()
        self.calculationPushButton.clicked.connect(self.runCalculation)

    def stopCalculation(self):
        self.process.kill()

    def processCalculation(self):
        # When did I finish?
        self.endingTime = datetime.datetime.now()

        # Reset the calculation button.
        self.resetCalculationPushButton()

        # Evaluate the exit code and status of the process.
        exitStatus = self.process.exitStatus()
        exitCode = self.process.exitCode()
        timeout = 10000
        statusBar = self.parent().statusBar()
        if exitStatus == 0 and exitCode == 0:
            message = ('Quanty has finished successfully in ')
            delta = int((self.endingTime - self.startingTime).total_seconds())
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

        # Copy back the details of the calculation, and overwrite all UI
        # changes done by the user during the calculation.
        self.loadParameters(self.calculation)

        # Initialize the spectra container.
        self.spectra = dict()

        e1Min = self.energies[0][1]
        e1Max = self.energies[0][2]
        e1NPoints = self.energies[0][3]
        self.spectra['e1'] = np.linspace(e1Min, e1Max, e1NPoints + 1)

        if 'RIXS' in self.experiment:
            e2Min = self.energies[1][1]
            e2Max = self.energies[1][2]
            e2NPoints = self.energies[1][3]
            self.spectra['e2'] = np.linspace(e2Min, e2Max, e2NPoints + 1)

        # Find all spectra in the current folder.
        pattern = '{}*.spec'.format(self.baseName)

        for spectrumName in glob.glob(pattern):
            try:
                spectrum = np.loadtxt(spectrumName, skiprows=5)
            except FileNotFoundError:
                return

            if '_iso.spec' in spectrumName:
                key = 'Isotropic'
            elif '_cd.spec' in spectrumName:
                key = 'Circular Dichroism'

            self.spectra[key] = -spectrum[:, 2::2]

            # Remove the spectrum file
            os.remove(spectrumName)

        self.updateSpectraComboBox()

        # Store the calculation details; have to encapsulate it into a list.
        self.saveParameters()
        self.resultsModel.appendItems([self.calculation])

        # Update the selected item in the results view.
        self.resultsView.selectionModel().clearSelection()
        index = self.resultsModel.index(self.resultsModel.rowCount() - 1)
        self.resultsView.selectionModel().select(
            index, QItemSelectionModel.Select)

        # TODO: Move this action in a better place.
        self.parent().plotWidget.spectraComboBox.currentTextChanged.connect(
            self.plot)

        self.plot()

    def updateSpectraComboBox(self):
        self.parent().plotWidget.spectraComboBox.clear()

        keys = ('Isotropic', 'Circular Dichroism')
        for key in keys:
            if key in self.spectra:
                self.parent().plotWidget.spectraComboBox.addItem(key)

        self.parent().plotWidget.spectraComboBox.setCurrentIndex(0)

    def plot(self):
        if not self.spectra:
            return

        plotWidget = self.parent().plotWidget

        if 'RIXS' in self.experiment:
            plotWidget.setGraphXLabel('Incident Energy (eV)')
            plotWidget.setGraphYLabel('Energy Transfer (eV)')

            colormap = {'name': 'viridis', 'normalization': 'linear',
                                'autoscale': True, 'vmin': 0.0, 'vmax': 1.0}
            plotWidget.setDefaultColormap(colormap)

            legend = self.label + self.uuid

            x = self.spectra['e1']
            xMin = x.min()
            xMax = x.max()
            xNPoints = x.size
            xScale = (xMax - xMin) / xNPoints

            y = self.spectra['e2']
            yMin = y.min()
            yMax = y.max()
            yNPoints = y.size
            yScale = (yMax - yMin) / yNPoints

            currentPlot = plotWidget.spectraComboBox.currentText()
            try:
                z = self.spectra[currentPlot]
            except KeyError:
                return

            plotWidget.addImage(
                z, origin=(xMin, yMin), scale=(xScale, yScale))
        else:
            plotWidget.setGraphXLabel('Absorption Energy (eV)')
            plotWidget.setGraphYLabel('Absorption Cross Section (a.u.)')

            legend = self.label + self.uuid

            x = self.spectra['e1']

            currentPlot = plotWidget.spectraComboBox.currentText()
            try:
                y = self.spectra[currentPlot]
            except KeyError:
                return

            y = y[:, 0]

            fwhm = self.e1GaussianBroadeningDoubleSpinBox.value()
            if fwhm:
                y = self.broaden(x, y, type='gaussian', fwhm=fwhm) * y.max()

            fwhm = (self.e1LorentzianBroadeningDoubleSpinBox.value() -
                    self.e1LorentzianBroadeningDoubleSpinBox.minimum())
            if fwhm:
                y = self.broaden(x, y, type='lorentzian', fwhm=fwhm) * y.max()

            plotWidget.addCurve(x, y, legend)

    def replot(self):
        # Whenever the broading changes, the data related to that plot 
        # has to change.

        # index = self.resultsView.selectedIndexes()[0]

        # self.getParameters()
        # self.saveParameters()
        # index = self.resultsModel.replaceItem(index, self.calculation)

        # self.resultsView.selectionModel().select(
        #     index, QItemSelectionModel.Select)

        self.plot()

    @staticmethod
    def broaden(x, y, type='gaussian', fwhm=None):
        yb = np.zeros_like(y)
        if type == 'gaussian':
            sigma = fwhm / 2.0 * np.sqrt(2.0 * np.log(2.0))
            for xi, yi in zip(x, y):
                yb += yi / (sigma * np.sqrt(2.0 * np. pi)) * np.exp(
                        -1.0 / 2.0 * ((x - xi) / sigma)**2)
        elif type == 'lorentzian':
            gamma = fwhm
            for xi, yi in zip(x, y):
                yb += yi / np.pi * (0.5 * gamma) / (
                    (x - xi)**2 + (0.5 * gamma)**2)
        yb = yb / yb.max()
        return yb

    def selectedHamiltonianTermChanged(self):
        index = self.hamiltonianTermsView.currentIndex()
        self.hamiltonianParametersView.setRootIndex(index)

    def selectedCalculations(self):
        indexes = self.resultsView.selectedIndexes()
        for index in indexes:
            yield self.resultsModel.getIndexData(index)

    def selectedCalculationsChanged(self):
        self.parent().plotWidget.clear()
        for index in self.selectedCalculations():
            self.loadParameters(index)
            self.updateSpectraComboBox()
        self.setUi()
        self.updateMainWindowTitle()

    def handleOutputLogging(self):
        self.process.setReadChannel(QProcess.StandardOutput)
        data = self.process.readAllStandardOutput().data()
        self.parent().loggerWidget.appendPlainText(data.decode('utf-8'))

    def handleErrorLogging(self):
        self.process.setReadChannel(QProcess.StandardError)
        data = self.process.readAllStandardError().data()
        self.parent().loggerWidget.appendPlainText(data.decode('utf-8'))

    def updateMainWindowTitle(self):
        title = 'Crispy - {}'.format(self.baseName + '.lua')
        self.parent().setWindowTitle(title)