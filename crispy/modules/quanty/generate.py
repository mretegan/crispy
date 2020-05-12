#!/usr/bin/env python3
# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This module provides a command line interface for generating the parameters of atomic configurations."""

__authors__ = ["Marius Retegan"]
__license__ = "MIT"
__date__ = "11/05/2019"

import argparse
import logging
import os

import h5py

from crispy.modules.quanty.utils import Calculations, Cowan, Element


def generate_parameters(elements):
    """Generate the atomic parameters of the elements and store them in an HDF5 container."""

    config = h5py.get_config()
    config.track_order = True

    root = os.path.dirname(os.path.abspath(__file__))

    calculations = Calculations(os.path.join(root, "calculations.json"))

    if elements == "all":
        elements = calculations.get_all_elements()

    for element in elements:
        element = Element(element)
        confs = calculations.unique_configurations(element)

        filename = "{:s}.h5".format(element.symbol)
        path = os.path.join(root, "atomic_parameters", filename)

        with h5py.File(path, "w") as h5:
            for conf in confs:
                cowan = Cowan(element, conf)
                conf.energy, conf.atomic_parameters = cowan.get_parameters()
                cowan.remove_calculation_files()

                # Write the parameters to the HDF5 file.
                root = "/{:s}".format(conf.name)
                h5[root + "/energy"] = conf.energy
                for parameter, value in conf.atomic_parameters.items():
                    path = root + "/parameters/{:s}".format(parameter)
                    h5[path] = value

                logging.info("%-2s %-8s", element.symbol, conf)
                logging.info("E = %-.4f eV", conf.energy)
                for parameter, value in conf.atomic_parameters.items():
                    logging.debug("%-s = %-.4f eV", parameter, value)
                logging.info("")


def main():
    parser = argparse.ArgumentParser(
        description="Generate the data needed to run the Quanty calculations.",
    )
    parser.add_argument("-l", "--loglevel", default="info")

    subparsers = parser.add_subparsers(dest="command")

    parameters = subparsers.add_parser("parameters")
    parameters.add_argument(
        "-e",
        "--elements",
        default="all",
        nargs="+",
        help="list of elements for which to generate the parameters",
    )

    args = parser.parse_args()

    logging.basicConfig(format="%(message)s", level=args.loglevel.upper())

    if args.command == "parameters":
        generate_parameters(args.elements)


if __name__ == "__main__":
    main()
