# coding: utf-8
###################################################################
# Copyright (c) 2016-2022 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Spectra related components."""

import copy
import logging

import numpy as np
from PyQt5.QtCore import Qt

from crispy.items import BaseItem, SelectableItem
from crispy.quanty.hamiltonian import PdHybridizationTerm
from crispy.broaden import broaden

logger = logging.getLogger(__name__)


class Spectrum(SelectableItem):
    """Base class for spectrum objects.

    The objects don't necessary have to have data.
    """

    def __init__(self, parent=None, name=None):
        super().__init__(parent=parent, name=name)
        self.suffix = None

    def copyFrom(self, item):
        super().copyFrom(item)
        self.suffix = copy.deepcopy(item.suffix)


class Spectrum1D(Spectrum):
    """One-dimensional spectrum.

    The number of points of a Quanty spectrum is equal to N + 1, where N
    is the number of points specified in the input.
    """

    def __init__(self, parent=None, name=None):
        super().__init__(parent=parent, name=name)
        self.raw = None
        self.x = None
        self._signal = None

        self.axes = self.ancestor.axes

        self.axes.scale.dataChanged.connect(self.process)
        self.axes.normalization.dataChanged.connect(self.process)

        self.axes.xaxis.shift.dataChanged.connect(self.process)
        self.axes.xaxis.gaussian.dataChanged.connect(self.process)

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
        except (OSError, IOError):
            message = f"Could not read spectrum {filename}."
            logger.info(message)
            self.setParent(None)
            return

        self.process()

    def copy(self):
        self.x = self.raw[:, 0].copy()
        self.signal = self.raw[:, 2].copy()

    def process(self):
        self.copy()
        self.shift()
        self.scale()
        self.normalize()
        self.gaussian()
        self.dataChanged.emit(1)

    def shift(self, value=None):
        if value is None:
            value = self.axes.xaxis.shift.value
        self.x = self.x + value

    def scale(self, value=None):
        if value is None:
            value = self.axes.scale.value
        if value <= 0:
            return
        self.signal = self.signal * value

    def normalize(self, value=None):
        if value is None:
            value = self.axes.normalization.value
        value = value.lower()
        if value == "none":
            return
        if value == "maximum":
            absmax = np.abs(self.signal).max()
            self.signal = self.signal / absmax
        elif value == "area":
            area = np.abs(np.trapz(self.signal, self.x))
            self.signal = self.signal / area

    def gaussian(self, value=None):
        if value is None:
            value = self.axes.xaxis.gaussian.value
        fwhm = value / self.axes.xaxis.interval
        self.signal = broaden(self.signal, fwhm, kind="gaussian")

    def plot(self, plotWidget):
        if not self.checkState:
            return
        calculation = self.ancestor
        index = calculation.childPosition() + 1
        legend = f"{index}-{self.suffix}"
        plotWidget.addCurve(self.x, self.signal, legend=legend)

    def copyFrom(self, item):
        super().copyFrom(item)
        self.x = copy.deepcopy(item.x)
        self.signal = copy.deepcopy(item.signal)
        self.suffix = copy.deepcopy(item.suffix)


class Spectrum2D(Spectrum1D):
    """Two-dimensional spectrum."""

    def __init__(self, parent=None, name=None):
        super().__init__(parent=parent, name=name)
        self.y = None

        self.axes.yaxis.shift.dataChanged.connect(self.process)
        self.axes.yaxis.gaussian.dataChanged.connect(self.process)

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

    def plot(self, plotWidget):
        if not self.checkState:
            return
        calculation = self.ancestor
        index = calculation.childPosition() + 1
        MAPPINGS = {
            "iso": "Iso",
        }
        name = MAPPINGS[self.suffix]
        legend = f"{index}-{name}"
        plotWidget.addImage(
            self.signal, origin=self.origin, scale=self.axesScale, legend=legend
        )

    def copyFrom(self, item):
        super().copyFrom(item)
        self.y = copy.deepcopy(item.y)


class Sample(BaseItem):
    def __init__(self, parent=None, name=None):
        super().__init__(parent=parent, name=name)


class SpectraToInteract(BaseItem):
    @property
    def all(self):
        for spectrum in self.children():
            yield spectrum

    @property
    def selected(self):
        for spectrum in self.all:
            if spectrum.checkState:
                yield spectrum.name

    @selected.setter
    def selected(self, names):
        for spectrum in self.all:
            if spectrum.name in names:
                spectrum.checkState = Qt.Checked
            else:
                spectrum.checkState = Qt.Unchecked


