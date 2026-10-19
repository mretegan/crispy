"""The module provides functionality to run Robert Cowan's programs"""

import argparse
import contextlib
import glob
import itertools
import logging
import os
import re
import subprocess
import sys
from types import SimpleNamespace

from crispy.quanty.calculation import OCCUPANCIES, Element

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

    ANGULAR_MOMENTA = {"s": 0, "p": 1, "d": 2, "f": 3}  # noqa: RUF012

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
    def subshell_pairs(subshells):
        """Return the pairs of subshells that have Slater integrals.

        The first subshell of a configuration with more than one subshell is the
        core subshell, which has no Slater integrals with itself.
        """
        if len(subshells) == 1:
            return [(subshells[0], subshells[0])]
        core, *valence = subshells
        pairs = list(itertools.combinations_with_replacement(valence, 2))
        pairs += [(core, subshell) for subshell in valence]
        return pairs

    def parameter_names(self, subshells):
        """Return the ordered names of the atomic parameters."""
        names = []
        for a, b in self.subshell_pairs(subshells):
            la, lb = self.ANGULAR_MOMENTA[a[-1]], self.ANGULAR_MOMENTA[b[-1]]
            names.append(f"U({a},{b})")
            names += [f"F{k}({a},{b})" for k in range(2, 2 * min(la, lb) + 1, 2)]
            if a != b:
                names += [f"G{k}({a},{b})" for k in range(abs(la - lb), la + lb + 1, 2)]
        names += [f"ζ({s})" for s in reversed(subshells) if not s.endswith("s")]
        return names

    def normalize_configuration_name(self, configuration):
        """Configuration name expected by Cowan's programs."""
        occupancies = configuration.occupancies
        subshells = configuration.subshells

        # rcn does not add f subshells. From La (5d) and Ac (6d), fill the f subshell
        # below the d subshell if the configuration does not give it.
        full_f_subshells = {"5d": ("4f", 57), "6d": ("5f", 89)}

        name = ""
        for subshell, occupancy in zip(subshells, occupancies, strict=False):
            if subshell in full_f_subshells:
                f_subshell, atomic_number = full_f_subshells[subshell]
                if (
                    f_subshell not in subshells
                    and self.element.atomicNumber >= atomic_number
                ):
                    subshell = f"{f_subshell}14 {subshell}"
            name += f"{subshell.upper():s}{occupancy:02d} "
        return name.rstrip()

    def run(self, command):
        """Run the "command"; show its output only if the exit status is not zero."""
        try:
            subprocess.run(
                (command, self.basename),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as error:
            logger.critical(
                "The command %s did not finish successfully:\n%s",
                command,
                error.output.rstrip(),
            )
            sys.exit(1)
        except OSError as error:
            # FileNotFoundError if the wrapper script is missing, PermissionError
            # if it is not executable; neither is a CalledProcessError.
            logger.critical("The command %s could not be run: %s.", command, error)
            sys.exit(1)

    def require_binary(self, name):
        """Exit with a clear error if the Cowan "name" binary is missing."""
        path = os.path.join(self.bin, name)
        if not os.path.isfile(path):
            logger.critical(
                "The %s binary was not found at %s; build it with the Makefile in %s.",
                name,
                path,
                self.root,
            )
            sys.exit(1)

    def run_rcn(self):
        """Create the input and run the RCN program."""
        self.require_binary("rcn")

        rcn_input = self.RCN_HEADER
        for configuration in (self.configuration,):
            rcn_input += self.configuration_line(
                f"{'':11s}{configuration.value}",
                f"{self.normalize_configuration_name(configuration):8s}",
            )
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
        pairs = self.subshell_pairs(subshells)

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
                        for subshell in subshells:
                            if subshell.upper() in line:
                                params[f"ζ({subshell})"] = _format(line[9:20])
                        line = next(fp)

                # Parse the Slater integrals.
                for a, b in pairs:
                    if f"( {a.upper()}, {b.upper()})" in line:
                        k = int(line[17:18])
                        if k != 0:
                            params[f"F{k}({a},{b})"] = _format(line[18:31])
                        if a != b:
                            k = int(line[73:74])
                            params[f"G{k}({a},{b})"] = _format(line[75:88])

                if "ETOT=" in line:
                    energy = _format(line.split()[-1])

        # The names also drop the zeta of the s subshells, which is zero.
        names = self.parameter_names(subshells)
        ordered_params = {name: params.get(name, 0.0) for name in names}

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

    def parse_etot(self, text):
        """Return the configuration-average energy E_av (eV) from an rcn output.

        E_av is the last column of the ETOT line, the total energy with
        correlation; the difference between two configurations gives the
        offset that separates them in the Hamiltonian.
        """
        energy = None
        for line in text.splitlines():
            if "ETOT=" in line:
                energy = self._to_ev(line.split()[-1])
        return energy

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

        delta = f"Δ({d},{p})"
        result = {}
        # Final state: the 1s^1 n d^m (n+1)p^1 dipole channel mixes with the
        # 1s^1 n d^(m+1) quadrupole channel; their E_av difference is the offset.
        occupancies = f"1S01 {inner}{d_upper}{m:02d} {p_upper}01"
        label = f"     {symbol} 1s1 {d}{m} {p}1"
        text = self.run_rcn_configuration(label, occupancies)
        final = self.parse_dp_parameters(text, d, p, core=True)
        e_final_dp = self.parse_etot(text)
        occupancies = f"1S01 {inner}{d_upper}{m + 1:02d} {p_upper}00"
        label = f"     {symbol} 1s1 {d}{m + 1}"
        text = self.run_rcn_configuration(label, occupancies)
        final[delta] = round(e_final_dp - self.parse_etot(text), ndigits=4)
        result["Final Hamiltonian"] = final
        # Initial state: the n d^(m-1) (n+1)p^1 dipole channel mixes with the
        # n d^m ground configuration (needs at least one d electron).
        if m >= 1:
            occupancies = f"1S02 {inner}{d_upper}{m - 1:02d} {p_upper}01"
            label = f"     {symbol} {d}{m - 1} {p}1"
            text = self.run_rcn_configuration(label, occupancies)
            initial = self.parse_dp_parameters(text, d, p, core=False)
            e_initial_dp = self.parse_etot(text)
            occupancies = f"1S02 {inner}{d_upper}{m:02d} {p_upper}00"
            label = f"     {symbol} {d}{m}"
            text = self.run_rcn_configuration(label, occupancies)
            initial[delta] = round(e_initial_dp - self.parse_etot(text), ndigits=4)
            result["Initial Hamiltonian"] = initial
        return result


def parse_configuration(value):
    """Parse a configuration with one or more subshells, for example "2p5,4f7,5d2".

    Unlike Configuration, the parser accepts more than two subshells.
    """
    tokens = re.findall(r"(\d)([spdf])(\d+)", value)
    if ",".join("".join(token) for token in tokens) != value:
        raise ValueError(f"Invalid configuration string {value}.")
    for level, shell, occupancy in tokens:
        if int(occupancy) > OCCUPANCIES[shell]:
            raise ValueError(f"Wrong number of electrons in the {level}{shell} shell.")
    return SimpleNamespace(
        value=value,
        subshells=tuple(f"{level}{shell}" for level, shell, _ in tokens),
        occupancies=tuple(int(occupancy) for _, _, occupancy in tokens),
    )


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
    conf = parse_configuration(args.configuration)

    cowan = Cowan(element, conf)
    energy, atomic_parameters = cowan.get_parameters()

    if logging.root.level != logging.DEBUG:
        cowan.remove_calculation_files()

    logging.info("%2s %-8s", element.symbol, conf.value)
    logging.info("E = %-.4f eV", energy)
    for parameter, value in atomic_parameters.items():
        logging.info("%-s = %-.4f eV", parameter, value)


if __name__ == "__main__":
    main()
