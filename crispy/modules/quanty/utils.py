# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This module provides functions that help to generate the parameters of the atomic configurations."""

__authors__ = ["Marius Retegan"]
__license__ = "MIT"
__date__ = "11/05/2019"

import glob
import json
import logging
import os
import re
import subprocess
import sys

import xraydb

from crispy.utils.odict import odict

xdb = xraydb.XrayDB()


SUBSHELLS = {
    "3d": {"atomic_numbers_range": (21, 30 + 1), "core_electrons": 18},
    "4d": {"atomic_numbers_range": (39, 48 + 1), "core_electrons": 36},
    "4f": {"atomic_numbers_range": (57, 71 + 1), "core_electrons": 54},
    "5d": {"atomic_numbers_range": (72, 80 + 1), "core_electrons": 68},
    "5f": {"atomic_numbers_range": (89, 103 + 1), "core_electrons": 86},
}

OCCUPANCIES = {"s": 2, "p": 6, "d": 10, "f": 14}


class Element:
    def __init__(self, symbol, charge=None):
        self.symbol = symbol
        self.charge = charge

    @property
    def atomic_number(self):
        return xdb.atomic_number(self.symbol)

    @property
    def valence_subshell(self):
        """Name of the valence subshell"""
        atomic_number = self.atomic_number
        for subshell, prop in SUBSHELLS.items():
            if atomic_number in range(*prop["atomic_numbers_range"]):
                return subshell
        return None

    @property
    def valence_occupancy(self):
        """Occupancy of the valence subshell"""
        assert self.charge is not None, "The charge must be set."

        # Reverse the string holding the charge before changing it to
        # an integer.
        charge = int(self.charge[::-1])

        # Calculate the number of electrons of the ion.
        ion_electrons = xdb.atomic_number(self.symbol) - charge

        core_electorns = SUBSHELLS[self.valence_subshell]["core_electrons"]
        occupancy = ion_electrons - core_electorns
        return occupancy

    def __repr__(self):
        if self.charge is None:
            return "{:s}".format(self.symbol)
        return "{:s}{:s}".format(self.symbol, self.charge)


