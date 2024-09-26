###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Axis related components."""

import copy
import logging
import os
from math import floor

import h5py
import numpy as np

from crispy import resourceAbsolutePath
from crispy.config import Config
from crispy.items import BaseItem, ComboItem, DoubleItem, IntItem, Vector3DItem
from crispy.quanty import XDB

logger = logging.getLogger(__name__)
settings = Config().read()


class Broadening(DoubleItem):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            return
        if value < 0.0:
            raise ValueError("The broadening cannot be negative.")
        self._value = value
        self.dataChanged.emit(1)


class Lorentzian(Broadening):
    MINIMUM = 0.1

    def __init__(self, parent=None, name="Lorentzian", value=None):
        super().__init__(parent=parent, name=name)
        self._value = value

        # TODO: Implement these for variable broadening.
        self.energies = BaseItem(self, "Energies")
        self.fwhms = BaseItem(self, "FWHM")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            return
        if value < self.MINIMUM:
            raise ValueError(
                f"The Lorentzian broadening cannot be smaller than {self.MINIMUM}."
            )
        self._value = value
        self.dataChanged.emit(1)

    @property
    def replacements(self):
        replacements = {}

        if self.ancestor.experiment.isTwoDimensional:
            # Energy dependent Lorentzian broadening of 2D spectra is not supported
            # in Quanty, so we use the value set for the Lorentzian broadening
            # as Gamma.
            replacements["Gamma"] = self.value
        else:
            axis = self.parent()
            start = axis.start.value
            stop = axis.stop.value

            points = [(start, self.value), (stop, self.value)]
            replacement = "{"
            for i, (energy, fwhm) in enumerate(points):
                replacement += f"{{{energy}, {fwhm}}}"
                if i != len(points) - 1:
                    replacement += ", "
                else:
                    replacement += "}"
            replacements["Lorentzian"] = replacement
            replacements["Gamma"] = self.MINIMUM

        return replacements

    def copyFrom(self, item):
        super().copyFrom(item)
        self.energies.copyFrom(item.energies)
        self.fwhms.copyFrom(item.fwhms)


class Gaussian(Broadening):
    def __init__(self, parent=None, name="Gaussian", value=None):
        super().__init__(parent=parent, name=name)
        self._value = value

    @property
    def replacements(self):
        replacements = {}
        # Use zero by default, but write the actual value as a comment.
        replacements["Gaussian"] = f"0.0 -- {self.value}"
        return replacements


class LightVector(Vector3DItem):
    @property
    def normalized(self):
        return self.value / np.linalg.norm(self.value)

    @property
    def replacements(self):
        # Normalize the vector.
        v = self.normalized
        return f"{{{v[0]:.8g}, {v[1]:.8g}, {v[2]:.8g}}}"


