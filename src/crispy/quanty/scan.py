"""Scanning of one or more calculation parameters over a range of values.

A scan runs the current calculation repeatedly while stepping a set of
parameters through start/stop/step ranges. Every combination of values produces
one result that is added to the Results tree, labeled with the scanned values.
"""

import contextlib
import itertools
import logging
import math
import os

import qtawesome as qta
from silx.gui.qt import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLocale,
    QObject,
    QPushButton,
    QScrollArea,
    Qt,
    QVBoxLayout,
    QWidget,
    pyqtSignal,
)

from crispy import resourceAbsolutePath
from crispy.quanty.calculation import Calculation
from crispy.uic import loadUi

logger = logging.getLogger(__name__)


def valueRange(start, stop, step):
    """Return the inclusive list of values from start to stop with the given step.

    Raises:
        ValueError: if the step is not positive or the stop is below the start.
    """
    if step <= 0:
        raise ValueError("The step must be positive.")
    if stop < start:
        raise ValueError("The stop must not be smaller than the start.")
    # The small epsilon keeps the endpoint when it is only missed by floating
    # point rounding (e.g. start=0, stop=1, step=0.1).
    n = math.floor((stop - start) / step + 1e-9)
    return [start + i * step for i in range(n + 1)]


# The scope key meaning "apply to every Hamiltonian that holds the parameter".
ALL_SCOPE = None


def _shortHamiltonianName(name):
    """Shorten "Initial Hamiltonian" to "Initial" for display."""
    return name.replace(" Hamiltonian", "")


class ScanParameter:
    """A single scannable parameter of a calculation.

    The getter and setter resolve the parameter on a calculation by name so the
    same descriptor can be applied to freshly cloned calculations.

    Hamiltonian parameters exist in several Hamiltonians (initial, intermediate,
    final). For them ``scopes`` is a list of (display, key) pairs describing
    which Hamiltonian a value is applied to, starting with ("All", ALL_SCOPE);
    the chosen key is passed to the setter. For parameters that have a single
    target (scale factors, temperature, magnetic field) ``scopes`` is None and
    the setter ignores the scope.
    """

    def __init__(self, label, getter, setter, *, scopes=None, currentValue=None):
        self.label = label
        self._getter = getter
        self._setter = setter
        self.scopes = scopes
        self.currentValue = currentValue

    def apply(self, calculation, value, scope=ALL_SCOPE):
        self._setter(calculation, value, scope)

    def current(self, calculation):
        return self._getter(calculation)

    def scopeLabel(self, scope):
        """Human-readable suffix for a scope, empty for the all-Hamiltonians case."""
        if self.scopes is None or scope is ALL_SCOPE:
            return ""
        return _shortHamiltonianName(scope)


def _scaleFactorParameter(attr, label):
    def getter(calculation):
        return getattr(calculation.hamiltonian, attr).value

    def setter(calculation, value, scope=ALL_SCOPE):
        scaleFactor = getattr(calculation.hamiltonian, attr)
        scaleFactor.value = value
        # Mirror the GUI behavior, which propagates the global scale factor to
        # the individual atomic parameters.
        scaleFactor.updateIndividualScaleFactors(value)

    return ScanParameter(label, getter, setter)


