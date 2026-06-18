#!/usr/bin/env python3

"""Tests for the parameter scan logic."""

import pytest

from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation
from crispy.quanty.scan import scannableParameters, valueRange


@pytest.fixture(autouse=True)
def _qapp(qapp):
    """Ensure a QApplication (provided by pytest-qt) exists for every test."""
    return qapp


def make_calculation(parent):
    return Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="XAS",
        edge="L2,3 (2p)",
        parent=parent,
    )


def test_value_range_inclusive():
    assert valueRange(0.0, 1.0, 0.5) == pytest.approx([0.0, 0.5, 1.0])
    # The endpoint is kept despite floating point rounding.
    assert valueRange(0.0, 1.0, 0.1) == pytest.approx([i / 10 for i in range(11)])
    # A zero-width range yields a single point.
    assert valueRange(2.0, 2.0, 0.1) == [2.0]


def test_value_range_rejects_invalid():
    with pytest.raises(ValueError):
        valueRange(0.0, 1.0, 0.0)
    with pytest.raises(ValueError):
        valueRange(1.0, 0.0, 0.1)


def crystal_field_tenDq(calculation):
    """The 10Dq(3d) parameters of every Hamiltonian, keyed by Hamiltonian name."""
    term = next(
        term
        for term in calculation.hamiltonian.terms.children()
        if term.name == "Crystal Field"
    )
    return {p.parent().name: p for p in term.parameters if p.name == "10Dq(3d)"}


def test_scannable_parameters_include_expected():
    model = TreeModel()
    calculation = make_calculation(model.rootItem())

    labels = {parameter.label for parameter in scannableParameters(calculation)}

    # Scale factors, the experimental conditions and a crystal-field parameter
    # (labeled with its owning term).
    assert {"Fk", "Gk", "ζ", "Temperature", "Magnetic Field"} <= labels
    assert "Crystal Field · 10Dq(3d)" in labels


def test_hamiltonian_parameter_scopes():
    model = TreeModel()
    calculation = make_calculation(model.rootItem())

    parameters = {p.label: p for p in scannableParameters(calculation)}
    tenDq = parameters["Crystal Field · 10Dq(3d)"]

    # The scale factors and experimental conditions have no scope selector.
    assert parameters["Fk"].scopes is None

    # A one-step XAS calculation has an initial and a final Hamiltonian, plus the
    # leading "All" entry.
    displays = [display for display, _ in tenDq.scopes]
    assert displays == ["All", "Initial", "Final"]


def test_apply_all_scope_sets_every_hamiltonian():
    model = TreeModel()
    calculation = make_calculation(model.rootItem())

    parameters = {p.label: p for p in scannableParameters(calculation)}
    parameters["Crystal Field · 10Dq(3d)"].apply(calculation, 3.5)

    values = crystal_field_tenDq(calculation)
    assert values
    assert all(p.value == 3.5 for p in values.values())


def test_apply_single_scope_sets_only_one_hamiltonian():
    model = TreeModel()
    calculation = make_calculation(model.rootItem())

    parameters = {p.label: p for p in scannableParameters(calculation)}
    tenDq = parameters["Crystal Field · 10Dq(3d)"]

    before = {name: p.value for name, p in crystal_field_tenDq(calculation).items()}
    finalScope = next(key for display, key in tenDq.scopes if display == "Final")
    tenDq.apply(calculation, 3.5, finalScope)

    after = crystal_field_tenDq(calculation)
    assert after["Final Hamiltonian"].value == 3.5
    # The initial Hamiltonian keeps its original value.
    assert after["Initial Hamiltonian"].value == before["Initial Hamiltonian"]


def test_apply_scale_factor_updates_individual_factors():
    model = TreeModel()
    calculation = make_calculation(model.rootItem())

    parameters = {p.label: p for p in scannableParameters(calculation)}
    parameters["Fk"].apply(calculation, 0.7)

    assert calculation.hamiltonian.fk.value == 0.7
    atomic = next(
        term
        for term in calculation.hamiltonian.terms.children()
        if term.name == "Atomic"
    )
    fParameters = [p for p in atomic.parameters if p.name.startswith("F")]
    assert fParameters
    assert all(p.scaleFactor == 0.7 for p in fParameters)
