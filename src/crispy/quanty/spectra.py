"""Spectra related components."""

import copy
import logging

import numpy as np
import silx
from silx.gui.qt import Qt

from crispy.broaden import broaden
from crispy.items import BaseItem, SelectableItem
from crispy.quanty.hamiltonian import PdHybridizationTerm

logger = logging.getLogger(__name__)


SPECTRA_TO_CALCULATE = {
    "XAS": {
        "Powder/Solution": ("Isotropic Absorption",),
        "Single Crystal/Thin Film": (
            "Absorption",
            "Circular Dichroic",
            "Linear Dichroic",
        ),
    },
    "XES": {"Single Crystal/Thin Film": ("Emission", "Circular Dichroic")},
    "XPS": {"Powder/Solution": ("Photoemission",)},
    "RIXS": {
        "Single Crystal/Thin Film": ("Resonant Inelastic",),
        "Powder/Solution": ("Isotropic Resonant Inelastic",),
    },
}


# Each entry maps a spectrum name to its (suffix, symbol, label, linestyle).
# The label is the text shown in the plot legend.
# fmt: off
SPECTRA = {
    "Isotropic Absorption": ("iso", None, "Isotropic Absorption", "-"),
    "Isotropic Absorption (Dipolar)": ("iso_dip", None, "Isotropic Absorption (Dipolar)", "--"),  # noqa: E501
    "Isotropic Absorption (Quadrupolar)": ("iso_quad", None, "Isotropic Absorption (Quadrupolar)", ":"),  # noqa: E501
    "Absorption": ("k", None, "Absorption", "-"),
    "Absorption (Dipolar)": ("k_dip", None, "Absorption (Dipolar)", "--"),
    "Absorption (Quadrupolar)": ("k_quad", None, "Absorption (Quadrupolar)", ":"),
    "Circular Dichroic": ("cd", "(R-L)", "CD (R-L)", "-."),
    "Circular Dichroic (Dipolar)": ("cd_dip", "(R-L)", "CD (R-L, Dipolar)", "--"),
    "Circular Dichroic (Quadrupolar)": ("cd_quad", "(R-L)", "CD (R-L, Quadrupolar)", ":"),  # noqa: E501
    "Right Polarized": ("r", "(R)", "CD (R)", "--"),
    "Left Polarized": ("l", "(L)", "CD (L)", ":"),
    "Linear Dichroic": ("ld", "(V-H)", "LD (V-H)", "-."),
    "Linear Dichroic (Dipolar)": ("ld_dip", "(V-H)", "LD (V-H, Dipolar)", "--"),
    "Linear Dichroic (Quadrupolar)": ("ld_quad", "(V-H)", "LD (V-H, Quadrupolar)", ":"),
    "Vertical Polarized": ("v", "(V)", "LD (V)", "--"),
    "Horizontal Polarized": ("h", "(H)", "LD (H)", ":"),
    "Resonant Inelastic": ("k", None, "Resonant Inelastic", None),
    "Isotropic Resonant Inelastic": ("iso", None, "Isotropic Resonant Inelastic", None),  # noqa: E501
    "Photoemission": ("pho", None, "Photoemission", "-"),
    "Emission": ("emi", None, "Emission", "-"),
}
# fmt: on

DEFAULT_COLORS = tuple(silx.config.DEFAULT_PLOT_CURVE_COLORS)


class BaseSpectrum(SelectableItem):
    """Base class for spectrum objects.

    The objects don't necessary have to have data.
    """

    def __init__(self, parent=None, *, name=None):
        super().__init__(parent=parent, name=name)
        self.suffix = None
        self.label = None
        self.lineStyle = "-"

    def _interactContainer(self):
        """The enclosing SpectraToInteract (to-calculate or to-plot), if any."""
        node = self.parent()
        while node is not None:
            if isinstance(node, SpectraToInteract):
                return node
            node = node.parent()
        return None

    def setData(self, column, value, role=Qt.EditRole):
        # A two-dimensional experiment (RIXS) produces a 2D map per spectrum, and
        # only one can be computed or displayed at a time. Checking one therefore
        # unchecks the others in the same list (single selection).
        if role == Qt.CheckStateRole and Qt.CheckState(value) == Qt.CheckState.Checked:
            calculation = self.ancestor
            if calculation is not None and calculation.experiment.isTwoDimensional:
                container = self._interactContainer()
                if container is not None:
                    for other in container.all:
                        if other is not self:
                            other.disable()
        return super().setData(column, value, role=role)

    def copyFrom(self, item):
        super().copyFrom(item)
        self.suffix = copy.deepcopy(item.suffix)
        self.label = copy.deepcopy(item.label)


