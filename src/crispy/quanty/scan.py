"""Scanning of one or more calculation parameters over a range of values.

A scan runs the current calculation repeatedly while stepping a set of
parameters through start/stop/step ranges. Every combination of values produces
one result that is added to the Results tree, labeled with the scanned values.
"""

import contextlib
import itertools
import logging
import math

from silx.gui.qt import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLocale,
    QObject,
    QPushButton,
    Qt,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    pyqtSignal,
)

from crispy.quanty.calculation import Calculation
from crispy.quanty.lorentzian import parseNumber
from crispy.widgets import ComboBox, RemoveButton

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


# Apply to every Hamiltonian that holds the parameter.
ALL_HAMILTONIANS = None


def _shortHamiltonianName(name):
    """Shorten "Initial Hamiltonian" to "Initial" for display."""
    return name.replace(" Hamiltonian", "")


class ScanParameter:
    """A single scannable parameter of a calculation.

    The getter and setter resolve the parameter on a calculation by name so the
    same descriptor can be applied to freshly cloned calculations.

    Hamiltonian parameters exist in several Hamiltonians (initial, intermediate,
    final). For them ``hamiltonians`` lists (display, key) pairs, starting with
    ("All", ALL_HAMILTONIANS). The setter uses the selected key to choose which
    Hamiltonian receives the value. For scale factors, temperature, and magnetic
    field, ``hamiltonians`` is None. Their setters ignore the Hamiltonian name.
    """

    def __init__(self, label, getter, setter, *, hamiltonians=None, currentValue=None):
        self.label = label
        self._getter = getter
        self._setter = setter
        self.hamiltonians = hamiltonians
        self.currentValue = currentValue

    def apply(self, calculation, value, hamiltonianName=ALL_HAMILTONIANS):
        self._setter(calculation, value, hamiltonianName)

    def current(self, calculation):
        return self._getter(calculation)

    def hamiltonianLabel(self, hamiltonianName):
        """Return the Hamiltonian suffix, or an empty string for all Hamiltonians."""
        if self.hamiltonians is None or hamiltonianName is ALL_HAMILTONIANS:
            return ""
        return _shortHamiltonianName(hamiltonianName)


