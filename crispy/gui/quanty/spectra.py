# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
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

from crispy.gui.items import BaseItem, SelectableItem
from crispy.utils.broaden import broaden

logger = logging.getLogger(__name__)


class Spectrum(SelectableItem):
    def __init__(self, parent=None, name=None):
        super().__init__(parent=parent, name=name)
        self.raw = None
        self.x = None
        self.signal = None
        self.suffix = None

    def copyFrom(self, item):
        super().copyFrom(item)
        self.suffix = copy.deepcopy(item.suffix)


class Spectrum1D(Spectrum):
    """One-dimensional spectrum.

    NOTE: The number of points of a Quanty spectrum is equal to N + 1, where N
    is the number of points specified in the input.
    """

    def __init__(self, parent, name):
        super().__init__(parent, name)
        self.axes = self.ancestor.axes

        self.axes.scale.dataChanged.connect(self.process)
        self.axes.normalization.dataChanged.connect(self.process)

        self.axes.xaxis.shift.dataChanged.connect(self.process)
        self.axes.xaxis.gaussian.dataChanged.connect(self.process)

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

    def shift(self, value=None):
        if value is None:
            value = self.axes.xaxis.shift.value
        self.x = self.x + value

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
        MAPPINGS = {
            "iso": "Iso",
            "k": "k",
            "cd": "CD",
            "r": "R",
            "l": "L",
            "ld": "LD",
            "h": "H",
            "v": "V",
        }
        name = MAPPINGS[self.suffix]
        legend = f"{index}-{name}"
        plotWidget.addCurve(self.x, self.signal, legend=legend)

    def copyFrom(self, item):
        super().copyFrom(item)
        self.x = copy.deepcopy(item.x)
        self.signal = copy.deepcopy(item.signal)


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
        replacements = dict()
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
            "Absorption": ("k", None),
            "Circular Dichroic": ("cd", "(R-L)"),
            "Right Polarized": ("r", "(R)"),
            "Left Polarized": ("l", "(L)"),
            "Linear Dichroic": ("ld", "(V-H)"),
            "Vertical Polarized": ("v", "(V)"),
            "Horizontal Polarized": ("h", "(H)"),
        }

        def addSpectrum(name, selected=True):
            suffix, symbol = SPECTRA[name]
            if symbol is not None:
                name = f"{name} {symbol}"
            if experiment.isOneDimensional:
                spectrum = Spectrum1D(parent=self.toPlot, name=name)
            else:
                # TODO: Here implement 2D.
                spectrum = None
            spectrum.suffix = suffix
            # Load before setting the check state to trigger plotting?
            spectrum.load()
            spectrum.checkState = Qt.Checked if selected else Qt.Unchecked

        for name in self.toCalculate.selected:
            addSpectrum(name)
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