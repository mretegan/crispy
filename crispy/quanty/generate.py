#!/usr/bin/env python3
# coding: utf-8
###################################################################
# Copyright (c) 2016-2022 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This module provides a command line interface for generating the parameters of
atomic configurations and the calculations templates.
"""

import argparse
import logging
import os

import h5py
from crispy import resourceAbsolutePath
from crispy.loggers import setUpLoggers
from crispy.models import TreeModel
from crispy.quanty import CALCULATIONS
from crispy.quanty.calculation import Calculation, Element
from crispy.quanty.cowan import Cowan

logger = logging.getLogger("crispy.quanty.generate")
config = h5py.get_config()
config.track_order = True


def unique_configurations(element):
    """Determine the unique electronic configurations of an element."""
    valenceSubshell = element.valenceSubshell

    charges = CALCULATIONS[valenceSubshell]["symbols"][element.symbol]["charges"]
    experiments = CALCULATIONS[valenceSubshell]["experiments"]

    configurations = list()
    for charge in charges:
        element.charge = charge
        for experiment in experiments:
            edges = experiments[experiment]["edges"]
            for edge in edges:
                logger.debug((element.symbol, charge, experiment, edge))
                calculation = Calculation(
                    symbol=element.symbol,
                    charge=charge,
                    experiment=experiment,
                    edge=edge,
                    hamiltonian=False,
                    parent=None,
                )

                configurations.extend(calculation.configurations)
    return sorted(list(set(configurations)))


def get_all_symbols():
    """Return a list of element symbols."""
    symbols = list()
    for subshell in CALCULATIONS.keys():
        symbols.extend(CALCULATIONS[subshell]["symbols"].keys())
    return symbols


def read_hybridization_parameters(symbol, conf):
    """Read the p-d hybridization parameters from an external file."""
    path = resourceAbsolutePath(
        os.path.join("quanty", "parameters", "p-d_hybridization", "parameters.dat")
    )
    with open(path) as fp:
        for line in fp:
            if symbol in line and conf in line:
                *_, p1, p2 = line.strip().split(",")
                return {"P1(1s,4p)": float(p1), "P2(1s,3d)": float(p2)}
    return None


def generate_parameters(symbols):
    """Generate the atomic parameters of the elements and store them in an
    HDF5 container.
    """
    if "all" in symbols:
        symbols = get_all_symbols()

    for symbol in symbols:
        element = Element()
        element.symbol = symbol
        confs = unique_configurations(element)
        logger.debug(confs)

        path = resourceAbsolutePath(
            os.path.join("quanty", "parameters", f"{element.symbol}.h5")
        )

        with h5py.File(path, "w") as h5:
            for conf in confs:
                # Get the atomic parameters.
                cowan = Cowan(element, conf)
                conf.energy, conf.parameters = cowan.get_parameters()
                cowan.remove_calculation_files()

                # Write the parameters to the HDF5 file.
                root = f"/{conf.value}"
                # h5[root + "/energy"] = conf.energy

                subroot = root + "/Atomic"
                for parameter, value in conf.parameters.items():
                    path = subroot + "/{:s}".format(parameter)
                    h5[path] = value

                logger.info("%-2s %-8s", element.symbol, conf)
                logger.info("E = %-.4f eV", conf.energy)
                for parameter, value in conf.parameters.items():
                    logger.debug("%-s = %-.4f eV", parameter, value)

                parameters = read_hybridization_parameters(element.symbol, conf.value)
                if parameters is not None:
                    subroot = root + "/3d-4p Hybridization"
                    for parameter, value in parameters.items():
                        path = subroot + "/{:s}".format(parameter)
                        h5[path] = value


def get_all_calculations():
    """Get a generator with all possible calculations."""
    for subshell in CALCULATIONS.keys():
        experiments = CALCULATIONS[subshell]["experiments"]
        symbols = CALCULATIONS[subshell]["symbols"]
        # Get the first symbol and charge for each subshell.
        symbol = list(symbols.keys())[0]
        charge = CALCULATIONS[subshell]["symbols"][symbol]["charges"][0]
        for experiment in experiments:
            edges = experiments[experiment]["edges"]
            symmetries = experiments[experiment]["symmetries"]
            for edge in edges:
                for symmetry in symmetries:
                    # The model is needed because in the case of 2D calculations
                    # there are calls to dataChanged which need an index from the
                    # model.
                    model = TreeModel()
                    calculation = Calculation(
                        symbol=symbol,
                        charge=charge,
                        symmetry=symmetry,
                        experiment=experiment,
                        edge=edge,
                        hamiltonian=False,
                        parent=model,
                    )
                    yield calculation


def generate_templates():
    # pylint: disable=all
    """Generate the templates for the Quanty calculations."""
    for calculation in get_all_calculations():
        block = calculation.element.valenceBlock
        element = calculation.element
        symmetry = calculation.symmetry
        templateName = calculation.templateName
        experiment = calculation.experiment
        edge = calculation.edge

        # cf - crystal field
        # lf - crystal field and hybridization with the ligands
        # pd - crystal field and p-d hybridization
        suffix = "cf"
        if block == "d":
            if symmetry.value == "Oh":
                suffix = "lf"
            elif symmetry.value == "D4h":
                suffix = "lf"
            elif symmetry.value == "Td":
                if experiment.value == "XAS" and edge.value == "K (1s)":
                    suffix = "pd"
                else:
                    suffix = "cf"
            elif symmetry.value == "C3v":
                if experiment.value == "XAS" and edge.value == "K (1s)":
                    suffix = "pd"
                else:
                    suffix = "cf"
            elif symmetry.value == "D3h":
                suffix = "cf"
        elif block == "f":
            if symmetry.value == "Oh":
                suffix = "lf"
        else:
            suffix = "cf"

        # Get a string representation of the blocks involved in the calculation.
        coreBlocks = edge.coreBlocks
        valenceBlock = element.valenceBlock
        blocks = f"{coreBlocks[0]}{valenceBlock}"
        if len(coreBlocks) > 1:
            blocks += coreBlocks[1]

        templates = resourceAbsolutePath(os.path.join("quanty", "templates"))
        path = os.path.join(templates, "meta", experiment.value.lower(), blocks)

        SUBSTITUTIONS = {
            "#header": f"header_{suffix}.lua",
            "#symmetry_term": f"{symmetry.value.lower()}_{suffix}.lua",
            "#fields_term": "fields.lua",
            "#helper_functions": "helper_functions.lua",
            "#restrictions": f"restrictions_{suffix}.lua",
            "#footer": f"footer_{suffix}.lua",
        }

        try:
            with open(os.path.join(path, "base.lua")) as fp:
                base = fp.read()
        except FileNotFoundError:
            continue

        filename = None
        try:
            for key, filename in SUBSTITUTIONS.items():
                with open(os.path.join(path, filename)) as fp:
                    base = base.replace(key, fp.read())
        except FileNotFoundError:
            logger.warning(
                "Could not make %s template because the file %s is missing.",
                templateName,
                filename,
            )
            continue

        logger.info(
            "%s, %s, %s, %s",
            calculation.element.valenceSubshell,
            symmetry.value,
            experiment.value,
            edge.value,
        )

        base = base.replace("#symmetry", symmetry.value)
        base = base.replace("#edge", edge.value)
        base = base.replace("#experiment", experiment.value)

        if experiment.isOneDimensional:
            base = base.replace("#i", edge.coreSubshells[0])
            base = base.replace("#f", element.valenceSubshell)
        else:
            base = base.replace("#i", edge.coreSubshells[0])
            base = base.replace("#m", element.valenceSubshell)
            base = base.replace("#f", edge.coreSubshells[1])

        with open(os.path.join(templates, templateName), "w") as template:
            template.write(base)


def main():
    parser = argparse.ArgumentParser(
        description="Generate the data needed to run the Quanty calculations.",
    )

    subparsers = parser.add_subparsers(dest="command")

    parameters_subparser = subparsers.add_parser("parameters")
    parameters_subparser.add_argument(
        "-s",
        "--symbols",
        default="all",
        nargs="+",
        help="list of element symbols for which to generate the parameters",
    )
    parser.add_argument("-l", "--loglevel", default="info")

    subparsers.add_parser("templates")

    args = parser.parse_args()

    # Set up the application logger.
    setUpLoggers()
    # Set the level of the application logger using the command line arguments.
    logger = logging.getLogger("crispy")
    logger.setLevel(args.loglevel.upper())

    if args.command == "parameters":
        generate_parameters(args.symbols)

    if args.command == "templates":
        generate_templates()


if __name__ == "__main__":
    main()
