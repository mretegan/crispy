# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Classes used to setup Quanty calculations."""

import datetime
import errno
import logging
import os
import re
import subprocess
from functools import lru_cache

from PyQt5.QtCore import QProcess, Qt, pyqtSignal

from crispy import resourceAbsolutePath
from crispy.config import Config
from crispy.gui.items import BaseItem, DoubleItem, IntItem, SelectableItem
from crispy.gui.quanty.axes import Axes
from crispy.gui.quanty.hamiltonian import Hamiltonian
from crispy.gui.quanty.spectra import Spectra
from crispy.quanty import CALCULATIONS, XDB

logger = logging.getLogger(__name__)
settings = Config().read()


SUBSHELLS = {
    "3d": {"atomicNumbers": (21, 30 + 1), "coreElectrons": 18},
    "4d": {"atomicNumbers": (39, 48 + 1), "coreElectrons": 36},
    "4f": {"atomicNumbers": (57, 71 + 1), "coreElectrons": 54},
    "5d": {"atomicNumbers": (72, 80 + 1), "coreElectrons": 68},
    "5f": {"atomicNumbers": (89, 103 + 1), "coreElectrons": 86},
}
OCCUPANCIES = {"s": 2, "p": 6, "d": 10, "f": 14}


class Element(BaseItem):
    def __init__(self, parent=None, name="Element", value=None):
        super().__init__(parent=parent, name=name)
        self.symbol = None
        self.charge = None
        self.value = value

    @property
    def atomicNumber(self):
        return XDB.atomic_number(self.symbol)

    @property
    def valenceSubshell(self):
        """Name of the valence subshell."""
        for subshell, properties in SUBSHELLS.items():
            if self.atomicNumber in range(*properties["atomicNumbers"]):
                return subshell
        return None

    @property
    def valenceBlock(self):
        # pylint: disable=unsubscriptable-object
        """Name of the valence block."""
        return self.valenceSubshell[-1]

    @property
    def valenceOccupancy(self):
        """Occupancy of the valence subshell."""
        assert self.charge is not None, "The charge must be set."

        # Reverse the string holding the charge before changing it to
        # an integer.
        charge = int(self.charge[::-1])

        # Calculate the number of electrons of the ion.
        ion_electrons = self.atomicNumber - charge

        core_electorns = SUBSHELLS[self.valenceSubshell]["coreElectrons"]
        occupancy = ion_electrons - core_electorns
        return occupancy

    @property
    def value(self):
        if self.charge is None:
            return f"{self.symbol}"
        return f"{self.symbol}{self.charge}"

    @value.setter
    def value(self, value):
        if value is None:
            return
        tokens = re.findall(r"(\w{1,2})(\d[+,-])", value)
        if not tokens:
            raise ValueError(f"Invalid element {value}.")
        [tokens] = tokens
        self.symbol, self.charge = tokens


