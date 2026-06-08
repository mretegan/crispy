"""Quanty dock widget components."""

import contextlib
import logging
import os
from itertools import pairwise

import qtawesome as qta
from silx.gui.qt import (
    QAction,
    QDockWidget,
    QFileDialog,
    QItemSelectionModel,
    QMenu,
    QModelIndex,
    QPoint,
    Qt,
    QWidget,
    pyqtSignal,
)

from crispy import resourceAbsolutePath
from crispy.config import Config
from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation
from crispy.quanty.details import DetailsDialog
from crispy.quanty.external import ExternalData
from crispy.quanty.preferences import PreferencesDialog
from crispy.quanty.progress import ProgressDialog
from crispy.uic import loadUi
from crispy.utils import findQtObject
from crispy.views import setMappings

logger = logging.getLogger(__name__)


class AxisWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        uiPath = os.path.join("quanty", "uis", "axis.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.lorentzianToolButton.setIcon(qta.icon("fa6s.gear"))

        self.mappers = []

        # The "Analyze polarization" checkbox is bound once and reads the photon
        # set by the most recent populate() call.
        self._analyzePhoton = None
        self.analyzeCheckBox.toggled.connect(self._onAnalyzeToggled)

    def _onAnalyzeToggled(self, checked):
        photon = self._analyzePhoton
        if photon is not None and hasattr(photon, "analyze"):
            photon.analyze.value = checked

    def setAnalyzeEnabled(self, enabled):
        self.analyzeCheckBox.setEnabled(enabled)

    def populate(self, axis):
        if self.mappers:
            for mapper in self.mappers:
                mapper.clearMapping()
        MAPPINGS = (
            (self.startLineEdit, axis.start),
            (self.stopLineEdit, axis.stop),
            (self.nPointsLineEdit, axis.npoints),
            (self.gaussianLineEdit, axis.gaussian),
            (self.lorentzianLineEdit, axis.lorentzian),
            (self.kLineEdit, axis.photon.k),
            (self.e1LineEdit, axis.photon.e1),
        )
        self.mappers = setMappings(MAPPINGS)
        self.lorentzianToolButton.setVisible(False)

        # The "Analyze polarization" checkbox only applies to the scattered
        # photon (it controls whether the outgoing polarization is resolved or
        # averaged over). A BoolItem is not editable through the data-widget
        # mapper, so the checkbox is driven by _onAnalyzeToggled instead.
        photon = axis.photon
        self._analyzePhoton = photon
        hasAnalyze = hasattr(photon, "analyze")
        self.analyzeCheckBox.setVisible(hasAnalyze)
        if hasAnalyze:
            self.analyzeCheckBox.blockSignals(True)
            self.analyzeCheckBox.setChecked(bool(photon.analyze.value))
            self.analyzeCheckBox.blockSignals(False)


class GeneralSetupPage(QWidget):
    comboBoxChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        uiPath = os.path.join("quanty", "uis", "general.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.xAxis = AxisWidget()
        self.yAxis = AxisWidget()
        self.axesTabWidget.addTab(self.xAxis, None)

        self.mappers = []

        # The model is shared across calculations; track it so the outgoing
        # polarization checkbox is kept in sync with the spectra selection
        # without stacking connections.
        self._model = None
        self._state = None

        self.symbolComboBox.currentTextChanged.connect(self.comboBoxChanged)
        self.chargeComboBox.currentTextChanged.connect(self.comboBoxChanged)
        self.symmetryComboBox.currentTextChanged.connect(self.comboBoxChanged)
        self.experimentComboBox.currentTextChanged.connect(self.comboBoxChanged)
        self.edgeComboBox.currentTextChanged.connect(self.comboBoxChanged)

    def update(self):
        pass

    def populate(self, state):
        logger.debug("Start populating the general setup page.")
        model = state.model()
        self._state = state

        logger.debug("Start populating the symbol combo box.")
        self.symbolComboBox.setItems(state.symbols, state.element.symbol)
        self.chargeComboBox.setItems(state.charges, state.element.charge)
        self.symmetryComboBox.setItems(state.symmetries, state.symmetry.value)
        self.experimentComboBox.setItems(state.experiments, state.experiment.value)
        self.edgeComboBox.setItems(state.edges, state.edge.value)

        if self.mappers:
            for mapper in self.mappers:
                mapper.clearMapping()

        MAPPINGS = (
            (self.temperatureLineEdit, state.temperature),
            (self.magneticFieldLineEdit, state.magneticField),
        )
        self.mappers = setMappings(MAPPINGS)

        self.xAxis.populate(state.axes.xaxis)
        self.axesTabWidget.setTabText(0, state.axes.xaxis.label)

        if state.experiment.isTwoDimensional:
            self.axesTabWidget.addTab(self.yAxis, None)
            self.axesTabWidget.setTabText(1, state.axes.yaxis.label)
            self.yAxis.populate(state.axes.yaxis)
            self.xAxis.e1Label.setText("ε (x, y, z)")
            self.xAxis.kLineEdit.setEnabled(True)
            self.xAxis.e1LineEdit.setEnabled(True)
            self.yAxis.kLabel.setText("k' (x, y, z)")
            self.yAxis.e1Label.setText("ε' (x, y, z)")
            self.yAxis.kLineEdit.setEnabled(True)
            self.yAxis.e1LineEdit.setEnabled(True)
        else:
            self.axesTabWidget.removeTab(1)
            self.xAxis.e1Label.setText("ε (x, y, z)")
            self.xAxis.kLineEdit.setEnabled(True)
            self.xAxis.e1LineEdit.setEnabled(True)

        self.spectraView.setModel(model)
        self.spectraView.setRootIndex(state.spectra.toCalculate.index())
        self.spectraView.hideColumn(1)
        self.spectraView.hideColumn(2)
        self.spectraView.setHeaderHidden(True)
        self.spectraView.expandAll()
        self.spectraView.setTabKeyNavigation(True)

        # Keep the outgoing-polarization checkbox in sync with the spectra
        # selection. The model is shared across calculations, so connect once.
        if self._model is not model:
            if self._model is not None:
                with contextlib.suppress(TypeError, RuntimeError):
                    self._model.dataChanged.disconnect(self._onSpectraChanged)
            self._model = model
            model.dataChanged.connect(self._onSpectraChanged)
        self._updateAnalyzeEnabled()

        self.updateTabOrder(twoDimensional=state.experiment.isTwoDimensional)
        logger.debug("Finished populating the general setup page.")

    def _onSpectraChanged(self, *args):
        self._updateAnalyzeEnabled()

    def _updateAnalyzeEnabled(self):
        """Enable the outgoing-polarization checkbox only when the isotropic RIXS
        spectrum is selected. Its geometry factor is the only place the setting
        takes effect."""
        if self._state is None:
            return
        selected = self._state.spectra.toCalculate.selected
        self.yAxis.setAnalyzeEnabled("Isotropic Resonant Inelastic" in selected)

    def updateTabOrder(self, twoDimensional=False):
        """Chain the focusable widgets in top-to-bottom visual order."""
        chain = [
            self.symbolComboBox,
            self.chargeComboBox,
            self.symmetryComboBox,
            self.experimentComboBox,
            self.edgeComboBox,
            self.temperatureLineEdit,
            self.magneticFieldLineEdit,
        ]
        axes = [self.xAxis, self.yAxis] if twoDimensional else [self.xAxis]
        for axis in axes:
            chain.append(axis.startLineEdit)
            chain.append(axis.stopLineEdit)
            chain.append(axis.nPointsLineEdit)
            chain.append(axis.lorentzianLineEdit)
            chain.append(axis.gaussianLineEdit)
            chain.append(axis.kLineEdit)
            chain.append(axis.e1LineEdit)
        chain.append(self.spectraView)

        # Link only widgets that can take focus, so a hidden or disabled field does
        # not sit between two real fields and break the chain on the native macOS
        # style.
        chain = [w for w in chain if w.isEnabled() and not w.isHidden()]
        for earlier, later in pairwise(chain):
            self.setTabOrder(earlier, later)


class HamiltonianSetupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        uiPath = os.path.join("quanty", "uis", "hamiltonian.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.mappers = []
        # This is needed for the updateAutoStates.
        self.hamiltonian = None

    def populate(self, state):
        logger.debug("Start populating the Hamiltonian Setup page.")
        hamiltonian = state.hamiltonian
        self.hamiltonian = hamiltonian
        model = state.model()

        if self.mappers:
            for mapper in self.mappers:
                mapper.clearMapping()
        MAPPINGS = (
            (self.fkLineEdit, hamiltonian.fk),
            (self.gkLineEdit, hamiltonian.gk),
            (self.zetaLineEdit, hamiltonian.zeta),
            (self.syncParametersCheckBox, hamiltonian.synchronizeParameters),
            (self.nStatesLineEdit, hamiltonian.numberOfStates),
            (self.nStatesAutoCheckBox, hamiltonian.numberOfStates.auto),
            (self.nConfigurationsLineEdit, hamiltonian.numberOfConfigurations),
        )
        self.mappers = setMappings(MAPPINGS)

        self.termsView.setModel(model)

        # Set the root index of the terms view.
        terms = hamiltonian.terms
        index = model.indexFromItem(terms)
        self.termsView.setRootIndex(index)

        # Select the first Hamiltonian term.
        index = model.indexFromItem(terms.children()[0])
        selectionModel = self.termsView.selectionModel()
        selectionModel.setCurrentIndex(index, QItemSelectionModel.Select)
        selectionModel.selectionChanged.disconnect()
        selectionModel.selectionChanged.connect(self.updateParametersView)

        self.parametersView.setModel(model)
        self.parametersView.expandAll()
        # self.parametersView.setColumnWidth(0, 130)
        currentIndex = self.termsView.currentIndex()
        self.parametersView.setRootIndex(currentIndex)

        value = hamiltonian.numberOfStates.auto.value
        self.nStatesLineEdit.setEnabled(not value)
        # Having this enabled will cause the nStatesAutoCheckBox to be checked, which
        # in turn will cause the numberOfStates to be reset to the maximum number.
        # self.nStatesAutoCheckBox.stateChanged.disconnect()
        self.nStatesAutoCheckBox.stateChanged.connect(self.updateAutoStates)
        logger.debug("Finished populating the Hamiltonian Setup page.")

    def updateParametersView(self):
        index = self.termsView.currentIndex()
        self.parametersView.setRootIndex(index)
        self.parametersView.expandAll()

    def updateAutoStates(self, value):
        # Reset the number of states to the maximum if the box is checked.
        if value == Qt.CheckState.Checked:
            self.hamiltonian.numberOfStates.reset()
        self.nStatesLineEdit.setEnabled(not value)


class ResultsPage(QWidget):
    currentIndexChanged = pyqtSignal(QModelIndex)

    # TODO: Implement saving an loading results.
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        uiPath = os.path.join("quanty", "uis", "results.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.detailsDialog = DetailsDialog(parent=self)

        # Add a context menu to the view.
        icon = qta.icon("fa6s.clipboard")
        self.showDetailsDialogAction = QAction(
            icon, "Show Details", self, triggered=self.showDetailsDialog
        )

        # icon = qta.icon("fa6s.floppy-disk")
        # self.saveSelectedResultsAsAction = QAction(
        #     icon, "Save Highlighted Results As...",
        #     self, triggered=self.saveHighlighted
        # )

        icon = qta.icon("fa6s.trash")
        self.removeSelectedResultsAction = QAction(
            icon, "Remove Highlighted Results", self, triggered=self.removeHighlighted
        )

        # icon = qta.icon("fa6s.folder-open")
        # self.loadResultsAction = QAction(
        #     icon, "Load Results", self, triggered=self.load
        # )

        self.contextMenu = QMenu("Results Context Menu", self)
        self.contextMenu.addAction(self.showDetailsDialogAction)
        # self.contextMenu.addSeparator()
        # self.contextMenu.addAction(self.saveSelectedResultsAsAction)
        self.contextMenu.addAction(self.removeSelectedResultsAction)
        # self.contextMenu.addSeparator()
        # self.contextMenu.addAction(self.loadResultsAction)

        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested[QPoint].connect(
            self.showResultsContextMenu
        )

        self.model = TreeModel(parent=self)
        self.view.setModel(self.model)
        selectionModel = self.view.selectionModel()
        selectionModel.selectionChanged.connect(self.selectionChanged)

        # TODO: How to distinguish between a dataChanged related to a change in
        # the name and a change in the checked state? Only the last one should
        # trigger the actions.
        self.model.dataChanged.connect(self.plot)
        self.currentIndexChanged.connect(
            lambda index: self.detailsDialog.populate(index.internalPointer())
        )

        self._currentIndex = QModelIndex()
        self.plotting = False

    @property
    def currentIndex(self):
        return self._currentIndex

    @currentIndex.setter
    def currentIndex(self, value):
        self._currentIndex = value
        self.currentIndexChanged.emit(value)

    def getHighlighted(self):
        indexes = self.view.selectedIndexes()
        items = [index.internalPointer() for index in indexes]
        return items

    def removeHighlighted(self):
        items = self.getHighlighted()

        for item in items:
            item.setParent(None)

        index = self.model.firstIndex()
        if index.isValid():
            # This changes the selection, and the self.currentIndex will be
            # updated.
            self.view.setCurrentIndex(index)
        else:
            self.currentIndex = QModelIndex()

        self.plot(self.currentIndex)

    def saveHighlighted(self):
        items = self.getHighlighted()
        if not items:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Highlighted Results As",
            filter="Python pickle files (*.pkl)",
        )

        if not path:
            return

    def load(self):
        pass

    def plot(self, *args):
        # Unchecking calculations below changes the model, which emits
        # dataChanged and re-enters this method. Guard against that recursion.
        if self.plotting:
            return

        index, *_ = args
        # Get the last item the user has changed (None for an invalid index).
        last = index.internalPointer() if index.isValid() else None

        children = self.model.rootItem().children()

        # Always reset the plot widget.
        plotWidget = findQtObject(name="plotWidget")
        plotWidget.reset()

        if not children:
            return

        self.plotting = True
        try:
            if isinstance(last, Calculation):
                for child in children:
                    if isinstance(child, ExternalData):
                        continue
                    if (last.experiment.isTwoDimensional and last != child) or (
                        not last.experiment.isTwoDimensional
                        and child.experiment.isTwoDimensional
                    ):
                        child.checkState = Qt.CheckState.Unchecked

            # Plot the calculations that are checked.
            for child in children:
                if not child.isEnabled():
                    continue
                if isinstance(child, Calculation):
                    child.spectra.plot(plotWidget)
                elif isinstance(child, ExternalData):
                    child.plot(plotWidget)

            # Reset the plot widget if nothing new was plotted.
            if plotWidget.isEmpty():
                plotWidget.reset()
        finally:
            self.plotting = False

    def selectionChanged(self):
        indexes = self.view.selectedIndexes()
        try:
            [index] = indexes
        except ValueError:
            return
        self.currentIndex = index

    def showResultsContextMenu(self, position):
        selected = bool(self.view.selectedIndexes())
        self.removeSelectedResultsAction.setEnabled(selected)
        # self.saveSelectedResultsAsAction.setEnabled(selected)

        # Enable the action only if there is a valid item under the cursor.
        # TODO: Probably also check if the item is of a valid class.
        # No need to set the current index to the index at position. This is
        # done already when the selection changes.
        index = self.view.indexAt(position)
        self.showDetailsDialogAction.setEnabled(index.internalPointer() is not None)
        self.contextMenu.exec(self.view.mapToGlobal(position))

    def showDetailsDialog(self):
        result = self.currentIndex.internalPointer()
        self.detailsDialog.populate(result)
        self.detailsDialog.show()
        self.detailsDialog.raise_()
        self.detailsDialog.activateWindow()


class DockWidget(QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        uiPath = os.path.join("quanty", "uis", "main.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.saveInputAsPushButton.setIcon(qta.icon("fa6s.floppy-disk"))
        self.calculationPushButton.setIcon(qta.icon("fa6s.play", color="#4caf50"))

        self.model = TreeModel()

        self.preferencesDialog = PreferencesDialog(self)
        self.preferencesDialog.settingsChanged.connect(self.populate)

        # Remove the placeholder page.
        self.toolBox.removeItem(0)

        self.generalPage = GeneralSetupPage()
        self.toolBox.addItem(self.generalPage, "General Setup")

        self.hamiltonianPage = HamiltonianSetupPage()
        self.toolBox.addItem(self.hamiltonianPage, "Hamiltonian Setup")

        self.resultsPage = ResultsPage()
        self.toolBox.addItem(self.resultsPage, "Results")

        # Setup the initial state and populate the widgets.
        self.state = Calculation(parent=self.model.rootItem())

        self.generalPage.comboBoxChanged.connect(self.populate)
        self.resultsPage.currentIndexChanged.connect(self.populate)

        self.saveInputAsPushButton.clicked.connect(self.saveInputAs)
        self.calculationPushButton.clicked.connect(self.run)

        # Set up the actions.
        self.preferencesAction = QAction(
            "Preferences...", self, triggered=self.preferencesDialog.show
        )
        self.preferencesAction.setMenuRole(QAction.NoRole)

        self.saveInputAction = QAction("Save Input", self, triggered=self.saveInput)
        self.saveInputAsAction = QAction(
            "Save Input As...", self, triggered=self.saveInputAs
        )
        self.showHideAction = QAction("Show/Hide Module", self, triggered=self.showHide)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        logger.debug("Start setting the state.")
        # Except for the case when the method is called from __init__,
        # self.state should be assigned to the results model, so disconnect
        # only the signals that are not relevant anymore.
        with contextlib.suppress(AttributeError):
            self.state.runner.outputUpdated.disconnect()
        self._state = value

        logger.debug("Start populating the widgets.")
        self.generalPage.populate(self.state)
        self.hamiltonianPage.populate(self.state)

        logger.debug("Start connecting the signals.")
        self.state.runner.outputUpdated.connect(self.updateLogger)
        self.state.runner.successful.connect(self.successful)
        self.state.titleChanged.connect(self.updateMainWindowTitle)

        logger.debug("Start updating the title.")
        self.updateMainWindowTitle()

    def populate(self, index=None):
        logger.debug("Start populating the widgets.")
        # Keep a reference to the current calculation before it is detached so
        # its parameters can be reused when only the symmetry changes.
        previous = self.state

        # Remove the previous state from the root item's children.
        rootItem = self.model.rootItem()
        for child in rootItem.children():
            child.setParent(None)

        result = index.internalPointer() if index is not None else None
        if isinstance(result, ExternalData):
            return

        if result is not None:
            symbol = result.element.symbol
            charge = result.element.charge
            symmetry = result.symmetry.value
            experiment = result.experiment.value
            edge = result.edge.value
        else:
            symbol = self.generalPage.symbolComboBox.currentText()
            charge = self.generalPage.chargeComboBox.currentText()
            symmetry = self.generalPage.symmetryComboBox.currentText()
            experiment = self.generalPage.experimentComboBox.currentText()
            edge = self.generalPage.edgeComboBox.currentText()

        # Detect whether the user changed only the symmetry. In that case the
        # symmetry-independent parameters are preserved and only the
        # symmetry-dependent Hamiltonian terms are regenerated.
        symmetryOnly = (
            result is None
            and symbol == previous.element.symbol
            and charge == previous.element.charge
            and experiment == previous.experiment.value
            and edge == previous.edge.value
            and symmetry != previous.symmetry.value
        )

        # Detect whether the user changed only the charge. In that case the
        # charge-independent parameters are preserved and only the
        # configuration-dependent parts (atomic parameters and the numbers of
        # states and configurations) are regenerated.
        chargeOnly = (
            result is None
            and symbol == previous.element.symbol
            and symmetry == previous.symmetry.value
            and experiment == previous.experiment.value
            and edge == previous.edge.value
            and charge != previous.element.charge
        )

        logger.debug("Start creating a new calculation.")
        state = Calculation(
            symbol=symbol,
            charge=charge,
            symmetry=symmetry,
            experiment=experiment,
            edge=edge,
            parent=self.model.rootItem(),
        )
        logger.debug("Finished creating the calculation.")

        logger.debug("Start copying the parameters.")
        if result is not None:
            state.copyFrom(result)
        elif symmetryOnly:
            state.copyFromExceptSymmetry(previous)
        elif chargeOnly:
            state.copyFromExceptCharge(previous)
        else:
            # For any other change (element, experiment, or edge) the
            # experimental conditions still apply and are carried over.
            state.copyExperimentalConditions(previous)
        logger.debug("Finished copying the parameters.")

        self.state = state
        logger.debug("Finished populating the widgets.")

    def addExternalData(self, raw, name):
        parent = self.resultsPage.model.rootItem()
        externalData = ExternalData(raw, parent=parent, name=name)
        index = externalData.index()
        self.resultsPage.view.setCurrentIndex(index)

    def run(self):
        progress = ProgressDialog(self)
        progress.rejected.connect(self.state.stop)
        self.state.runner.successful.connect(progress.accept)
        try:
            self.state.run()
        except RuntimeError as e:
            logger.error(e)
            return
        progress.show()

    def stop(self):
        self.state.stop()

    def saveInput(self):
        self.state.saveInput()

    def saveInputAs(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Quanty Input",
            os.path.join(self.currentPath, f"{self.state.value}.lua"),
            "Quanty Input File (*.lua)",
        )

        if path:
            basename = os.path.basename(path)
            self.state.value, _ = os.path.splitext(basename)
            self.currentPath = path
            try:
                self.state.saveInput()
            except OSError:
                return

    def updateLogger(self, data):
        self.parent().loggerWidget.appendPlainText(data)

    def updateMainWindowTitle(self, title=None):
        # The window title shows the same human-readable label as the results
        # view.
        self.parent().setWindowTitle(f"Crispy - {self.state.label}")

    def successful(self, successful):
        # Scroll to the bottom of the logger widget.
        scrollBar = self.parent().loggerWidget.verticalScrollBar()
        scrollBar.setValue(scrollBar.maximum())

        if not successful:
            return

        # If the "Hamiltonian Setup" page is currently selected, when the
        # current widget is set to the "Results Page", the former is not
        # displayed. To avoid this we switch first to the "General Setup" page.
        self.toolBox.setCurrentWidget(self.generalPage)
        self.toolBox.setCurrentWidget(self.resultsPage)

        # Move the state to the results model.
        self.state.setParent(self.resultsPage.model.rootItem())
        self.state.checkState = Qt.CheckState.Checked
        index = self.state.index()
        self.resultsPage.view.setCurrentIndex(index)

    def showHide(self):
        self.setVisible(not self.isVisible())

    @property
    def currentPath(self):
        settings = Config().read()
        return settings.value("CurrentPath")

    @currentPath.setter
    def currentPath(self, value):
        path = os.path.dirname(value)
        settings = Config().read()
        settings.setValue("CurrentPath", path)
        settings.sync()
