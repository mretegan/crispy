###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""The Quanty Hamiltonian and terms."""

import copy
import logging
import os
from math import factorial

import h5py
from silx.gui.qt import QLocale, Qt

from crispy import resourceAbsolutePath
from crispy.items import BaseItem, BoolItem, DoubleItem, IntItem, SelectableItem

OCCUPANCIES = {"s": 2, "p": 6, "d": 10, "f": 14}
logger = logging.getLogger(__name__)


class ScaleFactor(DoubleItem):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value < 0.0:
            raise ValueError("The scale factor must be positive.")
        self._value = value
        self.dataChanged.emit(1)

    def updateIndividualScaleFactors(self, value):
        CONVERTERS = {"Fk": "F", "Gk": "G", "Zeta": "ζ"}
        calculation = self.ancestor
        hamiltonian = calculation.hamiltonian
        children = hamiltonian.findChildren(HamiltonianParameter)
        for child in children:
            if child.name.startswith(CONVERTERS[self.name]):
                child.scaleFactor = value

    def setData(self, column, value, role=Qt.EditRole):
        if column == 1:
            value, ok = QLocale().toDouble(value)
            if not ok:
                return False

        if role == Qt.EditRole:
            if column == 1:
                self.value = value
            self.updateIndividualScaleFactors(value)
            return True
        return super().setData(column, value, role)


class HamiltonianParameter(DoubleItem):
    def __init__(self, parent=None, name=None, value=None, scaleFactor=None):
        super().__init__(parent=parent, name=name, value=value)
        self._scaleFactor = scaleFactor

    def columnCount(self):
        return 3

    @property
    def scaleFactor(self):
        return self._scaleFactor

    @scaleFactor.setter
    def scaleFactor(self, value):
        self._scaleFactor = value
        self.dataChanged.emit(2)

    def data(self, column, role=Qt.DisplayRole):
        def formatData(value, precision=3):
            if value is None:
                return value
            if abs(value) < 1e-3 and value != 0.0:
                text = QLocale().toString(value, "E", 3)
            else:
                text = QLocale().toString(value, "f", precision)
            return text

        if role in (Qt.DisplayRole, Qt.EditRole):
            if column == 1:
                return formatData(self.value, precision=3)
            if column == 2:
                return formatData(self.scaleFactor, precision=2)
        elif role in (Qt.UserRole,):
            if column == 2:
                return self.scaleFactor
        elif role == Qt.TextAlignmentRole:
            if column > 0:
                return Qt.AlignRight
        return super().data(column, role)

    def synchronizeParameters(self, column, value):
        # If requested, synchronize the parameters of the Hamiltonian.
        calculation = self.ancestor
        hamiltonian = calculation.hamiltonian
        if not hamiltonian.synchronizeParameters.value:
            return

        siblings = self.parent().siblings()
        for sibling in siblings:
            for child in sibling.children():
                if child.name == self.name and child is not self:
                    if column == 1:
                        child.value = value
                    if column == 2:
                        child.scaleFactor = value

    def setData(self, column, value, role=Qt.EditRole):
        # Do the conversion to float here as the value might be needed for other items.
        if column > 0:
            value, ok = QLocale().toDouble(value)
            if not ok:
                return False

        if role == Qt.EditRole:
            if column == 1:
                self.value = value
            if column == 2:
                self.scaleFactor = value
            self.synchronizeParameters(column, value)
            return True
        return super().setData(column, value, role)

    def copyFrom(self, item):
        super().copyFrom(item)
        self._scaleFactor = copy.deepcopy(item.scaleFactor)