class Configuration:
    def __init__(self, name):
        self.name = name
        self.energy = None
        self.atomic_parameters = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        PATTERNS = (r"^(\d)(\w)(\d+),(\d)(\w)(\d+)$", r"^(\d)(\w)(\d+)$")

        # Test the configuration string.
        tokens = [token for pattern in PATTERNS for token in re.findall(pattern, value)]
        if not tokens:
            raise ValueError("Invalid configuration string.")
        [tokens] = tokens

        if len(tokens) == 3:
            core = None
            valence = tokens
        elif len(tokens) == 6:
            core = tokens[:3]
            valence = tokens[-3:]

        valence_level, valence_shell, valence_occupancy = valence
        valence_level = int(valence_level)
        valence_occupancy = int(valence_occupancy)
        if valence_occupancy > OCCUPANCIES[valence_shell]:
            raise ValueError(
                "Wrong number of electrons in the valence shell: {}".format(value)
            )

        if core:
            core_level, core_shell, core_occupancy = core
            core_level = int(core_level)
            core_occupancy = int(core_occupancy)
            if core_occupancy > OCCUPANCIES[core_shell]:
                raise ValueError(
                    "Wrong number of electrons in the core shell: {}".format(value)
                )

            self.levels = [core_level, valence_level]
            self.shells = [core_shell, valence_shell]
            self.occupancies = [core_occupancy, valence_occupancy]
        else:
            self.levels = [valence_level]
            self.shells = [valence_shell]
            self.occupancies = [valence_occupancy]

        self.subshells = [
            str(level) + shell for level, shell in zip(self.levels, self.shells)
        ]

        self._name = value

    @classmethod
    def from_subshells_and_occupancies(cls, subshells, occupancies):
        name = ",".join(
            "{:s}{:d}".format(subshell, occupancy)
            for subshell, occupancy in zip(subshells, occupancies)
        )
        return cls(name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return self.name


class Symmetry:
    def __init__(self, name):
        self.name = name


class Edge:
    def __init__(self, name=None):
        self.name = name

    @property
    def core_subshells(self):
        """Use the name of the edge to determine the names of the core subshells.
        e.g. for K (1s) the function returns ("1s",), while for K-L2,3 (1s2p) it returns ("1s", "2p").
        """
        pattern = re.compile(r"(.*) \((.*)\)")
        tokens = re.match(pattern, self.name).group(2)
        if len(tokens) == 2:
            subshells = (tokens,)
        elif len(tokens) == 4:
            subshells = (tokens[:2], tokens[2:])
        else:
            raise ValueError("The name of the edge cannot be parsed.")
        return subshells

    @property
    def core_occupancies(self):
        core_occupancies = list()
        for shell, occupancy in OCCUPANCIES.items():
            for core_subshell in self.core_subshells:
                if shell in core_subshell:
                    core_occupancies.append(occupancy)
        return core_occupancies

    def __repr__(self):
        return "{:s}".format(self.name)


class Experiment:
    def __init__(self, name=None):
        self.name = name

    @property
    def one_step_process(self):
        return self.name in ("XAS", "XPS")

    @property
    def excites_to_vacuum(self):
        return self.name in ("XES", "XPS")

    def __repr__(self):
        return "{:s}".format(self.name)


class Cowan:
    """Calculate the parameters of an electronic configuration using Cowan's programs."""

    RCN_HEADER = "22 -9    2   10  1.0    5.E-06    1.E-09-2   130   1.0  0.65  0.0 0.50 0.0  0.7\n"
    RCN2_HEADER = """G5INP     000                 00        00000000  9999999999 .00       1229
        -1
    """
    RCN = "runrcn.sh"
    RCN2 = "runrcn2.sh"
    RCG = "runrcg.sh"

    RYDBER_TO_EV = 13.605693122994

    def __init__(self, element, configuration, basename="input"):
        self.element = element
        self.configuration = configuration
        self.basename = basename

        if "TTMULT" not in os.environ:
            logging.debug(
                "The $TTMULT environment variable is not set; will use internal binaries."
            )
            os.environ["TTMULT"] = self.bin

    @property
    def root(self):
        return os.path.join(os.path.dirname(__file__), "cowan")

    @property
    def bin(self):
        return os.path.join(self.root, "bin", sys.platform)

    @property
    def scripts(self):
        return os.path.join(self.root, "scripts")

    @staticmethod
    def normalize_configuration_name(configuration):
        """Configuration name expected by Cowan's programs."""
        occupancies = configuration.occupancies
        subshells = configuration.subshells

        name = str()
        for subshell, occupancy in zip(subshells, occupancies):
            # For some elements, some of the occupied subshells must be included explicitly.
            if "4f" in subshell and "3d" not in configuration.name:
                subshell = "3d10 4f"
            elif "5d" in subshell and "4f" not in subshells:
                subshell = "4f14 5d"
            name += "{0:s}{1:02d} ".format(subshell.upper(), occupancy)
        return name.rstrip()

    def run(self, command):
        """Run the "command"; discard stdout and stderr, but check the exit status."""
        try:
            subprocess.run(
                (command, self.basename),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        except subprocess.CalledProcessError:
            logging.critical("The command %s did not finish successfully.", command)
            sys.exit()

    def rcn(self):
        """Create the input and run the RCN program."""
        rcn_input = self.RCN_HEADER
        for configuration in (self.configuration,):
            line = "{0:5d}           {1:8s}         {2:8s}\n".format(
                self.element.atomic_number,
                configuration.name,
                self.normalize_configuration_name(configuration),
            )
            rcn_input += line
        rcn_input += "{:5d}\n".format(-1)

        filename = "{:s}.rcn".format(self.basename)
        with open(filename, "w") as fp:
            fp.write(rcn_input)
        self.run(os.path.join(self.scripts, self.RCN))

    def rcn2(self):
        """Create the input and run the RCN2 program."""
        filename = "{:s}.rcn2".format(self.basename)
        with open(filename, "w") as fp:
            fp.write(self.RCN2_HEADER)
        self.run(os.path.join(self.scripts, self.RCN2))

    def rcg(self):
        """Create the input and run the RCG program."""
        filename = "{:s}.rcg".format(self.basename)
        # The input file has ".orig" appended to the end.
        # os.rename(filename + ".orig", filename)
        with open(filename, "r") as fp:
            lines = fp.readlines()
        with open(filename, "w") as fp:
            for line in lines:
                fp.write(re.sub(r"80998080", r"99999999", line))
        self.run(os.path.join(self.scripts, self.RCG))

    def remove_calculation_files(self):
        filenames = sorted(glob.glob(self.basename + "*"))
        filenames.append("FTN02")
        for filename in filenames:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

    def get_parameters(self):  # noqa
        self.rcn()
        self.rcn2()
        self.rcg()

        subshells = self.configuration.subshells

        # Parse the output of the RCG program to get the names of the parameters.
        tmp = list()
        filename = "{:s}.rcg_out".format(self.basename)
        with open(filename) as fp:
            for line in fp:
                if "PARAMETER VALUES IN" in line:
                    # Skip two lines
                    for _ in range(2):
                        line = next(fp)
                    while line.split():
                        tokens = re.split(r"\s{2,}", line.strip())
                        tmp.extend(tokens)
                        line = next(fp)

        # Process the names.
        names = list()
        for name in tmp:
            if name.startswith("F") or name.startswith("G"):
                start = name[:2]
                idx1 = int(name[3]) - 1
                idx2 = int(name[4]) - 1
                subshell1 = subshells[idx1]
                subshell2 = subshells[idx2]
                name = "{}({},{})".format(start, subshell1, subshell2)
            elif name.startswith("ZETA"):
                idx = int(name.split()[-1]) - 1
                subshell = subshells[idx]
                name = "ζ({})".format(subshell)
            else:
                continue
            names.append(name)

        # Parse the output of the RCN program to get the values of the parameters.
        values = list()
        filename = "{:s}.rcn_out".format(self.basename)
        with open(filename) as fp:
            for line in fp:
                if "ETOT=" in line:
                    energy = float(line.split()[-1]) * self.RYDBER_TO_EV
                    line = next(fp)

                    # Skip a few empty lines.
                    while not line.split():
                        line = next(fp)

                    # Parse the atomic parameters.
                    tokens = map(float, line.split()[4::2])
                    values.extend(tokens)

                    # In some cases the parameters also span the next two lines.
                    for _ in range(2):
                        line = next(fp)
                        tokens = line.split()
                        if tokens:
                            values.extend(map(float, tokens[::2]))

        parameters = odict()
        for name, value in zip(names, values):
            parameters[name] = value

        # Don't remove files if the logging level is set to debug.
        if logging.root.level != logging.DEBUG:
            self.remove_calculation_files()

        return energy, parameters


class Calculations:
    def __init__(self, filename):
        with open(filename) as fp:
            self.data = json.load(fp, object_hook=odict)

    def unique_configurations(self, element):
        """Determine the unique electronic configurations of an element."""
        valence_subshell = element.valence_subshell

        charges = self.data[valence_subshell]["elements"][element.symbol]
        experiments = self.data[valence_subshell]["experiments"]

        configurations = list()
        for charge in charges:
            element.charge = charge
            for experiment in experiments:
                edges = experiments[experiment]["edges"]
                for edge in edges:
                    configurations.extend(
                        self.calculation_configurations(
                            element, Experiment(experiment), Edge(edge)
                        )
                    )
        return sorted(list(set(configurations)))

    def get_all_elements(self):
        elements = list()
        for subshell in self.data:
            elements.extend(self.data[subshell]["elements"].keys())
        return elements

    @staticmethod
    def calculation_configurations(element, experiment, edge):  # noqa
        """Determine the electronic configuration involved in a calculation."""
        valence_subshell = element.valence_subshell
        valence_occupancy = element.valence_occupancy

        core_subshells = edge.core_subshells
        core_occupancies = edge.core_occupancies

        configurations = list()

        # Initial configuration.
        initial_configuration = Configuration.from_subshells_and_occupancies(
            (valence_subshell,), (valence_occupancy,)
        )
        configurations.append(initial_configuration)

        # Final and in some cases intermediate configurations.
        if experiment.one_step_process:
            if not experiment.excites_to_vacuum:
                valence_occupancy += 1

            (core_subshell,) = core_subshells
            (core_occupancy,) = core_occupancies

            core_occupancy -= 1

            final_configuration = Configuration.from_subshells_and_occupancies(
                (core_subshell, valence_subshell), (core_occupancy, valence_occupancy)
            )

            configurations.append(final_configuration)
        else:
            if not experiment.excites_to_vacuum:
                valence_occupancy += 1

            core1_subshell, core2_subshell = core_subshells
            core1_occupancy, core2_occupancy = core_occupancies

            core1_occupancy -= 1
            core2_occupancy -= 1

            intermediate_configuration = Configuration.from_subshells_and_occupancies(
                (core1_subshell, valence_subshell), (core1_occupancy, valence_occupancy)
            )
            configurations.append(intermediate_configuration)

            if core2_subshell == valence_subshell:
                final_configuration = Configuration.from_subshells_and_occupancies(
                    (valence_subshell,), (valence_occupancy - 1,)
                )
            else:
                final_configuration = Configuration.from_subshells_and_occupancies(
                    (core2_subshell, valence_subshell),
                    (core2_occupancy, valence_occupancy),
                )
            configurations.append(final_configuration)

        logging.debug((element, experiment, edge, configurations))

        return configurations