class DataSpectrum(BaseSpectrum):
    """Base class for spectra that hold data and are processed for plotting.

    Subclasses implement the per-dimensionality pipeline steps used by
    process(): copy(), shift(), normalize() and gaussian(), as well as plot().
    """

    def __init__(self, parent=None, *, name=None):
        super().__init__(parent=parent, name=name)
        self.raw = None
        self.x = None
        self._signal = None

        self.axes = self.ancestor.axes

        for trigger in self.reprocessingTriggers:
            trigger.connect(self.process)

    def disconnectFromAxes(self):
        """Stop reprocessing on axis changes once the spectrum is discarded."""
        for trigger in self.reprocessingTriggers:
            try:
                trigger.disconnect(self.process)
            except (TypeError, RuntimeError):
                pass

    @property
    def reprocessingTriggers(self):
        """Signals whose emission requires the spectrum to be reprocessed."""
        return (
            self.axes.scale.dataChanged,
            self.axes.normalization.dataChanged,
            self.axes.xaxis.shift.dataChanged,
            self.axes.xaxis.gaussian.dataChanged,
        )

    @property
    def signal(self):
        return self._signal

    @signal.setter
    def signal(self, values):
        if values is None:
            return
        # Check for very small values.
        maximum = np.max(np.abs(values))
        if maximum < np.finfo(np.float32).eps:
            values = np.zeros_like(values)
        self._signal = values

    def load(self):
        calculation = self.ancestor
        filename = f"{calculation.value}_{self.suffix}.spec"

        try:
            self.raw = np.loadtxt(filename, skiprows=5)
        except OSError:
            message = f"Could not read spectrum {filename}."
            logger.info(message)
            self.disconnectFromAxes()
            self.setParent(None)
            return False

        self.process()
        return True

    def process(self):
        self.copy()
        self.shift()
        self.scale()
        self.normalize()
        self.gaussian()
        self.dataChanged.emit(1)

    def scale(self, value=None):
        if value is None:
            value = self.axes.scale.value
        if value <= 0:
            return
        self.signal = self.signal * value

    def copyFrom(self, item):
        super().copyFrom(item)
        self.x = copy.deepcopy(item.x)
        self.signal = copy.deepcopy(item.signal)
        self.suffix = copy.deepcopy(item.suffix)


class Spectrum1D(DataSpectrum):
    """One-dimensional spectrum.

    The number of points of a Quanty spectrum is equal to N + 1, where N
    is the number of points specified in the input.
    """

    def copy(self):
        self.x = self.raw[:, 0].copy()
        self.signal = self.raw[:, 2].copy()

    def shift(self, value=None):
        if value is None:
            value = self.axes.xaxis.shift.value
        self.x = self.x + value

    def normalize(self, value=None):
        if value is None:
            value = self.axes.normalization.value
        value = value.lower()
        if value == "none":
            return
        if value == "maximum":
            self.signal = self.signal / np.abs(self.signal).max()
        elif value == "area":
            area = np.abs(np.trapezoid(self.signal, self.x))
            self.signal = self.signal / area

    def gaussian(self, value=None):
        if value is None:
            value = self.axes.xaxis.gaussian.value
        fwhm = value / self.axes.xaxis.interval
        self.signal = broaden(self.signal, fwhm, kind="gaussian")

    def plot(self, plotWidget=None):
        if not self.isEnabled() or plotWidget is None:
            return
        calculation = self.ancestor
        index = calculation.childPosition()
        legend = f"{index + 1} · {self.label}"
        i = index % len(DEFAULT_COLORS)
        plotWidget.addCurve(
            self.x,
            self.signal,
            legend=legend,
            linestyle=self.lineStyle,
            color=DEFAULT_COLORS[i],
        )


class Spectrum2D(DataSpectrum):
    """Two-dimensional spectrum."""

    def __init__(self, parent=None, *, name=None):
        super().__init__(parent=parent, name=name)
        self.y = None

    @property
    def reprocessingTriggers(self):
        return (
            *super().reprocessingTriggers,
            self.axes.yaxis.shift.dataChanged,
            self.axes.yaxis.gaussian.dataChanged,
        )

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

    def copy(self):
        xaxis = self.axes.xaxis
        self.x = np.linspace(
            xaxis.start.value, xaxis.stop.value, xaxis.npoints.value + 1
        )

        yaxis = self.axes.yaxis
        self.y = np.linspace(
            yaxis.start.value, yaxis.stop.value, yaxis.npoints.value + 1
        )
        self.signal = self.raw[:, 2::2].copy()

    def shift(self, value=None):
        if value is None:
            xs = self.axes.xaxis.shift.value
            ys = self.axes.yaxis.shift.value
        else:
            xs, ys = value
        self.x = self.x + xs
        self.y = self.y + ys

    def normalize(self, value=None):
        if value is None:
            value = self.axes.normalization.value
        value = value.lower()
        if value == "none":
            return
        if value == "maximum":
            absmax = np.abs(self.signal).max()
            self.signal = self.signal / absmax

    def gaussian(self, value=None):
        if value is None:
            xg = self.axes.xaxis.gaussian.value
            yg = self.axes.yaxis.gaussian.value
        else:
            xg, yg = value

        xfwhm = xg / self.axes.xaxis.interval
        yfwhm = yg / self.axes.yaxis.interval

        fwhm = (xfwhm, yfwhm)

        self.signal = broaden(self.signal, fwhm, kind="gaussian")

    def plot(self, plotWidget=None):
        if not self.isEnabled() or plotWidget is None:
            return
        calculation = self.ancestor
        index = calculation.childPosition() + 1
        legend = f"{index} · {self.label}"
        plotWidget.addImage(
            self.signal, origin=self.origin, scale=self.axesScale, legend=legend
        )

    def copyFrom(self, item):
        super().copyFrom(item)
        self.y = copy.deepcopy(item.y)