class HamiltonianTerm(SelectableItem):
    def __init__(self, parent=None, name=None):
        super().__init__(parent=parent, name=name)

        # Makes things easier to call.
        calculation = self.ancestor
        self.block = calculation.element.valenceBlock
        self.subshell = calculation.element.valenceSubshell
        self.element = calculation.element
        self.symmetry = calculation.symmetry
        self.experiment = calculation.experiment
        self.edge = calculation.edge
        self.configurations = calculation.configurations

        # This can't be accessed via the calculation object.
        self.hamiltonian = self.parent().parent()

    @property
    def hamiltonianNames(self):
        names = [("Initial Hamiltonian", "i"), ("Final Hamiltonian", "f")]
        if self.experiment.isTwoSteps:
            names.insert(1, ("Intermediate Hamiltonian", "m"))
        return names

    @property
    def replacements(self):
        replacements = {}

        # Use the name of the class to generate the name of the replacement.
        name = type(self).__name__
        replacements[name] = self.isEnabled()

        def formatName(name):
            CONVERTERS = {
                "ζ": "zeta",
                "Δ": "Delta",
                "σ": "sigma",
                "τ": "tau",
                "μ": "mu",
                "ν": "nu",
            }
            for greek, latin in CONVERTERS.items():
                name = name.replace(greek, latin)
            return name

        # Fill the replacements dictionary with the parameters names, values, and
        # scale factors.
        mappings = dict(self.hamiltonianNames)
        for hamiltonian in self.children():
            # Each type of Hamiltonian has a certain suffix.
            suffix = mappings[hamiltonian.name]
            for parameter in hamiltonian.children():
                name = f"{formatName(parameter.name)}_{suffix}"
                replacements[f"{name}_value"] = parameter.value
                if parameter.scaleFactor is not None:
                    replacements[f"{name}_scaleFactor"] = parameter.scaleFactor

        return replacements

    def scaleFactorFromName(self, name):
        if name.startswith("F"):
            return self.hamiltonian.fk.value
        if name.startswith("G"):
            return self.hamiltonian.gk.value
        if name.startswith("ζ"):
            return self.hamiltonian.zeta.value
        return None

    @property
    def parameters(self):
        for hamiltonian in self.children():
            yield from hamiltonian.children()

    def copyFrom(self, item):
        super().copyFrom(item)
        old = list(self.parameters)
        new = list(item.parameters)
        for o, n in zip(old, new):
            o.copyFrom(n)


