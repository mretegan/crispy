#!/usr/bin/env python3

"""Tests for carrying parameters over when a single selection changes."""

import pytest
from silx.gui import qt

from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation


@pytest.fixture(scope="module", autouse=True)
def qapp():
    app = qt.QApplication.instance() or qt.QApplication([])
    yield app


def make_calculation(symmetry, parent):
    return Calculation(
        symbol="Ni",
        charge="2+",
        symmetry=symmetry,
        experiment="XAS",
        edge="L2,3 (2p)",
        parent=parent,
    )


def find_term(calculation, name):
    for term in calculation.hamiltonian.terms.children():
        if term.name == name:
            return term
    raise AssertionError(f"Term {name!r} not found.")


def crystal_field_names(calculation):
    term = find_term(calculation, "Crystal Field")
    return {parameter.name for parameter in term.parameters}


def test_symmetry_change_preserves_independent_parameters():
    model = TreeModel()
    old = make_calculation("Oh", model.rootItem())

    # Parameters that do not depend on the symmetry.
    old.temperature.value = 300
    old.hamiltonian.fk.value = 0.95
    old.hamiltonian.numberOfStates.value = 5
    old.axes.xaxis.start.value = -12.34

    atomic = find_term(old, "Atomic")
    atomic_parameter = next(iter(atomic.parameters))
    atomic_parameter.value = 7.77
    atomic_key = (atomic_parameter.parent().name, atomic_parameter.name)

    # A crystal-field value that must NOT carry over to the new symmetry.
    crystal_field = find_term(old, "Crystal Field")
    next(iter(crystal_field.parameters)).value = 9.99

    new = make_calculation("D4h", model.rootItem())
    new.copyFromExceptSymmetry(old)

    # The name reflects the new symmetry.
    assert new.value == "Ni2+_D4h_XAS_2p"
    assert new.symmetry.value == "D4h"

    # Symmetry-independent parameters are preserved.
    assert new.temperature.value == 300
    assert new.hamiltonian.fk.value == 0.95
    assert new.hamiltonian.numberOfStates.value == 5
    assert new.axes.xaxis.start.value == -12.34

    new_atomic = find_term(new, "Atomic")
    new_atomic_values = {
        (p.parent().name, p.name): p.value for p in new_atomic.parameters
    }
    assert new_atomic_values[atomic_key] == 7.77

    # The crystal-field term is regenerated for D4h: it has the D4h parameter
    # set and the default 10Dq, not the modified value from Oh.
    assert crystal_field_names(new) == {"10Dq(3d)", "Ds(3d)", "Dt(3d)"}
    new_crystal_field = find_term(new, "Crystal Field")
    tenDq = next(p for p in new_crystal_field.parameters if p.name == "10Dq(3d)")
    assert tenDq.value == 1.0


def test_symmetry_change_handles_differing_term_sets():
    """Oh has ligand-hybridization terms; D3h has none. The symmetry-independent
    terms must still be matched by name rather than by position."""
    model = TreeModel()
    old = make_calculation("Oh", model.rootItem())

    old.magneticField.value = 2.0  # writes Bx/By/Bz and enables the term
    exchange = find_term(old, "Exchange Field")
    exchange.enable()
    next(iter(exchange.parameters)).value = 0.5

    magnetic = find_term(old, "Magnetic Field")
    bz = next(p for p in magnetic.parameters if p.name == "Bz").value

    new = make_calculation("D3h", model.rootItem())
    # D3h drops the ligand terms, so the term lists have different shapes.
    assert "3d-Ligands Hybridization (LMCT)" not in {
        t.name for t in new.hamiltonian.terms.children()
    }
    new.copyFromExceptSymmetry(old)

    new_magnetic = find_term(new, "Magnetic Field")
    new_exchange = find_term(new, "Exchange Field")

    assert new.magneticField.value == 2.0
    assert new_magnetic.isEnabled()
    assert next(p for p in new_magnetic.parameters if p.name == "Bz").value == bz
    assert new_exchange.isEnabled()
    assert next(iter(new_exchange.parameters)).value == 0.5

    # The crystal field is regenerated for D3h.
    assert crystal_field_names(new) == {"Dμ(3d)", "Dν(3d)"}  # noqa: RUF001


