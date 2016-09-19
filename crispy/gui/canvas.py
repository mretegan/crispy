# coding: utf-8

import collections
import json
import numpy as np
import os
import shutil
import subprocess

from PyQt5.QtCore import QItemSelectionModel, QEvent, Qt
from PyQt5.QtWidgets import QAbstractItemView, QMainWindow, QFileDialog
from PyQt5 import uic

from .models.treemodel import TreeModel
from .models.listmodel import ListModel
from ..resources import resource_filename


class MainWindow(QMainWindow):

    _defaults = {'command': None,
                 'inputPath': None,
                 'outputPath': None,
                 'baseName': 'untitled',
                 'element': 'Ni',
                 'charge': '2+',
                 'symmetry': 'Oh',
                 'theoreticalModel': 'Crystal field (CF)',
                 'experiment': 'XAS',
                 'edge': 'L2,3 (2p)',
                 }

    def __init__(self):
        super(MainWindow, self).__init__()
        self.__dict__.update(self._defaults)
        uiPath = resource_filename('gui/main.ui')
        uic.loadUi(uiPath, baseinstance=self, package='crispy.gui')

        self.loadUiParameters()
        self.populateUi()
        self.activateUi()

        self.updateEnergyAxes()

        self.loadHamiltonianParameters()
        self.updateHamiltonian()

        self.statusBar().showMessage('Ready')

    def loadHamiltonianParameters(self):
        path = resource_filename(
            'modules/quanty/parameters/hamiltonian.json')
        with open(path) as f:
            self.hamiltonianParameters = json.loads(
                f.read(), object_pairs_hook=collections.OrderedDict)

    def loadUiParameters(self):
        # Load the parameters used to populate some of the UI elements.
        path = resource_filename(
            'modules/quanty/parameters/ui.json')
        with open(path) as f:
            self.uiParameters = json.loads(
                f.read(), object_pairs_hook=collections.OrderedDict)

    def populateUi(self):
        self.elementComboBox.addItems(self.uiParameters)
        self.elementComboBox.setCurrentText(self.element)

        self.chargeComboBox.addItems(self.uiParameters[self.element])
        self.chargeComboBox.setCurrentText(self.charge)

        self.symmetryComboBox.addItems(
            self.uiParameters[self.element][self.charge])
        self.symmetryComboBox.setCurrentText(self.symmetry)

        self.theoreticalModelComboBox.addItems(
            self.uiParameters[self.element][self.charge][self.symmetry])
        self.theoreticalModelComboBox.setCurrentText(self.theoreticalModel)

        self.experimentComboBox.addItems(
            self.uiParameters[self.element][self.charge][self.symmetry]
            [self.theoreticalModel])
        self.experimentComboBox.setCurrentText(self.experiment)

        self.edgeComboBox.addItems(
            self.uiParameters[self.element][self.charge][self.symmetry]
            [self.theoreticalModel][self.experiment])
        self.edgeComboBox.setCurrentText(self.edge)

        self.resultsModel = ListModel(list())
        self.resultsView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.resultsView.setModel(self.resultsModel)
        self.resultsView.selectionModel().selectionChanged.connect(
            self.selectedResultsChanged)
        self.resultsView.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.resultsView.viewport().installEventFilter(self)

    def activateUi(self):
        # Activate the combo boxes.
        self.elementComboBox.currentTextChanged.connect(self.updateUi)
        self.chargeComboBox.currentTextChanged.connect(self.updateUi)
        self.symmetryComboBox.currentTextChanged.connect(self.updateUi)

        self.theoreticalModelComboBox.currentTextChanged.connect(self.updateUi)

        self.experimentComboBox.currentTextChanged.connect(self.updateUi)
        self.edgeComboBox.currentTextChanged.connect(self.updateUi)

        # Activate the buttons.
        self.savePushButton.clicked.connect(self.saveInput)
        self.runPushButton.clicked.connect(self.runCalculation)

        # Activate the menubar.
        self.quantyRunCalculation.triggered.connect(self.runCalculation)
        self.quantySaveInput.triggered.connect(self.saveInput)
        self.quantySaveAsInput.triggered.connect(self.saveAsInput)
        self.quantyModuleShow.triggered.connect(self.moduleShow)
        self.quantyModuleHide.triggered.connect(self.moduleHide)

    def updateUi(self):
        self.element = self.elementComboBox.currentText()

        self.chargeComboBox.updateItems(self.uiParameters[self.element])
        self.charge = self.chargeComboBox.currentText()

        self.symmetryComboBox.updateItems(
            self.uiParameters[self.element][self.charge])
        self.symmetry = self.symmetryComboBox.currentText()

        self.theoreticalModelComboBox.updateItems(
            self.uiParameters[self.element][self.charge][self.symmetry])
        self.theoreticalModel = self.theoreticalModelComboBox.currentText()

        self.experimentComboBox.updateItems(
            self.uiParameters[self.element][self.charge][self.symmetry]
            [self.theoreticalModel])
        self.experiment = self.experimentComboBox.currentText()

        self.edgeComboBox.updateItems(
            self.uiParameters[self.element][self.charge][self.symmetry]
            [self.theoreticalModel][self.experiment])
        self.edge = self.edgeComboBox.currentText()

        self.updateEnergyAxes()
        self.updateHamiltonian()

    def updateEnergyAxes(self):
        self.e2GroupBox.setHidden(True)

        axes = (self.uiParameters[self.element][self.charge]
                [self.symmetry][self.theoreticalModel]
                [self.experiment][self.edge]['axes'])

        self.e1GroupBox.setTitle(axes['e1']['label'])
        self.e1MinDoubleSpinBox.setValue(axes['e1']['min'])
        self.e1MaxDoubleSpinBox.setValue(axes['e1']['max'])
        self.e1NPointsDoubleSpinBox.setValue(axes['e1']['npoints'])
        self.e1GammaDoubleSpinBox.setValue(axes['e1']['gamma'])

        if self.experiment == 'RIXS':
            self.e2GroupBox.setHidden(False)

            self.e2GroupBox.setTitle(axes['e2']['label'])
            self.e2MinDoubleSpinBox.setValue(axes['e2']['min'])
            self.e2MaxDoubleSpinBox.setValue(axes['e2']['max'])
            self.e2NPointsDoubleSpinBox.setValue(axes['e2']['npoints'])
            self.e2GammaDoubleSpinBox.setValue(axes['e2']['gamma'])

    def updateHamiltonian(self):
        data = self.hamiltonianParameters[self.element][self.charge]

        configurations = (self.uiParameters[self.element][self.charge]
                          [self.symmetry][self.theoreticalModel]
                          [self.experiment][self.edge]['configurations'])

        hamiltonian = collections.OrderedDict()

        for hamiltonianTerm in data:
            if 'field' not in hamiltonianTerm:
                parameters = data[hamiltonianTerm]
            else:
                hamiltonianTerm = self.theoreticalModel
                parameters = data[hamiltonianTerm][self.symmetry]

            hamiltonian[hamiltonianTerm] = collections.OrderedDict()

            for configuration in configurations:
                label = '{0} CFG ({1})'.format(
                    configuration, configurations[configuration])

                hamiltonian[hamiltonianTerm][label] = (
                    parameters[configurations[configuration]])

        # Create the Hamiltonian model.
        self.hamiltonianModel = TreeModel(
            header=['parameter', 'value', 'scaling', 'min', 'max'],
            data=hamiltonian)

        # Assign the Hamiltonian model to the Hamiltonian view.
        self.hamiltonianTermsView.setModel(self.hamiltonianModel)
        self.hamiltonianTermsView.selectionModel().setCurrentIndex(
            self.hamiltonianModel.index(0, 0), QItemSelectionModel.Select)
        index = self.hamiltonianTermsView.selectionModel().currentIndex()
        self.hamiltonianTermsView.selectionModel().selectionChanged.connect(
            self.selectedHamiltonianTermChanged)
        self.hamiltonianTermsView.setAttribute(
            Qt.WA_MacShowFocusRect, False)

        # Assign the Hamiltonian model to the Hamiltonian parameters view, and
        # set some properties.
        self.hamiltonianParametersView.setModel(self.hamiltonianModel)
        self.hamiltonianParametersView.expandAll()
        self.hamiltonianParametersView.resizeAllColumnsToContents()
        self.hamiltonianParametersView.setColumnWidth(0, 160)
        self.hamiltonianParametersView.setRootIndex(index)
        self.hamiltonianParametersView.setAttribute(
            Qt.WA_MacShowFocusRect, False)
        self.hamiltonianParametersView.viewport().installEventFilter(self)

    def selectedHamiltonianTermChanged(self):
        index = self.hamiltonianTermsView.selectionModel().currentIndex()
        self.hamiltonianParametersView.setRootIndex(index)

    def selectedResultsChanged(self):
        self.plotWidget.clear()
        selectedIndexes = self.resultsView.selectionModel().selectedIndexes()
        for index in selectedIndexes:
            label, data = self.resultsModel.getIndexData(index)
            self.plot(data, label)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.MouseButtonPress and
            event.button() == Qt.RightButton and
            (source is self.hamiltonianParametersView.viewport() or
                source is self.resultsView.viewport())):
            return True
        else:
            return super(MainWindow, self).eventFilter(source, event)

    def saveInput(self):
        # Load the template file specific to the requested calculation.
        templateFileName = (self.uiParameters[self.element][self.charge]
                            [self.symmetry][self.theoreticalModel]
                            [self.experiment][self.edge]['template'])

        templateFile = resource_filename(
            os.path.join('modules', 'quanty', 'templates',
                         '{0:s}'.format(templateFileName)))

        try:
            with open(templateFile) as f:
                template = f.read()
        except FileNotFoundError:
            print('Could not find template: {0:s}'.format(templateFileName))
            return

        shells = (self.uiParameters[self.element][self.charge]
                  [self.symmetry][self.theoreticalModel][self.experiment]
                  [self.edge]['shells'])

        for shell in shells:
            template = template.replace(
                '$NElectrons_{0:s}'.format(shell), str(shells[shell]))

        template = template.replace(
            '$T', '{0:8.3f}'.format(
                self.temperatureDoubleSpinBox.value()))

        template = template.replace('$Bx', '0')
        template = template.replace('$By', '0')
        template = template.replace('$Bz', '1e-6')

        # Absorption or incident energy group box
        template = template.replace(
            '$Emin1', '{0:8.1f}'.format(
                self.e1MinDoubleSpinBox.value()))

        template = template.replace(
            '$Emax1', '{0:8.1f}'.format(
                self.e1MaxDoubleSpinBox.value()))

        template = template.replace(
            '$NE1', '{0:8.0f}'.format(
                self.e1NPointsDoubleSpinBox.value()))

        template = template.replace(
            '$Gamma1', '{0:8.2f}'.format(
                self.e1GammaDoubleSpinBox.value()))

        # Energy transfer group box
        template = template.replace(
            '$Emin2', '{0:8.1f}'.format(
                self.e2MinDoubleSpinBox.value()))

        template = template.replace(
            '$Emax2', '{0:8.1f}'.format(
                self.e2MaxDoubleSpinBox.value()))

        template = template.replace(
            '$NE2', '{0:8.0f}'.format(
                self.e2NPointsDoubleSpinBox.value()))

        template = template.replace(
            '$Gamma2', '{0:8.2f}'.format(
                self.e2GammaDoubleSpinBox.value()))

        # Get the most recent Hamiltonian data from the model.
        hamiltonian = self.hamiltonianModel.getModelData()

        for hamiltonianTerm in hamiltonian:
            configurations = hamiltonian[hamiltonianTerm]
            for configuration in configurations:
                if 'Starting' in configuration:
                    suffix = 'sc'
                elif 'Intermediate' in configuration:
                    suffix = 'ic'
                elif 'Final' in configuration:
                    suffix = 'fc'
                else:
                    suffix = str()
                parameters = configurations[configuration]
                for parameter, value in parameters.items():
                    if isinstance(value, list):
                        value = float(value[0]) * float(value[1])
                    else:
                        value = float(value)
                    template = template.replace(
                        '${0:s}_{1:s}'.format(parameter, suffix),
                        '{0:8.4f}'.format(value))

        for hamiltonianTerm, hamiltonianTermState in (
                self.hamiltonianModel.getNodesState().items()):
            if 'Coulomb' in hamiltonianTerm:
                termName = 'H_coulomb'
            elif 'Spin-orbit coupling' in hamiltonianTerm:
                termName = 'H_soc'
            elif 'Crystal field' in hamiltonianTerm:
                termName = 'H_cf'
            elif 'Ligand field' in hamiltonianTerm:
                termName = 'H_lf'

            # Check the state of the Hamiltonian term.
            if hamiltonianTermState == 0:
                termState = 0
            else:
                termState = 1

            template = template.replace(
                '${0:s}_flag'.format(termName), '{0:d}'.format(termState))

        template = template.replace('$baseName', self.baseName)

        self.inputPath = '{0:s}.lua'.format(self.baseName)

        with open(self.inputPath, 'w') as f:
            f.write(template)

    def runCalculation(self):
        # Determine the location of the executable program.
        self.command = shutil.which('Quanty') or shutil.which('Quanty.exe')

        if self.command is None:
            print('Could not find Quanty in the path.')
            return

        # Write the input file to disk.
        if self.inputPath:
            self.saveInput()
        else:
            self.saveAsInput()

        if not self.inputPath:
            return

        # Determine the name of the output path.
        self.outputPath = '{0:s}.out'.format(self.baseName)

        with open(self.outputPath, 'w') as f:
            try:
                subprocess.check_call(
                    [self.command, self.inputPath], stdout=f, stderr=f)
            except subprocess.CalledProcessError:
                print('Quanty has not terminated gracefully.')
                return

        # Load the data to be plotted.
        data = np.loadtxt('{0:s}.spec'.format(self.baseName), skiprows=5)

        id = self.resultsModel.size() + 1
        label = '#{:d} - {:s}{:s} | {:s} | {:s} | {:s}'.format(
            id, self.element, self.charge, self.symmetry, self.experiment,
            self.edge)

        # Store the simulation details.
        self.resultsModel.appendItem((label, data))

        # Update the selected item in the results view.
        self.resultsView.selectionModel().clearSelection()
        index = self.resultsModel.index(self.resultsModel.rowCount() - 1)
        self.resultsView.selectionModel().select(
            index, QItemSelectionModel.Select)

    def plot(self, data, label):
        if data.shape[1] < 4:
            x = data[:, 0]
            y = -data[:, 2]
            self.plotWidget.addCurve(x, y, legend=label)
            self.plotWidget.setGraphXLabel('Absorption Energy (eV)')
            self.plotWidget.setGraphYLabel('Absorption cross section (a.u.)')
        else:
            xMin = self.e1MinDoubleSpinBox.value()
            xMax = self.e1MaxDoubleSpinBox.value()
            xPoints = self.e1NPointsDoubleSpinBox.value()
            xScale = (xMax - xMin) / xPoints

            yMin = self.e2MinDoubleSpinBox.value()
            yMax = self.e2MaxDoubleSpinBox.value()
            yPoints = self.e2NPointsDoubleSpinBox.value()
            yScale = (yMax - yMin) / yPoints

            self.plotWidget.setGraphXLabel('Incident Energy (eV)')
            self.plotWidget.setGraphYLabel('Energy Transfer (eV)')
            colormap = {'name': 'viridis', 'normalization': 'linear',
                                'autoscale': True, 'vmin': 0.0, 'vmax': 1.0}
            self.plotWidget.setDefaultColormap(colormap)

            data = -data[:, 2::2]
            self.plotWidget.addImage(
                data, origin=(xMin, yMin), scale=(xScale, yScale))

    def saveAsInput(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Quanty Input', '{0:s}.lua'.format(self.baseName),
            'Quanty Input File (*.lua)')

        if path:
            os.chdir(os.path.dirname(path))
            self.baseName = os.path.splitext(os.path.basename(path))[0]
            self.saveInput()

    def moduleShow(self):
        self.quantyDockWidget.setVisible(True)
        self.menuModulesQuanty.insertAction(
            self.quantyModuleShow, self.quantyModuleHide)
        self.menuModulesQuanty.removeAction(self.quantyModuleShow)

    def moduleHide(self):
        self.quantyDockWidget.setVisible(False)
        self.menuModulesQuanty.insertAction(
            self.quantyModuleHide, self.quantyModuleShow)
        self.menuModulesQuanty.removeAction(self.quantyModuleHide)


def main():
    import sys

    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('Crispy')
    window.show()

    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