class AtomicTerm(HamiltonianTerm):
    def __init__(self, parent=None, name="Atomic"):
        super().__init__(parent=parent, name=name)

        path = resourceAbsolutePath(
            os.path.join("quanty", "parameters", f"{self.element.symbol}.h5")
        )

        with h5py.File(path, "r") as h5:
            for configuration, (hamiltonianName, _) in zip(
                self.configurations, self.hamiltonianNames
            ):
                hamiltonian = BaseItem(self, hamiltonianName)
                parameters = h5[f"{configuration}/{self.name}"]
                for parameterName, value in parameters.items():
                    value = float(value[()])
                    scaleFactor = self.scaleFactorFromName(parameterName)
                    HamiltonianParameter(hamiltonian, parameterName, value, scaleFactor)

        self.enable()

    def setData(self, column, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole:
            # The atomic term should always be checked.
            return False
        return super().setData(column, value, role=role)


class CrystalFieldTerm(HamiltonianTerm):
    def __init__(self, parent=None, name="Crystal Field"):
        super().__init__(parent=parent, name=name)

        names = []
        if self.block == "d":
            if self.symmetry.value == "Oh":
                names, values = ("10Dq",), (1.0,)
            elif self.symmetry.value == "Td":
                names, values = ("10Dq",), (0.5,)
            elif self.symmetry.value == "D4h":
                names, values = ("10Dq", "Ds", "Dt"), (1.0, 0.0, 0.0)
            elif self.symmetry.value == "D3h":
                names, values = ("Dμ", "Dν"), (0.1, -0.1)
            elif self.symmetry.value == "C3v":
                names, values = ("10Dq", "Dσ", "Dτ"), (1.0, 0.0, 0.0)
            else:
                raise ValueError("Unknown symmetry.")
        elif self.block == "f":
            names, values = ("Ea2u", "Et1u", "Et2u"), (-1.8, 0.3, 0.3)
        else:
            raise ValueError("Unknown symmetry.")

        for hamiltonianName, _ in self.hamiltonianNames:
            hamiltonian = BaseItem(self, hamiltonianName)
            for parameterName, value in zip(names, values):
                # Extend the parameterName to include the subshell.
                parameterName = parameterName + f"({self.subshell})"
                HamiltonianParameter(hamiltonian, parameterName, value, None)

        self.enable()


class LigandHybridizationTerm(HamiltonianTerm):
    def __init__(self, parent=None, name="Ligands Hybridization"):
        super().__init__(parent=parent, name=name)

        ligandsName = "L2" if "MLCT" in self.name else "L1"

        names = []
        if self.block == "d":
            if self.symmetry.value == "Oh":
                names = ("Δ", "Veg", "Vt2g", "10Dq")
            elif self.symmetry.value == "D4h":
                names = ("Δ", "Va1g", "Vb1g", "Vb2g", "Veg", "10Dq", "Ds", "Dt")
            # elif self.symmetry.value == "Td":
            #     names = ("Δ", "Ve", "Vt2", "10Dq")
            else:
                raise ValueError("Unknown symmetry.")
        elif self.block == "f":
            if self.symmetry.value == "Oh":
                names = ("Δ", "Va2u", "Vt2u", "Vt1u", "Ea2u", "Et1u", "Et2u")
            else:
                raise ValueError("Unknown symmetry.")

        for hamiltonianName, _ in self.hamiltonianNames:
            hamiltonian = BaseItem(self, hamiltonianName)
            for parameterName in names:
                if parameterName in ("10Dq", "Ds", "Dt", "Ea2u", "Et1u", "Et2u"):
                    suffix = f"({ligandsName})"
                else:
                    suffix = f"({self.subshell},{ligandsName})"
                # Extend the name to include the suffix.
                parameterName = parameterName + suffix
                HamiltonianParameter(hamiltonian, parameterName, 0.0, None)

    def setData(self, column, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole:
            siblings = []
            for sibling in self.siblings():
                if isinstance(sibling, LigandHybridizationTerm):
                    siblings.append(sibling)

            # At the moment only one type of ligands hybridization is possible.
            value = Qt.CheckState(value)
            for sibling in siblings:
                if value == Qt.CheckState.Checked and sibling is not self:
                    sibling.disable()
                    sibling.dataChanged.emit(1)

        return super().setData(column, value, role)


class LmctLigandsHybridizationTerm(LigandHybridizationTerm):
    def __init__(self, parent=None, name=None):
        super().__init__(parent=parent, name=name)


class MlctLigandsHybridizationTerm(LigandHybridizationTerm):
    def __init__(self, parent=None, name=None):
        super().__init__(parent=parent, name=name)


class PdHybridizationTerm(HamiltonianTerm):
    def __init__(self, parent=None, name=None):
        super().__init__(parent=parent, name=name)

        def generateParameters(hamiltonianName, names):
            hamiltonian = BaseItem(self, hamiltonianName)
            for name in names:
                if name in ("ζ(", "G1(1s,"):
                    name = name + "4p)"
                else:
                    name = name + f"({self.subshell},4p)"
                value = 0.0
                scaleFactor = self.scaleFactorFromName(name)
                HamiltonianParameter(hamiltonian, name, value, scaleFactor)

        initialAtomic = ("F2", "G1", "G3", "ζ(")
        finalAtomic = ("F2", "G1", "G3", "G1(1s,", "ζ(")
        if self.symmetry.value == "Td":
            hybridization = ("Δ", "Vt2")
            names = hybridization + initialAtomic
            generateParameters("Initial Hamiltonian", names)
            names = hybridization + finalAtomic
            generateParameters("Final Hamiltonian", names)
        elif self.symmetry.value == "C3v":
            hybridization = ("Δ", "Va1", "Ve(eg)", "Ve(t2g)")
            names = hybridization + initialAtomic
            generateParameters("Initial Hamiltonian", names)
            names = hybridization + finalAtomic
            generateParameters("Final Hamiltonian", names)

    @property
    def replacements(self):
        replacements = super().replacements

        # Read term specific parameters.
        path = resourceAbsolutePath(
            os.path.join("quanty", "parameters", f"{self.element.symbol}.h5")
        )

        # TODO: The parameters should be stored in the final configuration.
        initial_configuration, *_ = self.configurations
        with h5py.File(path, "r") as h5:
            parameters = h5[f"{initial_configuration}/{self.name}"]
            for parameterName, value in parameters.items():
                value = float(value[()])
                replacements[parameterName] = value

        return replacements


class MagneticFieldTerm(HamiltonianTerm):
    def __init__(self, parent=None, name="Magnetic Field"):
        super().__init__(parent=parent, name=name)

        for hamiltonianName, _ in self.hamiltonianNames:
            hamiltonian = BaseItem(self, hamiltonianName)
            for parameterName in ("Bx", "By", "Bz"):
                HamiltonianParameter(hamiltonian, parameterName, 0.0, None)


class ExchangeFieldTerm(HamiltonianTerm):
    def __init__(self, parent=None, name="Exchange Field"):
        super().__init__(parent=parent, name=name)

        for hamiltonianName, _ in self.hamiltonianNames:
            hamiltonian = BaseItem(self, hamiltonianName)
            for parameterName in ("Hx", "Hy", "Hz"):
                HamiltonianParameter(hamiltonian, parameterName, 0.0, None)


class HamiltonianTerms(BaseItem):
    def __init__(self, parent=None, name="Hamiltonian Terms"):
        super().__init__(parent=parent, name=name)

        calculation = self.ancestor
        # For all calculations it should be possible to have at lest the "Atomic" and
        # the "Crystal Field" terms.
        self.atomic = AtomicTerm(parent=self)
        self.crystalField = CrystalFieldTerm(parent=self)

        if calculation.element.valenceBlock == "d":
            # Add ligands hybridization term.
            # TODO: Td is still problematic due to the another set of t2 ligands
            # http://quanty.org/forum/data/2019/metal_3d_to_ligand_hybridization_in_td
            if calculation.symmetry.value in ("Oh", "D4h"):
                # TODO: These exceptions have to be advertised somewhere as the
                # generation of templates must also use them.
                if (
                    calculation.symmetry.value == "Td"
                    and calculation.edge.value == "K (1s)"
                    and calculation.experiment.value == "XAS"
                ):
                    pass
                else:
                    valenceSubshell = calculation.element.valenceSubshell
                    name = f"{valenceSubshell}-Ligands Hybridization (LMCT)"
                    self.lmctLigandsHybridization = LmctLigandsHybridizationTerm(
                        parent=self, name=name
                    )
                    name = f"{valenceSubshell}-Ligands Hybridization (MLCT)"
                    self.mlctLigandsHybridization = MlctLigandsHybridizationTerm(
                        parent=self, name=name
                    )

            # Add pd-hybridization term.
            if calculation.symmetry.value in ("Td", "C3v"):
                if (
                    calculation.edge.value == "K (1s)"
                    and calculation.experiment.value == "XAS"
                ):
                    valenceSubshell = calculation.element.valenceSubshell
                    name = f"{valenceSubshell}-4p Hybridization"
                    self.pdHybridization = PdHybridizationTerm(parent=self, name=name)

        if calculation.element.valenceBlock == "f":
            # Add ligands hybridization term.
            if calculation.symmetry.value in ("Oh",):
                valenceSubshell = calculation.element.valenceSubshell
                name = f"{valenceSubshell}-Ligands Hybridization (LMCT)"
                self.lmctLigandsHybridization = LmctLigandsHybridizationTerm(
                    parent=self, name=name
                )

        # In all calculations it should be possible to add a magnetic and an
        # exchange field, and they should be placed at the end.
        self.magneticField = MagneticFieldTerm(parent=self)
        self.exchangeField = ExchangeFieldTerm(parent=self)

    @property
    def all(self):
        yield from self.children()

    def copyFrom(self, item):
        super().copyFrom(item)
        # Copy the Hamiltonian terms.
        old = self.children()
        new = item.children()
        for o, n in zip(old, new):
            o.copyFrom(n)


class NumberOfStates(IntItem):
    def __init__(self, parent, name="Number of States", value=None):
        super().__init__(parent=parent, name=name)
        self.value = value if value is not None else self.maximum
        self.auto = BoolItem(parent=self, name="Auto", value=True)

    def reset(self):
        self.value = self.maximum

    @property
    def maximum(self):
        """The maximum number of states given the occupation of the valence shell."""
        calculation = self.ancestor

        norbs = OCCUPANCIES[calculation.element.valenceBlock]
        nel = calculation.element.valenceOccupancy

        return int(factorial(norbs) / (factorial(nel) * factorial(norbs - nel)))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value <= 0:
            raise ValueError("There must be at least one state.")
        if value > self.maximum:
            raise ValueError(f"The maximum number of states is {self.maximum}.")
        self._value = value
        self.dataChanged.emit(1)

    def copyFrom(self, item):
        super().copyFrom(item)
        self.auto.copyFrom(item.auto)


class NumberOfConfigurations(IntItem):
    def __init__(self, parent, name="Number of Configurations", value=None):
        super().__init__(parent=parent, name=name)
        self.value = value if value is not None else self.minimum

    def reset(self):
        self.value = self.minimum

    @property
    def minimum(self):
        """The number of configurations used in the calculation."""
        configurations = 1
        for term in self.parent().terms.children():
            if "Ligands" in term.name and term.isEnabled():
                configurations += 1
        return configurations

    @property
    def maximum(self):
        calculation = self.ancestor
        nel = calculation.element.valenceOccupancy
        norbs = OCCUPANCIES[calculation.element.valenceBlock]

        maximum = 1
        for term in self.parent().terms.children():
            if "LMCT" in term.name and term.isEnabled():
                maximum += norbs - nel
            elif "MLCT" in term.name and term.isEnabled():
                maximum += nel
        return maximum

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value <= 0:
            raise ValueError("There must be at least one configuration.")
        if value > self.maximum:
            message = f"The maximum number of configurations is {self.maximum}."
            raise ValueError(message)
        self._value = value
        self.dataChanged.emit(1)


class Hamiltonian(BaseItem):
    def __init__(self, parent):
        super().__init__(parent=parent, name="Hamiltonian")

        self.fk = ScaleFactor(parent=self, name="Fk", value=0.8)
        self.gk = ScaleFactor(parent=self, name="Gk", value=0.8)
        self.zeta = ScaleFactor(parent=self, name="Zeta", value=1.0)

        self.numberOfStates = NumberOfStates(parent=self)

        self.terms = HamiltonianTerms(parent=self)

        name = "Synchronize Parameters"
        self.synchronizeParameters = BoolItem(parent=self, name=name, value=True)

        self.numberOfConfigurations = NumberOfConfigurations(parent=self)
        for term in self.terms.children():
            term.dataChanged.connect(self.numberOfConfigurations.reset)

    def isTermEnabled(self, termType):
        for term in self.terms.children():
            if isinstance(term, termType) and term.isEnabled():
                return True
        return False

    @property
    def replacements(self):
        # The NPsisAuto has to come before NPsis. Using regular expressions with
        # word boundaries doesn't work that well.
        replacements = {
            "NPsisAuto": self.numberOfStates.auto.value,
            "NPsis": self.numberOfStates.value,
            "NConfigurations": self.numberOfConfigurations.value,
        }

        for term in self.terms.children():
            replacements.update(term.replacements)

        return replacements

    def copyFrom(self, item):
        super().copyFrom(item)
        self.fk.copyFrom(item.fk)
        self.gk.copyFrom(item.gk)
        self.zeta.copyFrom(item.zeta)
        self.numberOfStates.copyFrom(item.numberOfStates)
        self.terms.copyFrom(item.terms)
        self.synchronizeParameters.copyFrom(item.synchronizeParameters)
        self.numberOfConfigurations.copyFrom(item.numberOfConfigurations)