class WaveVector(LightVector):
    def __init__(self, parent=None, name="Wave Vector", value=None):
        super().__init__(parent=parent, name=name, value=value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if np.all(value == 0):
            raise ValueError("The wave vector cannot be null.")

        photon = self.parent()
        k, e1 = value, photon.e1.value
        # If the wave and polarization vectors are not perpendicular, select a new
        # perpendicular vector for the polarization.
        if np.dot(k, e1) != 0:
            if k[2] != 0 or (-k[0] - k[1]) != 0:
                e1 = np.array([k[2], k[2], -k[0] - k[1]])
            else:
                e1 = np.array([-k[2] - k[1], k[0], k[0]])

        self._value = value
        photon.e1.value = e1
        photon.e2.value = np.cross(e1, k)


class FirstPolarization(LightVector):
    def __init__(self, parent=None, name="First Polarization", value=None):
        super().__init__(parent=parent, name=name, value=value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if np.all(value == 0):
            raise ValueError("The polarization vector cannot be null.")

        photon = self.parent()
        if np.dot(photon.k.value, value) != 0:
            raise ValueError(
                "The wave and polarization vectors need to be perpendicular."
            )
        self._value = value
        photon.e2.value = np.cross(value, photon.k.value)


class SecondPolarization(LightVector):
    def __init__(self, parent=None, name="Second Polarization", value=None):
        super().__init__(parent=parent, name=name, value=value)


class Photon(BaseItem):
    def __init__(self, parent=None, name="Photon"):
        super().__init__(parent=parent, name=name)

        self.k = WaveVector(parent=self, value=np.array([0, 0, 1]))
        self.e1 = FirstPolarization(parent=self, value=np.array([0, 1, 0]))
        self.e2 = SecondPolarization(parent=self, value=np.array([1, 0, 0]))

    @property
    def replacements(self):
        return {
            "WaveVector": self.k.replacements,
            "FirstPolarization": self.e1.replacements,
            "SecondPolarization": self.e2.replacements,
        }

    def copyFrom(self, item):
        super().copyFrom(item)
        self.k.copyFrom(item.k)
        self.e1.copyFrom(item.e1)
        self.e2.copyFrom(item.e2)


class IncidentPhoton(Photon):
    def __init__(self, parent=None, name="Incident Photon"):
        super().__init__(parent=parent, name=name)


class ScatteredPhoton(Photon):
    def __init__(self, parent=None, name="Scattered Photon"):
        super().__init__(parent=parent, name=name)


class Start(DoubleItem):
    def __init__(self, parent=None, name="Start", value=None):
        super().__init__(parent=parent, name=name)
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        stop = self.parent().stop
        if stop.value is not None and value > stop.value:
            raise ValueError(
                "The lower energy limit cannot be larger than the upper limit."
            )
        self._value = value


class Stop(DoubleItem):
    def __init__(self, parent=None, name="Stop", value=None):
        super().__init__(parent=parent, name=name)
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        start = self.parent().start
        if start.value is not None and value < start.value:
            raise ValueError(
                "The upper energy limit cannot be larger than the lower limit."
            )
        self._value = value


class NPoints(IntItem):
    def __init__(self, parent=None, name="Number of Points", value=None):
        super().__init__(parent=parent, name=name)
        self._value = value

    @property
    def minimum(self):
        axis = self.parent()
        start, stop = axis.start, axis.stop
        lorentzian = axis.lorentzian
        return int(floor(stop.value - start.value) / lorentzian.value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value < self.minimum:
            raise ValueError(
                f"The number of points must be greater than {self.minimum}."
            )
        self._value = value
        self.dataChanged.emit(1)

    def reset(self):
        self.value = self.minimum


class Shift(DoubleItem):
    def __init__(self, parent=None, value=None):
        super().__init__(parent=parent, name="User Defined Shift", value=value)


class Axis(BaseItem):
    def __init__(self, parent=None, name="Axis"):
        super().__init__(parent=parent, name=name)

        self.idx = 0
        if name == "Y-axis":
            self.idx = 1

        # A user defined shift applied to the axis.
        self.shift = Shift(parent=self, value=0.0)

        start, stop = self.limits
        self.start = Start(parent=self, value=start)
        self.stop = Stop(parent=self, value=stop)
        self.npoints = NPoints(parent=self, value=2000)

        self.gaussian = Gaussian(parent=self, value=0.1)
        self.lorentzian = Lorentzian(parent=self, value=self.coreholeWidth)

        self.photon = None

    @property
    def interval(self):
        # Checked and it is consistent with Quanty.
        return np.abs(self.stop.value - self.start.value) / self.npoints.value

    @property
    def configuration(self):
        # Get the configuration for the axis.
        return self.ancestor.configurations[self.idx + 1]

    @property
    def zeroShift(self):
        # Calculate the shift required to approximately align the edge to zero. The
        # shift is calculated using the spin-orbit coupling parameter of the
        # core subshell for the electronic configuration of the element in the
        # 2+ oxidation state.
        calculation = self.ancestor
        element = calculation.element

        chargeDelta = element.chargeDifference(charge="2+")

        # Add the charge delta to the configuration string.
        subshells = self.configuration.subshells
        occupancies = list(self.configuration.occupancies)
        occupancies[-1] = occupancies[-1] + chargeDelta
        occupancies = tuple(occupancies)

        baseConfigurationValue = ",".join(
            f"{subshell}{occupancy}"
            for subshell, occupancy in zip(subshells, occupancies)
        )

        if self.configuration.hasCore:
            coreSubshell = self.configuration.subshells[0]
            name = f"ζ({coreSubshell})"
            path = resourceAbsolutePath(
                os.path.join("quanty", "parameters", f"{element.symbol}.h5")
            )

            with h5py.File(path, "r") as h5:
                try:
                    value = h5[baseConfigurationValue]["Atomic"][name][()]
                except KeyError:
                    value = 0.0
            factor = 0.5 if "p" in coreSubshell else 1.0
            value *= factor
        else:
            # The value is zero for configurations without core-hole.
            # These can be the final configurations RIXS or XES calculations.
            value = 0.0

        return value

    @property
    def limits(self):
        calculation = self.ancestor

        STEP = 10
        if calculation.experiment.isEmission:
            limits = [-3 * STEP, STEP]
        else:
            label = calculation.edge.labels[self.idx]
            if label in ("K", "L1", "M1", "N1"):
                limits = [-STEP, STEP]
            else:
                subshell = calculation.element.valenceSubshell
                if subshell in ("3d",):
                    limits = [-STEP, 3 * STEP]
                else:
                    limits = [-STEP, 2 * STEP]

        # Shift the limits to focus on the lower-energy edge or line.
        limits = [limit - self.zeroShift for limit in limits]

        shift = 0.0
        shiftSpectra = settings.value("Quanty/ShiftSpectra", type=bool)
        if shiftSpectra:
            shift = self.zeroShift + self.experimentalShift

        # Update and round the limits.
        return [round(limit + shift, 0) for limit in limits]

    @property
    def experimentalShift(self):
        """Experimental edges/lines energies."""
        calculation = self.ancestor
        label = calculation.edge.labels[self.idx]
        if calculation.experiment.isEmission:
            energy = XDB.xray_lines(calculation.element.symbol)[label].energy
        else:
            try:
                energy = XDB.xray_edges(calculation.element.symbol)[label].energy
            except (TypeError, AttributeError, KeyError):
                energy = 0.0
                logger.debug(
                    "%s %s %s %s",
                    calculation.element,
                    calculation.experiment,
                    calculation.edge,
                    label,
                )
        return energy

    @property
    def coreholeWidth(self):
        calculation = self.ancestor
        label = calculation.edge.labels[self.idx]
        try:
            coreholeWidth = XDB.corehole_width(calculation.element.symbol, label)
        except KeyError:
            coreholeWidth = 0.1

        try:
            coreholeWidth = float(coreholeWidth)
        except TypeError:
            coreholeWidth = 0.1

        coreholeWidth = max(coreholeWidth, 0.1)

        return round(coreholeWidth, 2)

    @property
    def replacements(self):
        replacements = {}

        replacements["Emin"] = self.start.value
        replacements["Emax"] = self.stop.value
        replacements["NPoints"] = self.npoints.value
        replacements["ZeroShift"] = self.zeroShift
        replacements["ExperimentalShift"] = self.experimentalShift
        # The Gaussian broadening is done in the interface, but we still
        # want the user to easily change this value if the script is run from
        # outside.
        replacements.update(self.lorentzian.replacements)
        replacements.update(self.gaussian.replacements)
        replacements.update(self.photon.replacements)

        prefix = self.name[0]
        replacements = {prefix + name: value for name, value in replacements.items()}

        return replacements

    def copyFrom(self, item):
        super().copyFrom(item)
        self.idx = copy.deepcopy(item.idx)
        self.start.copyFrom(item.start)
        self.stop.copyFrom(item.stop)
        self.npoints.copyFrom(item.npoints)
        self.gaussian.copyFrom(item.gaussian)
        self.lorentzian.copyFrom(item.lorentzian)
        self.shift.copyFrom(item.shift)
        self.photon.copyFrom(item.photon)


class XAxis(Axis):
    def __init__(self, parent=None, name="X-axis"):
        super().__init__(parent=parent, name=name)
        self.photon = IncidentPhoton(parent=self)

    @property
    def label(self):
        calculation = self.ancestor
        value = calculation.experiment.value
        if value == "XAS":
            return "Absorption Energy"
        if value == "XES":
            return "Emission Energy"
        if value == "XPS":
            return "Binding Energy"
        return "Incident Energy"


class YAxis(Axis):
    def __init__(self, parent=None, name="Y-axis"):
        super().__init__(parent=parent, name=name)
        self.photon = ScatteredPhoton(parent=self)

    @property
    def label(self):
        return "Energy Transfer"


class Axes(BaseItem):
    def __init__(self, parent=None, name="Axes"):
        super().__init__(parent=parent, name=name)

        self.scale = DoubleItem(parent=self, name="Scale Factor", value=1.0)
        self.normalization = ComboItem(parent=self, name="Normalization", value="None")
        self.normalization.items = ["None", "Maximum", "Area"]

        self.xaxis = XAxis(parent=self)

        calculation = self.ancestor
        self.labels = [f"{self.xaxis.label} (eV)", "Intensity (a.u.)"]

        if calculation.experiment.isTwoDimensional:
            self.xaxis.npoints.reset()
            self.xaxis.lorentzian.dataChanged.connect(self.xaxis.npoints.reset)
            self.yaxis = YAxis(parent=self)
            self.labels = [f"{l} (eV)" for l in (self.xaxis.label, self.yaxis.label)]

    def copyFrom(self, item):
        super().copyFrom(item)
        self.scale.copyFrom(item.scale)
        self.normalization.copyFrom(item.normalization)
        self.xaxis.copyFrom(item.xaxis)
        if getattr(self, "yaxis", None) is not None:
            self.yaxis.copyFrom(item.yaxis)
