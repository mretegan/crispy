#!/usr/bin/env python3
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
        return list(yaml.load(f).items())


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

    # Change the settings after the calculation is created, because creating
    # the calculation can reset them to the defaults. Keep the spectra on disk
    # to compare them with the references.
    calc = calculation(*parameters["args"])

    settings = Config().read()
    settings.setValue("CurrentPath", str(tmp_path))
    settings.setValue("Quanty/RemoveFiles", False)
    settings.sync()

    calc.set_parameter("Basename", "test")
    # Always test the isotropic spectrum, not the default spectrum.
    calc._calculation.spectra.toCalculate.selected = {"Isotropic Absorption"}
    for parameter in parameters:
        if parameter == "parameters":
            for args in parameters["parameters"]:
                calc.set_parameter(*args)
        if parameter == "hamiltonian":
            set_hamiltonian_parameters(calc, parameters["hamiltonian"])

    calc.run()

    ref_path = os.path.join(os.path.dirname(__file__), "references", f"{idx}")
    spectra = sorted(os.path.basename(p) for p in glob.glob(f"{tmp_path}/*.spec"))
    references = sorted(os.path.basename(p) for p in glob.glob(f"{ref_path}/*.spec"))
    assert spectra, "The calculation did not write any spectra."
    assert spectra == references
    for spectrum in spectra:
        ref = np.loadtxt(os.path.join(ref_path, spectrum), skiprows=5)
        out = np.loadtxt(os.path.join(tmp_path, spectrum), skiprows=5)
        try:
            kwargs = parameters["test"]["numpy_allclose_kwargs"]
        except KeyError:
            kwargs = {}
        assert np.allclose(ref, out, **kwargs)
