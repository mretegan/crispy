###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""The module provides functionality to run Robert Cowan's programs"""

import argparse
import contextlib
import glob
import logging
import os
import subprocess
import sys

from crispy.quanty.calculation import Configuration, Element

logger = logging.getLogger(__name__)


class Cowan:
    """Calculate the parameters of an electronic configuration using Cowan's programs."""

    RCN_HEADER = "22 -9    2   10  1.0    5.E-06    1.E-09-2   130   1.0  0.65  0.0 0.50 0.0  0.7\n"
    RCN = "runrcn.sh"

    RYDBERG_TO_EV = 13.605693122994  # The value in Cowan's programs is 13.60580.

    NAMES = {
        "d": ("U({0:s},{0:s})", "F2({0:s},{0:s})", "F4({0:s},{0:s})", "ζ({0:s})"),
        "s,d": (
            "U({1:s},{1:s})",
            "F2({1:s},{1:s})",
            "F4({1:s},{1:s})",
            "U({0:s},{1:s})",
            "G2({0:s},{1:s})",
            "ζ({1:s})",
        ),
        "p,d": (
            "U({1:s},{1:s})",
            "F2({1:s},{1:s})",
            "F4({1:s},{1:s})",
            "U({0:s},{1:s})",
            "F2({0:s},{1:s})",
            "G1({0:s},{1:s})",
            "G3({0:s},{1:s})",
            "ζ({1:s})",
            "ζ({0:s})",
        ),
        "f": (
            "U({0:s},{0:s})",
            "F2({0:s},{0:s})",
            "F4({0:s},{0:s})",
            "F6({0:s},{0:s})",
            "ζ({0:s})",
        ),
        "s,f": (
            "U({1:s},{1:s})",
            "F2({1:s},{1:s})",
            "F4({1:s},{1:s})",
            "F6({1:s},{1:s})",
            "U({0:s},{1:s})",
            "G3({0:s},{1:s})",
            "ζ({1:s})",
        ),
        "p,f": (
            "U({1:s},{1:s})",
            "F2({1:s},{1:s})",
            "F4({1:s},{1:s})",
            "F6({1:s},{1:s})",
            "U({0:s},{1:s})",
            "F2({0:s},{1:s})",
            "G2({0:s},{1:s})",
            "G4({0:s},{1:s})",
            "ζ({1:s})",
            "ζ({0:s})",
        ),
        "d,f": (
            "U({1:s},{1:s})",
            "F2({1:s},{1:s})",
            "F4({1:s},{1:s})",
            "F6({1:s},{1:s})",
            "U({0:s},{1:s})",
            "F2({0:s},{1:s})",
            "F4({0:s},{1:s})",
            "G1({0:s},{1:s})",
            "G3({0:s},{1:s})",
            "G5({0:s},{1:s})",
            "ζ({1:s})",
            "ζ({0:s})",
        ),
        "f,f": (
            "U({1:s},{1:s})",
            "F2({1:s},{1:s})",
            "F4({1:s},{1:s})",
            "F6({1:s},{1:s})",
            "U({0:s},{1:s})",
            "F2({0:s},{1:s})",
            "F4({0:s},{1:s})",
            "F6({0:s},{1:s})",
            "G0({0:s},{1:s})",
            "G2({0:s},{1:s})",
            "G4({0:s},{1:s})",
            "G6({0:s},{1:s})",
            "ζ({1:s})",
            "ζ({0:s})",
        ),
    }

    def __init__(self, element, configuration, basename="input"):
        self.element = element
        self.configuration = configuration
        self.basename = basename

        logger.debug(
            "Internal TTMULT binaries are going to be used for the calculation."
        )
        os.environ["TTMULT"] = self.bin

    @property
    def root(self):
        return os.path.join(os.path.dirname(__file__), "parameters", "cowan")

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

        name = ""
        for subshell, occupancy in zip(subshells, occupancies):
            # For 5d elements, the 4f occupied subshells must be included explicitly.
            if "5d" in subshell and "4f" not in subshells:
                subshell = "4f14 5d"
            name += f"{subshell.upper():s}{occupancy:02d} "
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
            logger.critical("The command %s did not finish successfully.", command)
            sys.exit()

    def run_rcn(self):
        """Create the input and run the RCN program."""
        rcn_input = self.RCN_HEADER
        for configuration in (self.configuration,):
            line = (
                f"{self.element.atomicNumber:5d}           "
                f"{configuration.value:8s}         "
                f"{self.normalize_configuration_name(configuration):8s}\n"
            )
            rcn_input += line
        rcn_input += f"{-1:5d}\n"

        filename = f"{self.basename:s}.rcn"
        with open(filename, "w", encoding="utf-8") as fp:
            fp.write(rcn_input)
        self.run(os.path.join(self.scripts, self.RCN))

    def remove_calculation_files(self):
        filenames = sorted(glob.glob(f"{self.basename}*"))
        filenames.append("FTN02")
        for filename in filenames:
            with contextlib.suppress(FileNotFoundError):
                os.remove(filename)

    def parse_rcn_output(self):
        """Parse the output of the RCN program to get the values of the parameters."""

        subshells = self.configuration.subshells
        if self.configuration.hasCore:
            core, valence = subshells
        else:
            core = None
            [valence] = subshells

        def _format(value):
            return round(float(value) * self.RYDBERG_TO_EV, ndigits=4)

        energy = 0.0
        params = {}
        filename = f"{self.basename:s}.rcn_out"
        with open(filename, encoding="utf-8") as fp:
            for line in fp:
                # Parse the spin-orbit coupling parameters (zeta).
                if "BLUME-WATSON" in line:
                    while "SLATER INTEGRALS" not in line:
                        # Zeta for the valence subshell.
                        token = valence.upper()
                        if token in line:
                            params[f"ζ({valence})"] = _format(line[9:20])
                        # Zeta for the core subshell, but not for s-orbitals.
                        if core is not None and "s" not in core:
                            token = core.upper()
                            if token in line:
                                token = core.upper()
                                params[f"ζ({core})"] = _format(line[9:20])
                        line = next(fp)

                # Parse the Slater integrals.
                token = f"( {valence.upper()}, {valence.upper()})"
                if token in line:
                    k = int(line[17:18])
                    if k != 0:
                        params[f"F{k}({valence},{valence})"] = _format(line[18:31])

                if core is not None:
                    token = f"( {core.upper()}, {valence.upper()})"
                    if token in line:
                        k = int(line[17:18])
                        if k != 0:
                            params[f"F{k}({core},{valence})"] = _format(line[18:31])
                        k = int(line[73:74])
                        params[f"G{k}({core},{valence})"] = _format(line[75:88])

                if "ETOT=" in line:
                    energy = _format(line.split()[-1])

        key = ",".join(self.configuration.shells)
        ordered_params = {}
        for name in self.NAMES[key]:
            name = name.format(*self.configuration.subshells)
            ordered_params[name] = 0.0

        ordered_params.update(params)

        return energy, ordered_params

    def get_parameters(self):
        self.run_rcn()
        return self.parse_rcn_output()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--element", default="Fe")
    parser.add_argument("-c", "--configuration", default="3d5")
    parser.add_argument("-l", "--loglevel", default="info")

    args = parser.parse_args()

    logging.basicConfig(
        format="%(levelname)s: %(message)s", level=args.loglevel.upper()
    )

    element = Element()
    element.symbol = args.element
    conf = Configuration(args.configuration)

    cowan = Cowan(element, conf)
    conf.energy, conf.atomic_parameters = cowan.get_parameters()

    if logging.root.level != logging.DEBUG:
        cowan.remove_calculation_files()

    logging.info("%2s %-8s", element.symbol, conf)
    logging.info("E = %-.4f eV", conf.energy)
    for parameter, value in conf.atomic_parameters.items():
        logging.info("%-s = %-.4f eV", parameter, value)


if __name__ == "__main__":
    main()
