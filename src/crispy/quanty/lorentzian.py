"""Dialog to set a constant or an energy dependent Lorentzian broadening."""

import logging
import os
from functools import partial
from math import ceil, hypot, isfinite, log10

from silx.gui.plot import PlotWidget
from silx.gui.plot.items import ItemChangedType
from silx.gui.qt import (
    QColor,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLocale,
    QMenu,
    Qt,
    QTableWidgetItem,
    QTimer,
)

from crispy import resourceAbsolutePath
from crispy.uic import loadUi
from crispy.widgets import RemoveButton

logger = logging.getLogger(__name__)

FWHM_COLOR = "#1f77b4"
SPECTRUM_COLOR = "#9e9e9e"
# Symbol size of the draggable points, in typographic points. The silx default
# for markers is 10.
POINT_SIZE = 6
# Largest distance (logical pixels) between a click and a point that selects it.
PICK_RADIUS = 8
# The table column after the energy and the FWHM holds the remove buttons.
REMOVE_COLUMN = 2


def stepPoints(energy, width, below, above):
    """Return the points of a step in the Lorentzian broadening.

    Args:
        energy: Energy at the middle of the step (eV).
        width: Width of the step (eV). A zero width gives a sharp step.
        below: FWHM below the step (eV).
        above: FWHM above the step (eV).

    Returns:
        A list with two (energy, FWHM) pairs.
    """
    return [(energy - width / 2, below), (energy + width / 2, above)]


def formatNumber(value):
    # Ten significant digits keep the energies of the K edges exact.
    return QLocale().toString(float(value), "g", 10)


def parseNumber(text):
    value, ok = QLocale().toDouble(text)
    return value if ok and isfinite(value) else None