def _scaleFactorParameter(attr, label):
    def getter(calculation):
        return getattr(calculation.hamiltonian, attr).value

    def setter(calculation, value, hamiltonianName=ALL_HAMILTONIANS):
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

    def iterMatching(calculation, hamiltonianName):
        for term in calculation.hamiltonian.terms.children():
            if term.name != termName:
                continue
            for hamiltonian in term.children():
                if (
                    hamiltonianName is not ALL_HAMILTONIANS
                    and hamiltonian.name != hamiltonianName
                ):
                    continue
                for parameter in hamiltonian.children():
                    if parameter.name == name:
                        yield parameter

    def getter(calculation):
        for parameter in iterMatching(calculation, ALL_HAMILTONIANS):
            return parameter.value
        return None

    def setter(calculation, value, hamiltonianName=ALL_HAMILTONIANS):
        # ALL_HAMILTONIANS matches the "Synchronize Parameters" behavior.
        for parameter in iterMatching(calculation, hamiltonianName):
            parameter.value = value

    hamiltonians = [("All", ALL_HAMILTONIANS)]
    hamiltonians += [(_shortHamiltonianName(h), h) for h in hamiltonianNames]
    label = f"{termName} · {name}"
    return ScanParameter(label, getter, setter, hamiltonians=hamiltonians)


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
            lambda c, v, hamiltonianName=ALL_HAMILTONIANS: setattr(
                c.temperature, "value", v
            ),
        )
    )
    parameters.append(
        ScanParameter(
            "Magnetic Field",
            lambda c: c.magneticField.value,
            lambda c, v, hamiltonianName=ALL_HAMILTONIANS: setattr(
                c.magneticField, "value", v
            ),
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


class ScanRow:
    """A row of the scan table: parameter, Hamiltonian, start, stop and step.

    The parameter and the Hamiltonian selectors are combo boxes. The start, stop
    and step are table items, as the points in the table of the Lorentzian dialog.
    """

    def __init__(self, parameters):
        self.parameters = parameters
        self._hamiltonianKeys = []

        self.comboBox = ComboBox()
        self.comboBox.addItems([parameter.label for parameter in parameters])
        self.hamiltonianComboBox = ComboBox()
        self.items = [QTableWidgetItem() for _ in range(3)]
        for item in self.items:
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.removeButton = RemoveButton()

        self.comboBox.currentIndexChanged.connect(self._parameterChanged)

        self._parameterChanged()

    @property
    def parameter(self):
        return self.parameters[self.comboBox.currentIndex()]

    @property
    def hamiltonianName(self):
        """Return the selected Hamiltonian name, or ALL_HAMILTONIANS."""
        if not self._hamiltonianKeys:
            return ALL_HAMILTONIANS
        return self._hamiltonianKeys[self.hamiltonianComboBox.currentIndex()]

    def _populateHamiltonians(self):
        hamiltonians = self.parameter.hamiltonians
        self.hamiltonianComboBox.blockSignals(True)
        self.hamiltonianComboBox.clear()
        if hamiltonians is None:
            # Keep the column aligned but inert for single-target parameters.
            self._hamiltonianKeys = []
            self.hamiltonianComboBox.addItem("—")
            self.hamiltonianComboBox.setEnabled(False)
        else:
            self._hamiltonianKeys = [key for _, key in hamiltonians]
            self.hamiltonianComboBox.addItems([display for display, _ in hamiltonians])
            self.hamiltonianComboBox.setEnabled(True)
        self.hamiltonianComboBox.blockSignals(False)

    def _parameterChanged(self):
        self._populateHamiltonians()
        self._prefill()

    def _prefill(self):
        """Seed the range with the current value of the selected parameter."""
        value = self.parameter.currentValue
        text = "" if value is None else QLocale().toString(float(value), "g", 4)
        for item, itemText in zip(self.items, (text, text, "0.1"), strict=True):
            item.setText(itemText)

    def getState(self):
        """Capture the row setup as a plain dict for later restoration."""
        start, stop, step = (item.text() for item in self.items)
        return {
            "label": self.parameter.label,
            "hamiltonian": self.hamiltonianName,
            "start": start,
            "stop": stop,
            "step": step,
        }

    def applyState(self, state):
        """Restore a captured setup. Return False if its parameter is gone."""
        labels = [parameter.label for parameter in self.parameters]
        if state["label"] not in labels:
            return False
        # Restore the Hamiltonian and range after the parameter resets them.
        self.comboBox.setCurrentIndex(labels.index(state["label"]))
        if state["hamiltonian"] in self._hamiltonianKeys:
            self.hamiltonianComboBox.setCurrentIndex(
                self._hamiltonianKeys.index(state["hamiltonian"])
            )
        for item, key in zip(self.items, ("start", "stop", "step"), strict=True):
            item.setText(state[key])
        return True

    def values(self):
        """Return the list of values for this row, or None when it is invalid."""
        start, stop, step = (parseNumber(item.text()) for item in self.items)
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

        # The table looks like the table of points in the Lorentzian dialog.
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Parameter", "Hamiltonian", "Start", "Stop", "Step", ""]
        )
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        columns = self.table.horizontalHeader()
        columns.setDefaultSectionSize(80)
        columns.setSectionResizeMode(0, QHeaderView.Stretch)
        # Wide enough for "Intermediate".
        columns.resizeSection(1, 140)
        columns.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.itemChanged.connect(self.updateCount)
        layout.addWidget(self.table)

        self.addButton = QPushButton("Add Parameter")
        self.addButton.clicked.connect(self.addRow)
        layout.addWidget(self.addButton)

        self.countLabel = QLabel()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Run")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Show the count on the same row as the buttons, in the free space on
        # the left.
        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(self.countLabel)
        bottomLayout.addWidget(self.buttonBox)
        layout.addLayout(bottomLayout)

        self._restore(initialState)
        self.updateCount()
        # Leave space for the long names of the Hamiltonian parameters.
        self.resize(640, 300)

    def addRow(self):
        row = ScanRow(self.parameters)
        row.removeButton.clicked.connect(lambda: self.removeRow(row))
        # The rows list and the table rows have the same order.
        index = len(self.rows)
        self.rows.append(row)
        self.table.insertRow(index)
        self.table.setCellWidget(index, 0, row.comboBox)
        self.table.setCellWidget(index, 1, row.hamiltonianComboBox)
        for column, item in enumerate(row.items, start=2):
            self.table.setItem(index, column, item)
        self.table.setCellWidget(index, 5, row.removeButton)
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
        index = self.rows.index(row)
        self.table.removeRow(index)
        del self.rows[index]
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
        """Return the scan as a list of (parameter, hamiltonianName, values) tuples."""
        return [(row.parameter, row.hamiltonianName, row.values()) for row in self.rows]


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
        self._hamiltonianNames = []
        self._combinations = []
        self._index = 0
        self._completed = 0
        self._current = None
        self._cancelled = False

    def run(self, spec):
        self._params = [parameter for parameter, _, _ in spec]
        self._hamiltonianNames = [hamiltonianName for _, hamiltonianName, _ in spec]
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
        for parameter, hamiltonianName, value in zip(
            self._params, self._hamiltonianNames, combination, strict=False
        ):
            parameter.apply(calculation, value, hamiltonianName)
            hamiltonianLabel = parameter.hamiltonianLabel(hamiltonianName)
            name = parameter.label
            if hamiltonianLabel:
                name = f"{name} ({hamiltonianLabel})"
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