class SpectraToInteract(BaseItem):
    @property
    def all(self):
        yield from self.children()

    @property
    def selected(self):
        for spectrum in self.all:
            if spectrum.isEnabled():
                yield spectrum.name

    @selected.setter
    def selected(self, names):
        for spectrum in self.all:
            if spectrum.name in names:
                spectrum.enable()
            else:
                spectrum.disable()


class SpectraToCalculate(SpectraToInteract):
    def __init__(self, parent=None):
        super().__init__(parent=parent, name="Spectra to Calculate")

        calculation = self.ancestor
        experiment = calculation.experiment

        checkState = Qt.CheckState.Checked
        for sample, spectraNames in SPECTRA_TO_CALCULATE[experiment.value].items():
            # The powder-averaged RIXS spectrum is built from the rank-2
            # fundamental spectra, which are only valid for dipole-in/dipole-out
            # edges. Skip it for the quadrupole-in edges (e.g. 1s2p, 1s3p).
            if (
                experiment.value == "RIXS"
                and sample == "Powder/Solution"
                and not calculation.isDipoleDipole
            ):
                continue
            sample = Sample(parent=self, name=sample)
            for spectrumName in spectraNames:
                spectrum = BaseSpectrum(parent=sample, name=spectrumName)
                spectrum.checkState = checkState
                checkState = Qt.CheckState.Unchecked

    @property
    def all(self):
        for sample in self.children():
            yield from sample.children()

    def copyFrom(self, item):
        super().copyFrom(item)
        # The order or the spectra should be the same in both objects.
        old = list(self.all)
        new = list(item.all)
        for o, n in zip(old, new, strict=False):
            o.copyFrom(n)


class SpectraToPlot(SpectraToInteract):
    def __init__(self, parent=None):
        super().__init__(parent=parent, name="Spectra to Plot")


class Spectra(BaseItem):
    def __init__(self, parent=None):
        super().__init__(parent=parent, name="Spectra")
        self.toCalculate = SpectraToCalculate(parent=self)
        self.toPlot = SpectraToPlot(parent=self)

    @property
    def replacements(self):
        if not list(self.toCalculate.selected):
            value = "{}"
        else:
            value = "{"
            for name in self.toCalculate.selected:
                value += f'"{name}", '
            # Replace the last two characters of the string.
            value = value[:-2] + "} "
        return {"SpectraToCalculate": value}

    def addSpectrum(self, name, selected=True):
        calculation = self.ancestor
        experiment = calculation.experiment
        suffix, symbol, label, linestyle = SPECTRA[name]
        if symbol is not None:
            name = f"{name} {symbol}"

        if experiment.isOneDimensional:
            spectrum = Spectrum1D(parent=self.toPlot, name=name)
            spectrum.lineStyle = linestyle
        else:
            spectrum = Spectrum2D(parent=self.toPlot, name=name)

        spectrum.suffix = suffix
        spectrum.label = label
        # Load before setting the check state to trigger plotting. Skip a
        # spectrum whose file could not be read; it has been discarded.
        if not spectrum.load():
            return
        spectrum.enable() if selected else spectrum.disable()

    def load(self):
        calculation = self.ancestor
        for name in self.toCalculate.selected:
            self.addSpectrum(name)
            # The case of calculations with p-d hybridization.
            if calculation.hamiltonian.isTermEnabled(PdHybridizationTerm):
                self.addSpectrum(f"{name} (Dipolar)", selected=False)
                self.addSpectrum(f"{name} (Quadrupolar)", selected=False)
            if name == "Circular Dichroic":
                self.addSpectrum("Right Polarized", selected=False)
                self.addSpectrum("Left Polarized", selected=False)
            elif name == "Linear Dichroic":
                self.addSpectrum("Vertical Polarized", selected=False)
                self.addSpectrum("Horizontal Polarized", selected=False)

    def plot(self, plotWidget=None):
        if plotWidget is None:
            return
        calculation = self.ancestor
        xlabel, ylabel = calculation.axes.labels
        plotWidget.setGraphXLabel(xlabel)
        plotWidget.setGraphYLabel(ylabel)
        for spectrum in self.toPlot.children():
            spectrum.plot(plotWidget)

    def copyFrom(self, item):
        super().copyFrom(item)
        self.toCalculate.copyFrom(item.toCalculate)


class Sample(BaseItem):
    def __init__(self, parent=None, *, name=None):
        super().__init__(parent=parent, name=name)