class LorentzianDialog(QDialog):
    """Edit a constant or an energy dependent Lorentzian broadening.

    The energies use the same frame as the start and stop values of the axis.
    """

    def __init__(self, lorentzian, overlay=None, parent=None):
        """Create the dialog.

        Args:
            lorentzian: The Lorentzian item of an axis.
            overlay: Optional (x, y) arrays of a spectrum to show in the preview.
                The x values must use the same frame as the axis.
            parent: The parent widget.
        """
        super().__init__(parent)

        uiPath = os.path.join("quanty", "uis", "lorentzian.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        axis = lorentzian.parent()
        self.start = axis.start.value
        self.stop = axis.stop.value
        self.defaultValue = axis.coreholeWidth
        self.markers = []

        self.plot = PlotWidget(parent=self)
        # The margins are fractions of the plot size. In a small plot, the default
        # bottom margin is too small for the tick labels and the axis label.
        self.plot.setMinimumHeight(280)
        self.plot.setAxesMargins(0.15, 0.05, 0.1, 0.2)
        # The dialog sets the limits of the plot, so the user cannot zoom or pan.
        # The "select" mode keeps the markers draggable.
        self.plot.setInteractiveMode("select", zoomOnWheel=False)
        self.plot.setPanWithArrowKeys(False)
        self.plot.setGraphXLabel(f"{axis.label} (eV)")
        self.plot.setGraphYLabel("FWHM (eV)")
        self.plotLayout.addWidget(self.plot)
        plotArea = self.plot.getWidgetHandle()
        plotArea.setContextMenuPolicy(Qt.CustomContextMenu)
        plotArea.customContextMenuRequested.connect(self.showPlotMenu)
        if overlay is not None:
            # The zoom reset fits the right axis to the spectrum. The FWHM limits
            # are set later by refresh().
            x, y = overlay
            self.plot.addCurve(
                x,
                y,
                legend="spectrum",
                color=SPECTRUM_COLOR,
                yaxis="right",
                selectable=False,
            )

        header = self.pointsTableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(REMOVE_COLUMN, QHeaderView.ResizeToContents)

        self.valueLineEdit.setText(formatNumber(lorentzian.value))
        center = round((self.start + self.stop) / 2, 2)
        self.stepEnergyLineEdit.setText(formatNumber(center))
        self.stepWidthLineEdit.setText(formatNumber(0.0))
        self.stepBelowLineEdit.setText(formatNumber(lorentzian.value))
        self.stepAboveLineEdit.setText(formatNumber(lorentzian.value))
        self.writeTable(lorentzian.points.value)
        self.variableRadioButton.setChecked(lorentzian.isVariable)

        self.constantRadioButton.toggled.connect(self.updateMode)
        self.valueLineEdit.textChanged.connect(lambda _: self.refresh())
        self.applyStepPushButton.clicked.connect(self.applyStep)
        self.addPushButton.clicked.connect(self.addPoint)
        self.pointsTableWidget.itemChanged.connect(
            lambda _: self.setPoints(self.readTable())
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.resetPushButton.clicked.connect(self.reset)

        self.updateMode()

    def isVariable(self):
        return self.variableRadioButton.isChecked()

    def value(self):
        """Return the constant FWHM, or None when it is not a finite number."""
        return parseNumber(self.valueLineEdit.text())

    def points(self):
        """Return the (energy, FWHM) pairs of the table, sorted by energy."""
        rows = [row for row in self.readTable() if None not in row]
        return sorted(rows, key=lambda row: row[0])

    def readTable(self):
        """Return the rows, with None for cells that are not finite numbers."""
        table = self.pointsTableWidget
        rows = []
        for row in range(table.rowCount()):
            values = []
            for column in range(REMOVE_COLUMN):
                item = table.item(row, column)
                values.append(parseNumber(item.text()) if item is not None else None)
            rows.append(tuple(values))
        return rows

    def writeTable(self, rows):
        """Write the rows to the table. A None value keeps the text of the cell."""
        table = self.pointsTableWidget
        # Change the text of the items in place, because the method also runs
        # from the itemChanged signal of these items.
        table.blockSignals(True)
        table.setRowCount(len(rows))
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                item = table.item(row, column)
                if item is None:
                    item = QTableWidgetItem()
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    table.setItem(row, column, item)
                if value is not None:
                    item.setText(formatNumber(value))
            if table.cellWidget(row, REMOVE_COLUMN) is None:
                button = RemoveButton()
                button.clicked.connect(partial(self.removePoint, button))
                table.setCellWidget(row, REMOVE_COLUMN, button)
        table.blockSignals(False)

    def setPoints(self, rows):
        """Write the rows to the table, and sort them if all the cells are valid."""
        if all(None not in row for row in rows):
            # Quanty needs non-decreasing energies. The sort is stable, so rows
            # with the same energy keep their order.
            rows = sorted(rows, key=lambda row: row[0])
        self.writeTable(rows)
        self.refresh()

    def updateMode(self):
        variable = self.isVariable()
        if variable and self.pointsTableWidget.rowCount() == 0:
            value = self.value() or self.defaultValue
            self.writeTable([(self.start, value), (self.stop, value)])
        self.valueLineEdit.setEnabled(not variable)
        self.stepWidget.setEnabled(variable)
        self.pointsWidget.setEnabled(variable)
        self.refresh()

    def applyStep(self):
        lineEdits = (
            self.stepEnergyLineEdit,
            self.stepWidthLineEdit,
            self.stepBelowLineEdit,
            self.stepAboveLineEdit,
        )
        values = [parseNumber(lineEdit.text()) for lineEdit in lineEdits]
        if None in values or values[1] < 0:
            self.messageLabel.setText(
                "Enter a finite number in each step field. "
                "The width cannot be negative."
            )
            return
        self.setPoints(stepPoints(*values))

    def addPoint(self):
        rows = self.readTable()
        valid = [row for row in rows if None not in row]
        point = valid[-1] if valid else (self.stop, self.value() or self.defaultValue)
        self.setPoints([*rows, point])

    def removePoint(self, button):
        # Remove the row of the table instead of rewriting the table, because a
        # rewrite keeps the old text in the cells that are not valid numbers.
        table = self.pointsTableWidget
        rows = range(table.rowCount())
        table.removeRow(
            next(row for row in rows if table.cellWidget(row, REMOVE_COLUMN) is button)
        )
        self.refresh()

    def pointAt(self, pos):
        """Return the table row of the point nearest to a pixel position.

        Returns:
            The row, or None if no point is within PICK_RADIUS of the position.
        """
        candidates = []
        for row, (energy, fwhm) in enumerate(self.readTable()):
            if None in (energy, fwhm):
                continue
            x, y = self.plot.dataToPixel(energy, fwhm, check=False)
            distance = hypot(x - pos.x(), y - pos.y())
            if distance <= PICK_RADIUS:
                candidates.append((distance, row))
        return min(candidates)[1] if candidates else None

    def plotMenu(self, pos):
        """Return the context menu of the plot at a pixel position of the plot area.

        Returns:
            The menu, or None if the broadening is constant or the position is
            outside the axes.
        """
        position = self.plot.pixelToData(pos.x(), pos.y(), check=True)
        if not self.isVariable() or position is None:
            return None

        rows = self.readTable()
        energy = round(position[0], 2)
        if position[1] <= 0.0:
            return None
        fwhm = self.roundFwhm(position[1])
        menu = QMenu(self)
        add = menu.addAction("Add Point")
        add.triggered.connect(lambda: self.setPoints([*rows, (energy, fwhm)]))
        row = self.pointAt(pos)
        if row is not None:
            remove = menu.addAction("Remove Point")
            remove.triggered.connect(
                lambda: self.setPoints(rows[:row] + rows[row + 1 :])
            )
        return menu

    def showPlotMenu(self, pos):
        menu = self.plotMenu(pos)
        if menu is not None:
            menu.exec(self.plot.getWidgetHandle().mapToGlobal(pos))

    def reset(self):
        self.valueLineEdit.setText(formatNumber(self.defaultValue))
        self.pointsTableWidget.setRowCount(0)
        self.constantRadioButton.setChecked(True)
        self.updateMode()

    def validate(self):
        """Mark the cells that are not valid.

        Returns:
            A message for the user, and True if the input is valid.
        """
        if not self.isVariable():
            value = self.value()
            if value is None or value <= 0.0:
                return "The FWHM must be finite and positive.", False
            return "", True

        rows = self.readTable()
        if not rows:
            return "Add at least one point.", False

        numbers = True
        fwhms = True
        table = self.pointsTableWidget
        table.blockSignals(True)
        for row, (energy, fwhm) in enumerate(rows):
            checks = (energy is not None, fwhm is not None and fwhm > 0.0)
            for column, ok in enumerate(checks):
                color = None if ok else QColor("red")
                table.item(row, column).setData(Qt.ForegroundRole, color)
            numbers = numbers and None not in (energy, fwhm)
            fwhms = fwhms and (fwhm is None or fwhm > 0.0)
        table.blockSignals(False)

        if not numbers:
            return "Enter a number in each cell.", False
        if not fwhms:
            return "Each FWHM must be positive.", False
        energies = [energy for energy, _ in rows]
        if min(energies) < self.start or max(energies) > self.stop:
            message = (
                "Some points are outside the start and stop energies. "
                "Quanty uses the first and the last FWHM outside the points."
            )
            return message, True
        return "", True

    def refresh(self):
        message, valid = self.validate()
        self.messageLabel.setText(message)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)

        if self.isVariable():
            points = self.points()
        else:
            value = self.value()
            points = [] if value is None else [(self.start, value), (self.stop, value)]
        self.plotCurves(points)
        self.plotMarkers()
        self.setLimits(points)

    def plotCurves(self, points):
        for legend in ("points", "below", "above"):
            self.plot.remove(legend=legend, kind="curve")
        if not points:
            return

        energies = [energy for energy, _ in points]
        fwhms = [fwhm for _, fwhm in points]
        # A click on a selectable curve shows its legend as a tooltip.
        style = {"color": FWHM_COLOR, "resetzoom": False, "selectable": False}
        self.plot.addCurve(energies, fwhms, legend="points", **style)
        # Outside the points, Quanty uses the first and the last FWHM.
        if self.start < energies[0]:
            x, y = [self.start, energies[0]], [fwhms[0]] * 2
            self.plot.addCurve(x, y, legend="below", linestyle="--", **style)
        if energies[-1] < self.stop:
            x, y = [energies[-1], self.stop], [fwhms[-1]] * 2
            self.plot.addCurve(x, y, legend="above", linestyle="--", **style)

    def plotMarkers(self):
        for marker in self.markers:
            self.plot.removeItem(marker)
        self.markers = []
        if not self.isVariable():
            return

        for row, (energy, fwhm) in enumerate(self.readTable()):
            if None in (energy, fwhm):
                continue
            marker = self.plot.addMarker(
                energy,
                fwhm,
                legend=f"point {row}",
                color=FWHM_COLOR,
                symbol="o",
                draggable=True,
                constraint=partial(self.pointConstraint, fwhm),
            )
            marker.setSymbolSize(POINT_SIZE)
            marker.sigItemChanged.connect(partial(self.pointMoving, row, marker))
            marker.sigDragFinished.connect(partial(self.pointMoved, row, marker))
            self.markers.append(marker)

    def pointConstraint(self, fwhm, x, y):
        # A drag below zero keeps the original positive FWHM.
        return x, y if y > 0.0 else fwhm

    def setLimits(self, points):
        if not points:
            return
        energies = [energy for energy, _ in points]
        fwhms = [fwhm for _, fwhm in points]
        self.plot.getXAxis().setLimits(
            min(self.start, *energies), max(self.stop, *energies)
        )
        # Start the FWHM axis at zero to show the true size of the steps.
        self.plot.getYAxis().setLimits(0.0, 1.2 * max(fwhms))

    def movedRows(self, row, marker):
        """Return the rows of the table, with a row moved to the dragged point."""
        rows = self.readTable()
        x, y = marker.getPosition()
        rows[row] = (round(x, 2), self.roundFwhm(y))
        return rows

    def roundFwhm(self, fwhm):
        """Round a positive FWHM from the plot to the size of one pixel.

        The number of decimals follows the FWHM axis, so a narrow broadening
        keeps more decimals. The result stays positive.
        """
        _, _, _, height = self.plot.getPlotBoundsInPixels()
        ymin, ymax = self.plot.getYAxis().getLimits()
        decimals = max(0, ceil(-log10((ymax - ymin) / max(height, 1))))
        return max(round(fwhm, decimals), 10.0**-decimals)

    def pointMoving(self, row, marker, event):
        if event != ItemChangedType.POSITION:
            return
        rows = self.movedRows(row, marker)
        valid = [values for values in rows if None not in values]
        self.plotCurves(sorted(valid, key=lambda values: values[0]))

    def pointMoved(self, row, marker):
        rows = self.movedRows(row, marker)
        # Update the dialog after the drag ends, because the update removes the
        # point that sends the signal.
        QTimer.singleShot(0, partial(self.setPoints, rows))
