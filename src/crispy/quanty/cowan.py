"""The module provides functionality to run Robert Cowan's programs"""

import argparse
import contextlib
import glob
import logging
import os
import re
import subprocess
import sys

from crispy.quanty.calculation import Configuration, Element

logger = logging.getLogger(__name__)


class Cowan:
    """Calculate atomic parameters of an electronic configuration."""

    RCN_HEADER = (
        "22 -9    2   10  1.0    5.E-06    1.E-09-2   130   1.0  0.65  "
        "0.0 0.50 0.0  0.7\n"
    )
    RCN = "runrcn.sh"
    RCN2 = "runrcn2.sh"
    RCN2_HEADER = (
        "G5INP     000                 00        00000000 39999999999 "
        ".00       1229\n        -1\n"
    )

    RYDBERG_TO_EV = 13.605693122994  # The value in Cowan's programs is 13.60580.

    NAMES = {  # noqa: RUF012
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
        "d,d": (
            "U({1:s},{1:s})",
            "F2({1:s},{1:s})",
            "F4({1:s},{1:s})",
            "U({0:s},{1:s})",
            "F2({0:s},{1:s})",
            "F4({0:s},{1:s})",
            "G0({0:s},{1:s})",
            "G2({0:s},{1:s})",
            "G4({0:s},{1:s})",
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

    @property
    def root(self):
        return os.path.join(os.path.dirname(__file__), "parameters", "cowan")

    @property
    def bin(self):
        return os.path.join(self.root, "bin")

    @property
    def scripts(self):
        return os.path.join(self.root, "scripts")

    @staticmethod
    def normalize_configuration_name(configuration):
        """Configuration name expected by Cowan's programs."""
        occupancies = configuration.occupancies
        subshells = configuration.subshells

        name = ""
        for subshell, occupancy in zip(subshells, occupancies, strict=False):
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

    def require_binary(self, name):
        """Exit with a clear error if the Cowan "name" binary is missing."""
        path = os.path.join(self.bin, name)
        if not os.path.isfile(path):
            logger.critical(
                "The %s binary was not found at %s; build it with the Makefile "
                "in %s.",
                name,
                path,
                self.root,
            )
            sys.exit()

    def run_rcn(self):
        """Create the input and run the RCN program."""
        self.require_binary("rcn")

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

    def configuration_line(self, label, occupancies):
        """Return one RCN configuration line.

        The occupancy block must start at column 34, so the label fills
        columns 6 to 33.
        """
        return f"{self.element.atomicNumber:>5d}{label:<28s}{occupancies}\n"

    def run_rcn2(self):
        """Run rcn and rcn2 for the three p-d hybridization configurations."""
        self.require_binary("rcn")
        self.require_binary("rcn2")

        symbol = self.element.symbol
        d = self.configuration.subshells[-1]
        m = self.configuration.occupancies[-1]
        p = f"{int(d[0]) + 1}p"
        d_upper, p_upper = d.upper(), p.upper()

        # 5d elements need the filled 4f shell declared explicitly; rcn does not
        # add it automatically (see normalize_configuration_name).
        inner = "4F14 " if d == "5d" else ""

        # Ground n d^m, then the 1s^1 n d^(m+1) (1s -> nd quadrupole) and
        # 1s^1 n d^m (n+1)p^1 (1s -> (n+1)p dipole) final states.
        ground = f"1S02 {inner}{d_upper}{m:02d} {p_upper}00"
        quadrupole = f"1S01 {inner}{d_upper}{m + 1:02d} {p_upper}00"
        dipole = f"1S01 {inner}{d_upper}{m:02d} {p_upper}01"
        configurations = (
            (f"     {symbol} {d}{m}", ground),
            (f"     {symbol} 1s1 {d}{m + 1}", quadrupole),
            (f"     {symbol} 1s1 {d}{m} {p}1", dipole),
        )
        rcn_input = self.RCN_HEADER
        for label, occupancies in configurations:
            rcn_input += self.configuration_line(label, occupancies)
        rcn_input += f"{-1:5d}\n"

        with open(f"{self.basename:s}.rcn", "w", encoding="utf-8") as fp:
            fp.write(rcn_input)
        self.run(os.path.join(self.scripts, self.RCN))

        with open(f"{self.basename:s}.rcn2", "w", encoding="utf-8") as fp:
            fp.write(self.RCN2_HEADER)
        self.run(os.path.join(self.scripts, self.RCN2))

    def parse_rcn2_output(self):
        """Return the dipole P1 and quadrupole P2 prefactors from the rcn2 output.

        ( 1S//R1// (n+1)P) is the dipolar prefactor and ( 1S//R2// nD) the
        quadrupolar one. Both enter the cross-section squared, so the magnitudes
        are kept.
        """
        d = self.configuration.subshells[-1]
        p = f"{int(d[0]) + 1}p"
        with open(f"{self.basename:s}.rcn2_out", encoding="utf-8") as fp:
            text = fp.read()

        p1 = re.search(rf"\( 1S//R1// {p.upper()}\)=\s*(-?\d+\.\d+)", text)
        p2 = re.search(rf"\( 1S//R2// {d.upper()}\)=\s*(-?\d+\.\d+)", text)
        if p1 is None or p2 is None:
            return None
        return {
            f"P1(1s,{p})": abs(float(p1.group(1))),
            f"P2(1s,{d})": abs(float(p2.group(1))),
        }

    def get_hybridization_parameters(self):
        """Return the p-d hybridization prefactors P1 and P2, or None.

        They are defined only for a ground n d^m (0 <= m <= 9) configuration of a
        transition metal.
        """
        configuration = self.configuration
        if configuration.hasCore or not configuration.subshells[-1].endswith("d"):
            return None
        if not 0 <= configuration.occupancies[-1] <= 9:
            return None
        self.run_rcn2()
        return self.parse_rcn2_output()

    def _to_ev(self, value):
        return round(float(value) * self.RYDBERG_TO_EV, ndigits=4)

    def run_rcn_configuration(self, label, occupancies):
        """Run rcn for a single configuration and return the output text."""
        self.require_binary("rcn")
        rcn_input = self.RCN_HEADER
        rcn_input += self.configuration_line(label, occupancies)
        rcn_input += f"{-1:5d}\n"
        with open(f"{self.basename:s}.rcn", "w", encoding="utf-8") as fp:
            fp.write(rcn_input)
        self.run(os.path.join(self.scripts, self.RCN))
        with open(f"{self.basename:s}.rcn_out", encoding="utf-8") as fp:
            return fp.read()

    def parse_dp_parameters(self, text, d, p, core):
        """Parse the n d - (n+1)p Slater integrals and (n+1)p spin-orbit.

        Also reads G1(1s,(n+1)p) when the configuration has a 1s core hole.
        """
        d_upper, p_upper = d.upper(), p.upper()
        params = {}
        in_zeta = False
        for line in text.splitlines():
            if "BLUME-WATSON" in line:
                in_zeta = True
            elif "SLATER INTEGRALS" in line:
                in_zeta = False
            if in_zeta and line.lstrip().startswith(f"{p_upper} "):
                params[f"ζ({p})"] = self._to_ev(line[9:20])
            if f"( {d_upper}, {p_upper})" in line:
                kf, kg = int(line[17:18]), int(line[73:74])
                if kf != 0:
                    params[f"F{kf}({d},{p})"] = self._to_ev(line[18:31])
                params[f"G{kg}({d},{p})"] = self._to_ev(line[75:88])
            if core and f"( 1S, {p_upper})" in line:
                kg = int(line[73:74])
                params[f"G{kg}(1s,{p})"] = self._to_ev(line[75:88])
        return params

    def get_hybridization_atomic_parameters(self):
        """Return the initial- and final-state n d - (n+1)p atomic parameters.

        Final values come from 1s^1 n d^m (n+1)p^1 and initial values from
        n d^(m-1) (n+1)p^1 (absent for m == 0). Returns None unless the
        configuration is a ground n d^m (0 <= m <= 9) state of a transition metal.
        """
        configuration = self.configuration
        d = configuration.subshells[-1]
        if configuration.hasCore or not d.endswith("d"):
            return None
        m = configuration.occupancies[-1]
        if not 0 <= m <= 9:
            return None

        symbol = self.element.symbol
        p = f"{int(d[0]) + 1}p"
        d_upper, p_upper = d.upper(), p.upper()
        inner = "4F14 " if d == "5d" else ""

        result = {}
        # Final state: 1s^1 n d^m (n+1)p^1.
        occupancies = f"1S01 {inner}{d_upper}{m:02d} {p_upper}01"
        label = f"     {symbol} 1s1 {d}{m} {p}1"
        text = self.run_rcn_configuration(label, occupancies)
        result["Final Hamiltonian"] = self.parse_dp_parameters(text, d, p, core=True)
        # Initial state: n d^(m-1) (n+1)p^1 (needs at least one d electron).
        if m >= 1:
            occupancies = f"1S02 {inner}{d_upper}{m - 1:02d} {p_upper}01"
            label = f"     {symbol} {d}{m - 1} {p}1"
            text = self.run_rcn_configuration(label, occupancies)
            params = self.parse_dp_parameters(text, d, p, core=False)
            result["Initial Hamiltonian"] = params
        return result


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
