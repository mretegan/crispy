#!/usr/bin/env python3
###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################

"""Quanty templates tests"""

import glob
import os

import numpy as np
import pytest
from ruamel.yaml import YAML

from crispy.config import Config
from crispy.notebook import calculation


def get_test_data():
    path = os.path.join(os.path.dirname(__file__), "test_data.yaml")
    with open(path, encoding="utf-8") as f:
        yaml = YAML(pure=True)
        yield from list(yaml.load(f).items())


def set_hamiltonian_parameters(calc, parameters):
    if "terms" in parameters:
        for term in parameters["terms"]:
            calc.hamiltonian.terms.enable(term["name"])
            for args in term["parameters"]:
                calc.hamiltonian.set_parameter(*args)

    if "parameters" in parameters:
        for args in parameters["parameters"]:
            calc.hamiltonian.set_parameter(*args)


@pytest.mark.parametrize("test_data", get_test_data())
def test_calculation(test_data, tmp_path):
    idx, parameters = test_data

    # Run tests in /tmp/tests
    # tmp_path = os.path.join("/tmp/crispy/tests", str(idx))
    # if os.path.exists(tmp_path):
    #     shutil.rmtree(tmp_path)
    # os.makedirs(tmp_path, exist_ok=True)

    settings = Config().read()
    # TODO: Save the current path before altering it.
    settings.setValue("CurrentPath", tmp_path)

    calc = calculation(*parameters["args"])

    calc.set_parameter("Basename", "test")
    for parameter in parameters:
        if parameter == "parameters":
            for args in parameters["parameters"]:
                calc.set_parameter(*args)
        if parameter == "hamiltonian":
            set_hamiltonian_parameters(calc, parameters["hamiltonian"])

    calc.run()

    ref_path = os.path.join(os.path.dirname(__file__), "references", f"{idx}")
    for spectrum in glob.glob("*.spec"):
        ref = np.loadtxt(os.path.join(ref_path, spectrum), skiprows=5)
        out = np.loadtxt(os.path.join(tmp_path, spectrum), skiprows=5)
        try:
            kwargs = parameters["test"]["numpy_allclose_kwargs"]
        except KeyError:
            kwargs = {}
        assert np.allclose(ref, out, **kwargs)