def _hamiltonianParameter(termName, name, hamiltonianNames):
    """Build a scannable parameter for a Hamiltonian-term parameter.

    Args:
        termName: name of the owning term, used to disambiguate identically
            named parameters in different terms.
        name: name of the parameter, e.g. "10Dq(3d)".
        hamiltonianNames: ordered full names of the Hamiltonians that hold the
            parameter, e.g. ("Initial Hamiltonian", "Final Hamiltonian").
    """

    def iterMatching(calculation, scope):
        for term in calculation.hamiltonian.terms.children():
            if term.name != termName:
                continue
            for hamiltonian in term.children():
                if scope is not ALL_SCOPE and hamiltonian.name != scope:
                    continue
                for parameter in hamiltonian.children():
                    if parameter.name == name:
                        yield parameter

    def getter(calculation):
        for parameter in iterMatching(calculation, ALL_SCOPE):
            return parameter.value
        return None

    def setter(calculation, value, scope=ALL_SCOPE):
        # With ALL_SCOPE the value is written to every Hamiltonian holding the
        # parameter (matching the "Synchronize Parameters" behavior); otherwise
        # only to the selected Hamiltonian.
        for parameter in iterMatching(calculation, scope):
            parameter.value = value

    scopes = [("All", ALL_SCOPE)]
    scopes += [(_shortHamiltonianName(h), h) for h in hamiltonianNames]
    label = f"{termName} · {name}"
    return ScanParameter(label, getter, setter, scopes=scopes)


def scannableParameters(calculation):
    """Build the list of scannable parameters for a calculation.

    Includes the global scale factors, the temperature, the magnetic field, and
    the parameters of every enabled Hamiltonian term.
    """
    parameters = []

    for attr, label in (("fk", "Fk"), ("gk", "Gk"), ("zeta", "ζ")):
        parameters.append(_scaleFactorParameter(attr, label))

    parameters.append(
        ScanParameter(
            "Temperature",
            lambda c: c.temperature.value,
            lambda c, v, scope=ALL_SCOPE: setattr(c.temperature, "value", v),
        )
    )
    parameters.append(
        ScanParameter(
            "Magnetic Field",
            lambda c: c.magneticField.value,
            lambda c, v, scope=ALL_SCOPE: setattr(c.magneticField, "value", v),
        )
    )

    for term in calculation.hamiltonian.terms.children():
        if not term.isEnabled():
            continue
        # Group the parameters of the term by name, recording which Hamiltonians
        # hold each (in order: initial, intermediate, final).
        order = []
        nameToHamiltonians = {}
        for hamiltonian in term.children():
            for parameter in hamiltonian.children():
                if parameter.name not in nameToHamiltonians:
                    nameToHamiltonians[parameter.name] = []
                    order.append(parameter.name)
                nameToHamiltonians[parameter.name].append(hamiltonian.name)
        for name in order:
            parameters.append(
                _hamiltonianParameter(term.name, name, nameToHamiltonians[name])
            )

    # Cache the current value so the dialog can prefill the range fields.
    for parameter in parameters:
        parameter.currentValue = parameter.current(calculation)

    return parameters