class Configuration:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, value=None):
        self.value = value
        self.energy = None
        self.atomic_parameters = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        PATTERNS = (r"^(\d)(\w)(\d+),(\d)(\w)(\d+)$", r"^(\d)(\w)(\d+)$")

        # Test the configuration string.
        tokens = (token for pattern in PATTERNS for token in re.findall(pattern, value))
        if not tokens:
            raise ValueError("Invalid configuration string.")
        [tokens] = tokens

        if len(tokens) == 3:
            core = None
            valence = tokens
        elif len(tokens) == 6:
            core = tokens[:3]
            valence = tokens[-3:]
        else:
            raise ValueError("Unexpected length of the configuration string.")

        valenceLevel, valenceShell, valenceOccupancy = valence
        valenceLevel = int(valenceLevel)
        valenceOccupancy = int(valenceOccupancy)
        if valenceOccupancy > OCCUPANCIES[valenceShell]:
            raise ValueError("Wrong number of electrons in the valence shell.")

        if core:
            coreLevel, coreShell, coreOccupancy = core
            coreLevel = int(coreLevel)
            coreOccupancy = int(coreOccupancy)
            if coreOccupancy > OCCUPANCIES[coreShell]:
                raise ValueError("Wrong number of electrons in the core shell.")

            self.levels = (coreLevel, valenceLevel)
            self.shells = (coreShell, valenceShell)
            self.occupancies = [coreOccupancy, valenceOccupancy]
        else:
            self.levels = (valenceLevel,)
            self.shells = (valenceShell,)
            self.occupancies = [valenceOccupancy]

        self.subshells = tuple(
            [f"{level}{shell}" for level, shell in zip(self.levels, self.shells)]
        )

        self._value = value

    @property
    def hasCore(self):
        return len(self.subshells) == 2

    @staticmethod
    def countParticles(shell, occupancy):
        """Count the number of particles (electrons) or quasiparticles
        (holes) in a shell."""
        key = f"{shell}{occupancy}"
        if key in ("s0", "s2", "p0", "p6", "d0", "d10", "f0", "f14"):
            particles = "zero"
        elif key in ("s1", "p1", "p5", "d1", "d9", "f1", "f13"):
            particles = "one"
        else:
            particles = "multiple"
        return particles

    @property
    def numberOfCoreParticles(self):
        """Count the number of core particles. Returns None if the electronic
        configuration has no core."""
        if not self.hasCore:
            return None
        core_shell, _ = self.shells
        core_occupancy, _ = self.occupancies
        return self.countParticles(core_shell, core_occupancy)

    @classmethod
    def fromSubshellsAndOccupancies(cls, subshells, occupancies):
        value = ",".join(
            f"{subshell:s}{occupancy:d}"
            for subshell, occupancy in zip(subshells, occupancies)
        )
        return cls(value=value)

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __repr__(self):
        return self.value


class Symmetry(BaseItem):
    def __init__(self, parent=None, name="Symmetry", value=None):
        super().__init__(parent=parent, name=name, value=value)


class Edge(BaseItem):
    def __init__(self, parent=None, name="Edge", value=None):
        super().__init__(parent=parent, name=name, value=value)

    @property
    def coreSubshells(self):
        """Use the name of the edge to determine the names of the core subshells.
        e.g. for K (1s) the function returns ("1s",), while for K-L2,3 (1s2p) it
        returns ("1s", "2p").
        """
        PATTERNS = (r".*\((\d\w)(\d\w)\)", r".*\((\d\w)\)")
        name = self.value
        tokens = (token for pattern in PATTERNS for token in re.findall(pattern, name))
        # Get the elements of the generator.
        [tokens] = tokens
        if not tokens:
            raise ValueError("The name of the edge cannot be parsed.")

        if isinstance(tokens, str):
            tokens = (tokens,)
        return tokens

    @property
    def coreBlocks(self):
        return tuple(subshell[1] for subshell in self.coreSubshells)

    @property
    def coreOccupancies(self):
        return tuple(OCCUPANCIES[coreBlock] for coreBlock in self.coreBlocks)

    @property
    def labels(self):
        """Edge or line labels needed to interrogate xraydb database."""

        CONVERTERS = {
            "Kɑ": "Ka1",
            "Kβ": "Kb1",
            "K": "K",
            "L1": "L1",
            "L2,3": "L3",
            "M1": "M1",
            "M2,3": "M3",
            "M4,5": "M5",
            "N1": "N1",
            "N2,3": "N3",
            "N4,5": "N5",
            "O1": "O1",
            "O2,3": "O3",
            "O4,5": "O5",
        }

        raw, _ = self.value.split()

        names = list()
        separator = "-"
        if separator in raw:
            names.extend(raw.split(separator))
        else:
            names.append(raw)
        # TODO: This needs to be put in a try/except block.
        names = [CONVERTERS[name] for name in names]
        return tuple(names)


class Experiment(BaseItem):
    def __init__(self, parent=None, name="Experiment", value=None):
        super().__init__(parent=parent, name=name, value=value)

    @property
    def isOneStep(self):
        return self.value in ("XAS", "XPS")

    @property
    def isTwoSteps(self):
        return not self.isOneStep

    @property
    def excitesToVacuum(self):
        return self.value in ("XES", "XPS")

    @property
    def isOneDimensional(self):
        return not self.isTwoDimensional

    @property
    def isTwoDimensional(self):
        return self.value in ("RIXS",)

    @property
    def isEmission(self):
        return self.value in ("XES",)