class SpectraToCalculate(SpectraToInteract):
    def __init__(self, parent=None, name="Spectra to Calculate"):
        super().__init__(parent=parent, name=name)

        calculation = self.ancestor
        experiment = calculation.experiment

        SPECTRA = {
            "XAS": {
                "Powder/Solution": ("Isotropic Absorption",),
                "Single Crystal/Thin Film": (
                    "Absorption",
                    "Circular Dichroic",
                    "Linear Dichroic",
                ),
            },
            "XES": {"Powder/Solution": ("Emission",)},
            "XPS": {"Powder/Solution": ("Photoemission",)},
            "RIXS": {"Powder/Solution": ("Resonant Inelastic",)},
        }

        checkState = Qt.Checked
        for sample, spectraNames in SPECTRA[experiment.value].items():
            sample = Sample(parent=self, name=sample)
            for spectrumName in spectraNames:
                spectrum = Spectrum(parent=sample, name=spectrumName)
                spectrum._checkState = checkState
                checkState = Qt.Unchecked

    @property
    def all(self):
        for sample in self.children():
            for spectrum in sample.children():
                yield spectrum

    def copyFrom(self, item):
        super().copyFrom(item)
        # The order or the spectra should be the same in both objects.
        old = list(self.all)
        new = list(item.all)
        for o, n in zip(old, new):
            o.copyFrom(n)


class SpectraToPlot(SpectraToInteract):
    def __init__(self, parent=None, name="Spectra to Plot"):
        super().__init__(parent=parent, name=name)


class Spectra(BaseItem):
    def __init__(self, parent=None, name="Spectra"):
        super().__init__(parent=parent, name=name)
        self.toCalculate = SpectraToCalculate(parent=self)
        self.toPlot = SpectraToPlot(parent=self)

    @property
    def replacements(self):
        replacements = {}
        if not list(self.toCalculate.selected):
            value = "{}"
        else:
            value = "{"
            for name in self.toCalculate.selected:
                value += f'"{name}", '
            # Replace the last two characters of the string.
            value = value[:-2] + "} "
        replacements["SpectraToCalculate"] = value
        return replacements

    def load(self):
        calculation = self.ancestor
        experiment = calculation.experiment

        SPECTRA = {
            "Isotropic Absorption": ("iso", None),
            "Isotropic Absorption (Dipolar)": ("iso_dip", None),
            "Isotropic Absorption (Quadrupolar)": ("iso_quad", None),
            "Absorption": ("k", None),
            "Absorption (Dipolar)": ("k_dip", None),
            "Absorption (Quadrupolar)": ("k_quad", None),
            "Circular Dichroic": ("cd", "(R-L)"),
            "Circular Dichroic (Dipolar)": ("cd_dip", "(R-L)"),
            "Circular Dichroic (Quadrupolar)": ("cd_quad", "(R-L)"),
            "Right Polarized": ("r", "(R)"),
            "Left Polarized": ("l", "(L)"),
            "Linear Dichroic": ("ld", "(V-H)"),
            "Linear Dichroic (Dipolar)": ("ld_dip", "(V-H)"),
            "Linear Dichroic (Quadrupolar)": ("ld_quad", "(V-H)"),
            "Vertical Polarized": ("v", "(V)"),
            "Horizontal Polarized": ("h", "(H)"),
            "Resonant Inelastic": ("iso", None),
            "Photoemission": ("pho", None),
            "Emission": ("emi", None),
        }

        def addSpectrum(name, selected=True):
            suffix, symbol = SPECTRA[name]
            if symbol is not None:
                name = f"{name} {symbol}"

            if experiment.isOneDimensional:
                spectrum = Spectrum1D(parent=self.toPlot, name=name)
            else:
                spectrum = Spectrum2D(parent=self.toPlot, name=name)

            spectrum.suffix = suffix
            # Load before setting the check state to trigger plotting?
            spectrum.load()
            spectrum.checkState = Qt.Checked if selected else Qt.Unchecked

        for name in self.toCalculate.selected:
            addSpectrum(name)
            # The case of calculations with p-d hybridization.
            if calculation.hamiltonian.isTermEnabled(PdHybridizationTerm):
                addSpectrum(f"{name} (Dipolar)", selected=False)
                addSpectrum(f"{name} (Quadrupolar)", selected=False)
            if name == "Circular Dichroic":
                addSpectrum("Right Polarized", selected=False)
                addSpectrum("Left Polarized", selected=False)
            elif name == "Linear Dichroic":
                addSpectrum("Vertical Polarized", selected=False)
                addSpectrum("Horizontal Polarized", selected=False)

    def plot(self, plotWidget=None):
        if plotWidget is None:
            return
        calculation = self.ancestor
        xlabel, ylabel = calculation.axes.labels
        plotWidget.setGraphXLabel(xlabel)
        plotWidget.setGraphYLabel(ylabel)
        for spectrum in self.toPlot.children():
            spectrum.plot(plotWidget=plotWidget)

    def copyFrom(self, item):
        super().copyFrom(item)
        self.toCalculate.copyFrom(item.toCalculate)