class ScanRow(QWidget):
    """A single row of the scan dialog: parameter, start, stop and step."""

    changed = pyqtSignal()
    removeRequested = pyqtSignal(object)

    def __init__(self, parameters, parent=None):
        super().__init__(parent=parent)

        uiPath = os.path.join("quanty", "uis", "scanrow.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.parameters = parameters
        self._scopeKeys = []

        self.comboBox.addItems([parameter.label for parameter in parameters])
        self.removeButton.setIcon(qta.icon("fa6s.trash"))

        self.comboBox.currentIndexChanged.connect(self._parameterChanged)
        for lineEdit in (self.startLineEdit, self.stopLineEdit, self.stepLineEdit):
            lineEdit.textChanged.connect(self.changed)
        self.removeButton.clicked.connect(lambda: self.removeRequested.emit(self))

        self._parameterChanged()

    @property
    def parameter(self):
        return self.parameters[self.comboBox.currentIndex()]

    @property
    def scope(self):
        """The selected scope key, or ALL_SCOPE when the parameter has no scopes."""
        if not self._scopeKeys:
            return ALL_SCOPE
        return self._scopeKeys[self.scopeComboBox.currentIndex()]

    def _populateScopes(self):
        scopes = self.parameter.scopes
        self.scopeComboBox.blockSignals(True)
        self.scopeComboBox.clear()
        if scopes is None:
            # Keep the column aligned but inert for single-target parameters.
            self._scopeKeys = []
            self.scopeComboBox.addItem("—")
            self.scopeComboBox.setEnabled(False)
        else:
            self._scopeKeys = [key for _, key in scopes]
            self.scopeComboBox.addItems([display for display, _ in scopes])
            self.scopeComboBox.setEnabled(True)
        self.scopeComboBox.blockSignals(False)

    def _parameterChanged(self):
        self._populateScopes()
        self._prefill()

    def _prefill(self):
        """Seed the range with the current value of the selected parameter."""
        value = self.parameter.currentValue
        text = "" if value is None else QLocale().toString(float(value), "g", 4)
        self.startLineEdit.setText(text)
        self.stopLineEdit.setText(text)
        self.stepLineEdit.setText("0.1")
        self.changed.emit()

    def getState(self):
        """Capture the row setup as a plain dict for later restoration."""
        return {
            "label": self.parameter.label,
            "scope": self.scope,
            "start": self.startLineEdit.text(),
            "stop": self.stopLineEdit.text(),
            "step": self.stepLineEdit.text(),
        }

    def applyState(self, state):
        """Restore a captured setup. Return False if its parameter is gone."""
        labels = [parameter.label for parameter in self.parameters]
        if state["label"] not in labels:
            return False
        # Setting the parameter repopulates the scopes and prefills the range,
        # so the scope and the range fields are restored afterwards.
        self.comboBox.setCurrentIndex(labels.index(state["label"]))
        if state["scope"] in self._scopeKeys:
            self.scopeComboBox.setCurrentIndex(self._scopeKeys.index(state["scope"]))
        self.startLineEdit.setText(state["start"])
        self.stopLineEdit.setText(state["stop"])
        self.stepLineEdit.setText(state["step"])
        return True

    def values(self):
        """Return the list of values for this row, or None when it is invalid."""
        start = self.startLineEdit.value()
        stop = self.stopLineEdit.value()
        step = self.stepLineEdit.value()
        if start is None or stop is None or step is None:
            return None
        try:
            return valueRange(start, stop, step)
        except ValueError:
            return None


class ScanDialog(QDialog):
    """Modal dialog to set up a multi-parameter scan."""

    def __init__(self, parameters, parent=None, initialState=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Parameter Scan")
        self.parameters = parameters
        self.rows = []

        layout = QVBoxLayout(self)

        header = QLabel(
            "Add one or more parameters to scan. Each is stepped from its start "
            "to its stop value; every combination is calculated."
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        # Scrollable container for the dynamically added rows.
        self.rowsWidget = QWidget()
        self.rowsLayout = QVBoxLayout(self.rowsWidget)
        self.rowsLayout.setContentsMargins(0, 0, 0, 0)
        self.rowsLayout.addStretch()

        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(self.rowsWidget)
        layout.addWidget(scrollArea)

        self.addButton = QPushButton(qta.icon("fa6s.plus"), "Add Parameter")
        self.addButton.clicked.connect(self.addRow)
        layout.addWidget(self.addButton)

        self.countLabel = QLabel()
        layout.addWidget(self.countLabel)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Run")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        self._restore(initialState)
        self.updateCount()

    def addRow(self):
        row = ScanRow(self.parameters)
        row.changed.connect(self.updateCount)
        row.removeRequested.connect(self.removeRow)
        # Insert before the trailing stretch.
        self.rowsLayout.insertWidget(self.rowsLayout.count() - 1, row)
        self.rows.append(row)
        self.updateCount()
        return row

    def _restore(self, initialState):
        """Rebuild the rows from a saved snapshot, dropping stale parameters."""
        for state in initialState or []:
            row = self.addRow()
            if not row.applyState(state):
                self.removeRow(row)
        if not self.rows:
            self.addRow()

    def snapshot(self):
        """Capture the current rows for later restoration."""
        return [row.getState() for row in self.rows]

    def removeRow(self, row):
        self.rows.remove(row)
        row.setParent(None)
        row.deleteLater()
        self.updateCount()

    def count(self):
        """Total number of calculations, or None when any row is invalid."""
        if not self.rows:
            return 0
        total = 1
        for row in self.rows:
            values = row.values()
            if values is None:
                return None
            total *= len(values)
        return total

    def updateCount(self):
        total = self.count()
        runButton = self.buttonBox.button(QDialogButtonBox.Ok)
        if total is None:
            self.countLabel.setText("Some ranges are invalid.")
            runButton.setEnabled(False)
        else:
            plural = "" if total == 1 else "s"
            self.countLabel.setText(f"This will run {total} calculation{plural}.")
            runButton.setEnabled(total > 0)

    def spec(self):
        """Return the scan as a list of (parameter, scope, values) tuples."""
        return [(row.parameter, row.scope, row.values()) for row in self.rows]


class ScanController(QObject):
    """Run a scan by executing one calculation per parameter combination.

    Quanty runs asynchronously and one calculation at a time, so the
    combinations are executed sequentially: the next run starts only once the
    previous one has finished.
    """

    progress = pyqtSignal(int, int)  # current (1-based), total
    finished = pyqtSignal(int)  # number of successful calculations

    def __init__(self, base, resultsModel, parent=None):
        super().__init__(parent=parent)
        self.base = base
        self.resultsModel = resultsModel

        self._params = []
        self._scopes = []
        self._combinations = []
        self._index = 0
        self._completed = 0
        self._current = None
        self._cancelled = False

    def run(self, spec):
        self._params = [parameter for parameter, _, _ in spec]
        self._scopes = [scope for _, scope, _ in spec]
        valueLists = [values for _, _, values in spec]
        self._combinations = list(itertools.product(*valueLists))
        self._index = 0
        self._completed = 0
        self._cancelled = False
        self._runNext()

    def cancel(self):
        self._cancelled = True
        if self._current is not None:
            self._current.stop()

    def _runNext(self):
        if self._cancelled or self._index >= len(self._combinations):
            self.finished.emit(self._completed)
            return

        calculation = self._build(self._combinations[self._index])
        self._current = calculation
        self.progress.emit(self._index + 1, len(self._combinations))

        calculation.runner.successful.connect(self._onFinished)
        try:
            calculation.run()
        except RuntimeError as e:
            logger.error(e)
            self.finished.emit(self._completed)

    def _build(self, combination):
        base = self.base
        # The calculation is built detached (no parent) so that constructing it
        # and loading its spectra do not emit changes into the live results
        # model while it is only half-built. It is attached on success.
        calculation = Calculation(
            symbol=base.element.symbol,
            charge=base.element.charge,
            symmetry=base.symmetry.value,
            experiment=base.experiment.value,
            edge=base.edge.value,
            parent=None,
        )
        calculation.copyFrom(base)

        labels = []
        for parameter, scope, value in zip(
            self._params, self._scopes, combination, strict=False
        ):
            parameter.apply(calculation, value, scope)
            scopeLabel = parameter.scopeLabel(scope)
            name = parameter.label
            if scopeLabel:
                name = f"{name} ({scopeLabel})"
            labels.append(f"{name}={value:g}")
        calculation.labelSuffix = ", ".join(labels)

        # A unique prefix so the input and spectra files of the scan points do
        # not collide on disk.
        calculation.value = f"{base.value}_{self._index}"
        return calculation

    def _onFinished(self, successful):
        calculation = self._current
        with contextlib.suppress(TypeError, RuntimeError):
            calculation.runner.successful.disconnect(self._onFinished)

        if successful:
            self._completed += 1
            # Attach the finished result to the results model and check it so it
            # is plotted alongside the others. A failed run is left detached and
            # discarded.
            calculation.setParent(self.resultsModel.rootItem())
            calculation.checkState = Qt.CheckState.Checked

        self._index += 1
        self._runNext()