def test_experimental_conditions_transfer_across_element_change():
    """Temperature and magnetic field are carried over even when the element
    changes; the magnetic field term is recomputed for the new calculation."""
    model = TreeModel()
    old = make_calculation("Oh", model.rootItem())
    old.temperature.value = 77
    old.magneticField.value = 4.0  # writes Bz and enables the term

    magnetic = find_term(old, "Magnetic Field")
    bz = next(p for p in magnetic.parameters if p.name == "Bz").value
    assert magnetic.isEnabled()

    new = Calculation(
        symbol="Fe",
        charge="2+",
        symmetry="Oh",
        experiment="XAS",
        edge="L2,3 (2p)",
        parent=model.rootItem(),
    )
    new.copyExperimentalConditions(old)

    assert new.temperature.value == 77
    assert new.magneticField.value == 4.0

    new_magnetic = find_term(new, "Magnetic Field")
    assert new_magnetic.isEnabled()
    # The default wave vector is the same, so the recomputed Bz matches.
    assert next(p for p in new_magnetic.parameters if p.name == "Bz").value == bz


def test_experimental_conditions_zero_field_leaves_term_disabled():
    model = TreeModel()
    old = make_calculation("Oh", model.rootItem())
    old.temperature.value = 123  # magnetic field left at its default of 0

    new = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="RIXS",
        edge="L2,3 (2p)",
        parent=model.rootItem(),
    )
    new.copyExperimentalConditions(old)

    assert new.temperature.value == 123
    assert new.magneticField.value == 0
    assert not find_term(new, "Magnetic Field").isEnabled()


def test_experimental_conditions_transfer_gaussian_broadening():
    model = TreeModel()
    old = make_calculation("Oh", model.rootItem())
    old.axes.xaxis.gaussian.value = 0.7

    new = Calculation(
        symbol="Fe",
        charge="2+",
        symmetry="Oh",
        experiment="XAS",
        edge="L2,3 (2p)",
        parent=model.rootItem(),
    )
    new.copyExperimentalConditions(old)

    assert new.axes.xaxis.gaussian.value == 0.7


def test_gaussian_broadening_partial_when_adding_second_axis():
    """A one-dimensional source has no second axis, so the new y-axis keeps its
    default broadening instead of failing."""
    model = TreeModel()
    old = make_calculation("Oh", model.rootItem())  # XAS is one-dimensional
    old.axes.xaxis.gaussian.value = 0.5

    new = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="RIXS",  # two-dimensional, adds a y-axis
        edge="L2,3 (2p)",
        parent=model.rootItem(),
    )
    new.copyExperimentalConditions(old)

    assert new.axes.xaxis.gaussian.value == 0.5
    assert new.axes.yaxis.gaussian.value == 0.1


def atomic_values(calculation):
    term = find_term(calculation, "Atomic")
    return {
        (p.parent().name, p.name): round(p.value, 4) for p in term.parameters
    }


def test_charge_change_regenerates_atomic_and_preserves_the_rest():
    model = TreeModel()
    old = make_calculation("Oh", model.rootItem())  # Ni2+ is 3d8
    old.temperature.value = 250
    old.hamiltonian.fk.value = 0.95
    old.hamiltonian.fk.updateIndividualScaleFactors(0.95)
    next(iter(find_term(old, "Crystal Field").parameters)).value = 3.3
    old.magneticField.value = 1.5

    old_atomic = atomic_values(old)

    # A fresh calculation with the new charge, used as the reference for what the
    # regenerated atomic parameters should be.
    reference = Calculation(
        symbol="Ni",
        charge="1+",  # 3d9
        symmetry="Oh",
        experiment="XAS",
        edge="L2,3 (2p)",
        parent=model.rootItem(),
    )
    reference_atomic = atomic_values(reference)
    reference_states = reference.hamiltonian.numberOfStates.value

    new = Calculation(
        symbol="Ni",
        charge="1+",
        symmetry="Oh",
        experiment="XAS",
        edge="L2,3 (2p)",
        parent=model.rootItem(),
    )
    new.copyFromExceptCharge(old)

    assert new.value == "Ni1+_Oh_XAS_2p"

    # Charge-independent parameters are preserved.
    assert new.temperature.value == 250
    assert new.hamiltonian.fk.value == 0.95
    assert next(iter(find_term(new, "Crystal Field").parameters)).value == 3.3
    assert new.magneticField.value == 1.5

    # The atomic parameters are regenerated for the new charge.
    assert atomic_values(new) == reference_atomic
    assert atomic_values(new) != old_atomic

    # The number of states is regenerated for the new occupancy.
    assert new.hamiltonian.numberOfStates.value == reference_states

    # The preserved global scale factor is propagated to the regenerated atomic
    # term rather than left at the default.
    for parameter in find_term(new, "Atomic").parameters:
        if parameter.name.startswith("F"):
            assert parameter.scaleFactor == 0.95