class Temperature(IntItem):
    def __init__(self, parent=None, name="Temperature", value=None):
        super().__init__(parent=parent, name=name, value=value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value < 0:
            raise ValueError("The temperature cannot be negative.")
        self._value = value


class MagneticField(DoubleItem):
    def __init__(self, parent=None, name="Magnetic Field", value=None):
        super().__init__(parent=parent, name=name, value=value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # TODO: Update the magnetic field term.
        self._value = value


class Runner(QProcess):

    outputUpdated = pyqtSignal(str)
    successful = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Merge stdout and stderr channels.
        self.setProcessChannelMode(QProcess.MergedChannels)
        self.startingTime = None
        self.endingTime = None

        self.readyRead.connect(self.updateOutput)
        self.finished.connect(self.checkExitCodes)

        self.output = str()

    def run(self, inputName):
        self.startingTime = datetime.datetime.now()

        # Run Quanty using QProcess.
        self.start(self.executablePath, (inputName,))

        cwd = os.getcwd()
        message = f"Running Quanty {inputName} in the folder {cwd}."
        logger.info(message)

    def checkExitCodes(self, exitCode, exitStatus):
        self.endingTime = datetime.datetime.now()

        successful = False
        if exitStatus == 0 and exitCode == 0:
            message = "Quanty has finished successfully in "
            delta = self.runningTime
            hours, reminder = divmod(delta, 3600)
            minutes, seconds = divmod(reminder, 60)
            seconds = round(seconds, 2)
            if hours > 0:
                message += "{} hours {} minutes and {} seconds.".format(
                    hours, minutes, seconds
                )
            elif minutes > 0:
                message += "{} minutes and {} seconds.".format(minutes, seconds)
            else:
                message += "{} seconds.".format(seconds)
            logger.info(message)
            successful = True
        elif exitStatus == 0 and exitCode == 1:
            message = (
                "Quanty has finished unsuccessfully. "
                "Check the logging window for more details."
            )
            logger.info(message)
        # exitCode is platform dependent; exitStatus is always 1.
        elif exitStatus == 1:
            message = "Quanty was stopped."
            logger.info(message)
        self.successful.emit(successful)

    def updateOutput(self):
        data = self.readAll().data()
        data = data.decode("utf-8").rstrip()
        self.output = self.output + data
        self.outputUpdated.emit(data)

    @property
    def runningTime(self):
        return (self.endingTime - self.startingTime).total_seconds()

    @property
    @lru_cache()
    def executablePath(self):
        path = Config().read().value("Quanty/Path")

        if path is None:
            message = (
                "The path to the Quanty executable is not set. "
                "Please use the preferences menu to set it."
            )
            raise RuntimeError(message)

        # Test the executable.
        with open(os.devnull, "w") as fp:
            try:
                subprocess.call(path, stdout=fp, stderr=fp)
            except OSError as e:
                if e.errno == errno.ENOENT:
                    message = (
                        "The Quanty executable is not working properly. "
                        "Is the PATH set correctly?"
                    )
                    raise RuntimeError(message)
                raise e
        return path


# TODO: Could this class also inherit from the Runner() class?
class Calculation(SelectableItem):
    # pylint: disable=too-many-instance-attributes, too-many-arguments, too-many-public-methods

    titleChanged = pyqtSignal(str)

    def __init__(
        self,
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="RIXS",
        edge="L2,3-M4,5 (2p3d)",
        hamiltonian=True,
        parent=None,
    ):

        super().__init__(parent=parent, name="Calculation")

        # Set the very special ancestor, in this case self.
        self._ancestor = self

        # Validate the keyword arguments. This is best done this way; using properties
        # it gets rather convoluted.
        self._symbols = list()
        for subshell in CALCULATIONS.keys():
            self._symbols.extend(CALCULATIONS[subshell]["symbols"])
        self._symbols = tuple(sorted(self._symbols))

        if symbol not in self.symbols:
            symbol = self._symbols[0]

        # Get the subshell.
        subshell = None
        for subshell in CALCULATIONS.keys():
            if symbol in CALCULATIONS[subshell]["symbols"]:
                break

        symbols = CALCULATIONS[subshell]["symbols"]
        experiments = CALCULATIONS[subshell]["experiments"]

        self._charges = tuple(symbols[symbol]["charges"])
        if charge not in self._charges:
            charge = self._charges[0]

        self._experiments = tuple(experiments)
        if experiment not in self._experiments:
            experiment = self._experiments[0]

        self._symmetries = tuple(experiments[experiment]["symmetries"])
        if symmetry not in self._symmetries:
            symmetry = self._symmetries[0]

        self._edges = tuple(experiments[experiment]["edges"])
        if edge not in self._edges:
            edge = self._edges[0]

        self.element = Element(parent=self, value=f"{symbol}{charge}")
        self.symmetry = Symmetry(parent=self, value=symmetry)
        self.experiment = Experiment(parent=self, value=experiment)
        self.edge = Edge(parent=self, value=edge)

        self.temperature = Temperature(parent=self, value=10)
        self.magneticField = MagneticField(parent=self, value=0)

        self.axes = Axes(parent=self)

        self.spectra = Spectra(parent=self)
        # This flag is needed because the class is also used to generate Hamiltonian
        # parameters, which are needed to create the Hamiltonian object in the
        # first place. A bit of chicken and egg problem.
        if hamiltonian:
            self.hamiltonian = Hamiltonian(parent=self)

        # Set the name of the calculation.
        subshells = "".join(self.edge.coreSubshells)
        element = self.element.value
        symmetry = self.symmetry.value
        experiment = self.experiment.value
        self._value = f"{element}_{symmetry}_{experiment}_{subshells}"

        # Instantiate the runner used to execute Quanty.
        self.runner = Runner()
        self.runner.successful.connect(self.process)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.dataChanged.emit(0)
        self.titleChanged.emit(value)

    def data(self, column, role=Qt.DisplayRole):
        if role in (Qt.EditRole, Qt.DisplayRole, Qt.UserRole):
            column = 0 if column == 1 else 1
        return super().data(column, role)

    def setData(self, column, value, role=Qt.EditRole):
        if role in (Qt.EditRole, Qt.UserRole):
            column = 0 if column == 1 else 1
        return super().setData(column, value, role)

    def flags(self, column):
        return (
            Qt.ItemIsEnabled
            | Qt.ItemIsSelectable
            | Qt.ItemIsEditable
            | Qt.ItemIsUserCheckable
        )

    @property
    def symbols(self):
        return self._symbols

    @property
    def charges(self):
        return self._charges

    @property
    def symmetries(self):
        return self._symmetries

    @property
    def experiments(self):
        return self._experiments

    @property
    def edges(self):
        return self._edges

    @property
    def templateName(self):
        valenceSubshell = self.element.valenceSubshell
        symmetry = self.symmetry.value
        experiment = self.experiment.value
        subshells = "".join(self.edge.coreSubshells)
        return f"{valenceSubshell}_{symmetry}_{experiment}_{subshells}.lua"

    @property
    @lru_cache()
    def configurations(self):
        """Determine the electronic configurations involved in a calculation."""
        valenceSubshell = self.element.valenceSubshell
        valenceOccupancy = self.element.valenceOccupancy

        configurations = list()

        # Initial configuration.
        initialConfiguration = Configuration.fromSubshellsAndOccupancies(
            subshells=(valenceSubshell,), occupancies=(valenceOccupancy,),
        )
        configurations.append(initialConfiguration)

        # Final and in some cases intermediate configurations.
        if self.experiment.isOneStep:
            if not self.experiment.excitesToVacuum:
                valenceOccupancy += 1
            (coreSubshell,) = self.edge.coreSubshells
            (coreOccupancy,) = self.edge.coreOccupancies

            coreOccupancy -= 1

            finalConfiguration = Configuration.fromSubshellsAndOccupancies(
                subshells=(coreSubshell, valenceSubshell),
                occupancies=(coreOccupancy, valenceOccupancy),
            )
            configurations.append(finalConfiguration)
        else:
            if not self.experiment.excitesToVacuum:
                valenceOccupancy += 1

            core1Subshell, core2Subshell = self.edge.coreSubshells
            core1Occupancy, core2Occupancy = self.edge.coreOccupancies

            core1Occupancy -= 1
            core2Occupancy -= 1

            intermediateConfiguration = Configuration.fromSubshellsAndOccupancies(
                subshells=(core1Subshell, valenceSubshell),
                occupancies=(core1Occupancy, valenceOccupancy),
            )
            configurations.append(intermediateConfiguration)

            if core2Subshell == valenceSubshell:
                finalConfiguration = Configuration.fromSubshellsAndOccupancies(
                    subshells=(valenceSubshell,), occupancies=(valenceOccupancy - 1,),
                )
            else:
                finalConfiguration = Configuration.fromSubshellsAndOccupancies(
                    subshells=(core2Subshell, valenceSubshell),
                    occupancies=(core2Occupancy, valenceOccupancy),
                )
            configurations.append(finalConfiguration)

        return configurations

    @property
    def replacements(self):
        """Replacements dictionary used to fill the calculation template. The
        construction of more complex items is delegated to the respective object.
        """
        replacements = dict()

        # Values defined in another places.
        replacements["Verbosity"] = settings.value("Quanty/Verbosity")
        replacements["DenseBorder"] = settings.value("Quanty/DenseBorder")

        subshell = self.element.valenceSubshell
        occupancy = self.element.valenceOccupancy

        replacements[f"NElectrons_{subshell}"] = occupancy
        replacements["Temperature"] = self.temperature.value
        replacements["Prefix"] = self.value

        replacements.update(self.axes.xaxis.replacements)
        if self.experiment.isTwoDimensional:
            replacements.update(self.axes.yaxis.replacements)

        replacements.update(self.spectra.replacements)
        replacements.update(self.hamiltonian.replacements)

        return replacements

    @property
    def input(self):
        path = resourceAbsolutePath(
            os.path.join("quanty", "templates", f"{self.templateName}")
        )
        try:
            with open(path) as fp:
                template = fp.read()
        except FileNotFoundError as e:
            message = f"Could not find the template file {self.templateName}."
            logger.error(message)
            raise e

        for pattern, replacement in self.replacements.items():
            # True/False in Lua are lowercase.
            if isinstance(replacement, bool):
                replacement = str(replacement).lower()
            else:
                replacement = str(replacement)
            template = template.replace(f"${pattern}", str(replacement))

        return template

    @property
    def inputName(self):
        return f"{self.value}.lua"

    @property
    def output(self):
        return self.runner.output

    @property
    def summary(self):
        return f"Summary for {self.value}"

    def saveInput(self):
        # TODO: Is this too hidden?
        os.chdir(settings.value("CurrentPath"))
        with open(self.inputName, "w") as fp:
            fp.write(self.input)

    def run(self):
        # Don't crash if something when wrong when saving the input file.
        try:
            self.saveInput()
        except FileNotFoundError:
            return
        self.runner.run(self.inputName)

    def process(self, successful):
        if not successful:
            return
        # TODO: Check if loading the spectra was successful.
        self.spectra.load()

    def stop(self):
        self.runner.kill()

    def clean(self):
        os.remove(f"{self.value}.lua")

    def copyFrom(self, item):
        super().copyFrom(item)
        self.temperature.copyFrom(item.temperature)
        self.magneticField.copyFrom(item.magneticField)
        self.axes.copyFrom(item.axes)
        self.spectra.copyFrom(item.spectra)
        self.hamiltonian.copyFrom(item.hamiltonian)


def main():
    parameters = (("XAS", "K (1s)"), ("RIXS", "L2,3-M4,5 (2p3d)"), ("XES", "Kɑ (1s2p)"))
    for experiment, edge in parameters:
        calculation = Calculation(symbol="Fe", experiment=experiment, edge=edge)
        print(calculation)
        print(calculation.xaxis.__dict__)
        try:
            print(calculation.yaxis.__dict__)
        except AttributeError:
            pass


if __name__ == "__main__":
    main()
