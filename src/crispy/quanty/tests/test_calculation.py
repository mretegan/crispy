#!/usr/bin/env python3

"""Tests for carrying parameters over when a single selection changes."""

import re

import pytest
from silx.gui.qt import Qt

from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation


@pytest.fixture(autouse=True)
def _qapp(qapp):
    """Ensure a QApplication (provided by pytest-qt) exists for every test."""
    return qapp


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
    return {(p.parent().name, p.name): round(p.value, 4) for p in term.parameters}


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


def test_d3d_crystal_field_parameters():
    """D3d exposes the trigonal irrep-energy parameter set and adds no ligand or
    pd-hybridization terms (crystal-field only) for both the d and the f block."""
    model = TreeModel()

    d_block = make_calculation("D3d", model.rootItem())  # Ni2+ (3d)
    assert crystal_field_names(d_block) == {
        "Ea1g(3d)",
        "Eegσ(3d)",  # noqa: RUF001
        "Eegπ(3d)",
        "Meg(3d)",
    }
    assert [t.name for t in d_block.hamiltonian.terms.children()] == [
        "Atomic",
        "Crystal Field",
        "Magnetic Field",
        "Exchange Field",
    ]

    f_block = Calculation(
        symbol="Ce",
        charge="3+",
        symmetry="D3d",
        experiment="XAS",
        edge="M4,5 (3d)",
        parent=model.rootItem(),
    )
    assert crystal_field_names(f_block) == {
        "Ea1u(4f)",
        "Ea2uA(4f)",
        "Ea2uB(4f)",
        "Eeu1(4f)",
        "Eeu2(4f)",
        "Ma2u(4f)",
        "Meu(4f)",
    }
    assert [t.name for t in f_block.hamiltonian.terms.children()] == [
        "Atomic",
        "Crystal Field",
        "Magnetic Field",
        "Exchange Field",
    ]


@pytest.mark.parametrize(
    ("symbol", "charge", "edge", "template"),
    [
        ("Ni", "2+", "L2,3 (2p)", "3d_D3d_XAS_2p.lua"),  # d block, p core (pd)
        ("Co", "2+", "K (1s)", "3d_D3d_XAS_1s.lua"),  # d block, s core (sd)
        ("Ce", "3+", "M4,5 (3d)", "4f_D3d_XAS_3d.lua"),  # f block, d core (df)
        ("Nd", "3+", "L2,3 (2p)", "4f_D3d_XAS_2p.lua"),  # f block, p core (pf)
    ],
)
def test_d3d_template_renders_without_unresolved_parameters(
    symbol, charge, edge, template
):
    """Every D3d crystal-field parameter placeholder in the generated template is
    filled by the parameters defined in the Hamiltonian (names must match)."""
    model = TreeModel()
    calculation = Calculation(
        symbol=symbol,
        charge=charge,
        symmetry="D3d",
        experiment="XAS",
        edge=edge,
        parent=model.rootItem(),
    )
    assert calculation.templateName == template
    # No "$Name(subshell)_i/f_value" parameter placeholder should remain.
    assert not re.search(r"\$[A-Za-z0-9]+\([^)]*\)_[if]_value", calculation.input)


@pytest.mark.parametrize(
    ("symbol", "charge", "edge", "dipole"),
    [
        ("Ni", "2+", "L2,3-M4,5 (2p3d)", True),  # pdd: 2p -> 3d, dipole
        ("Ce", "3+", "M4,5-N6,7 (3d4f)", True),  # dff: 3d -> 4f, dipole
        ("U", "3+", "M4,5-O6,7 (3d5f)", True),  # dff: 3d -> 5f, dipole
        ("Ni", "2+", "K-L2,3 (1s2p)", False),  # sdp: 1s -> 3d, quadrupole
        ("Ce", "3+", "L2,3-M4,5 (2p3d)", False),  # 2p -> 4f, quadrupole
    ],
)
def test_rixs_powder_offered_only_for_dipole_dipole(symbol, charge, edge, dipole):
    """The powder/isotropic RIXS spectrum is built from the rank-2 fundamental
    spectra and is only valid for dipole-in/dipole-out edges. It must be offered
    for the pdd/dff edges and withheld for the quadrupole-in (sdp/pfd) edges."""
    model = TreeModel()
    calculation = Calculation(
        symbol=symbol,
        charge=charge,
        symmetry="Oh",
        experiment="RIXS",
        edge=edge,
        parent=model.rootItem(),
    )
    # Guard against a silent fall-back to a different edge.
    assert calculation.edge.value == edge
    assert calculation.isDipoleDipole is dipole

    samples = {s.name for s in calculation.spectra.toCalculate.children()}
    spectra = {s.name for s in calculation.spectra.toCalculate.all}
    assert ("Powder/Solution" in samples) is dipole
    assert ("Isotropic Resonant Inelastic" in spectra) is dipole
    # The single-crystal spectrum is always available.
    assert "Resonant Inelastic" in spectra


def test_rixs_spectra_are_single_select():
    """RIXS spectra are 2D maps, so only one can be active at a time. Checking one
    must uncheck the others."""
    model = TreeModel()
    calculation = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="RIXS",
        edge="L2,3-M4,5 (2p3d)",
        parent=model.rootItem(),
    )
    spectra = {s.name: s for s in calculation.spectra.toCalculate.all}
    assert set(spectra) == {"Resonant Inelastic", "Isotropic Resonant Inelastic"}

    # Exactly one is enabled by default.
    assert sum(s.isEnabled() for s in spectra.values()) == 1

    # Checking the powder spectrum unchecks the single-crystal one.
    spectra["Isotropic Resonant Inelastic"].setData(
        0, Qt.CheckState.Checked, Qt.CheckStateRole
    )
    assert spectra["Isotropic Resonant Inelastic"].isEnabled()
    assert not spectra["Resonant Inelastic"].isEnabled()

    # And vice versa.
    spectra["Resonant Inelastic"].setData(0, Qt.CheckState.Checked, Qt.CheckStateRole)
    assert spectra["Resonant Inelastic"].isEnabled()
    assert not spectra["Isotropic Resonant Inelastic"].isEnabled()


def test_analyze_checkbox_enabled_only_for_isotropic_rixs():
    """The outgoing-polarization checkbox controls only the isotropic RIXS
    geometry factor, so it is enabled only while that spectrum is selected."""
    from crispy.quanty.main import GeneralSetupPage

    model = TreeModel()
    calculation = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="RIXS",
        edge="L2,3-M4,5 (2p3d)",
        parent=model.rootItem(),
    )
    page = GeneralSetupPage()
    page.populate(calculation)
    checkbox = page.yAxis.analyzeCheckBox

    spectra = {s.name: s for s in calculation.spectra.toCalculate.all}

    # Single-crystal is the default selection, so the checkbox starts disabled.
    assert not checkbox.isEnabled()

    # Selecting the isotropic spectrum enables it; reselecting the single-crystal
    # spectrum disables it again (RIXS spectra are single-select).
    spectra["Isotropic Resonant Inelastic"].setData(
        0, Qt.CheckState.Checked, Qt.CheckStateRole
    )
    assert checkbox.isEnabled()

    spectra["Resonant Inelastic"].setData(0, Qt.CheckState.Checked, Qt.CheckStateRole)
    assert not checkbox.isEnabled()


def test_save_output_writes_log_next_to_input(tmp_path, monkeypatch):
    """The Quanty output (the log) is written to "<name>.out" so it is kept on
    disk together with the input and spectra files."""
    model = TreeModel()
    calculation = make_calculation("Oh", model.rootItem())
    calculation.runner.output = "Quanty log\nsecond line"

    monkeypatch.chdir(tmp_path)
    calculation.saveOutput()

    output = tmp_path / f"{calculation.value}.out"
    assert output.read_text(encoding="utf-8") == "Quanty log\nsecond line"


def test_save_output_skips_empty_log(tmp_path, monkeypatch):
    """No file is created when the calculation produced no output."""
    model = TreeModel()
    calculation = make_calculation("Oh", model.rootItem())
    calculation.runner.output = ""

    monkeypatch.chdir(tmp_path)
    calculation.saveOutput()

    assert not (tmp_path / f"{calculation.value}.out").exists()


def test_clean_removes_input_spectra_and_output(tmp_path, monkeypatch):
    """clean() removes the input, the spectra, and the output log together."""
    model = TreeModel()
    calculation = make_calculation("Oh", model.rootItem())
    name = calculation.value

    monkeypatch.chdir(tmp_path)
    (tmp_path / f"{name}.lua").write_text("-- input", encoding="utf-8")
    (tmp_path / f"{name}_iso.spec").write_text("0 0", encoding="utf-8")
    (tmp_path / f"{name}.out").write_text("log", encoding="utf-8")

    calculation.clean()

    assert not (tmp_path / f"{name}.lua").exists()
    assert not (tmp_path / f"{name}_iso.spec").exists()
    assert not (tmp_path / f"{name}.out").exists()


def test_clean_without_output_file_does_not_raise(tmp_path, monkeypatch):
    """A run with no output leaves no ".out" file; clean() must still succeed."""
    model = TreeModel()
    calculation = make_calculation("Oh", model.rootItem())
    name = calculation.value

    monkeypatch.chdir(tmp_path)
    (tmp_path / f"{name}.lua").write_text("-- input", encoding="utf-8")
    (tmp_path / f"{name}_iso.spec").write_text("0 0", encoding="utf-8")

    calculation.clean()

    assert not (tmp_path / f"{name}.lua").exists()
    assert not (tmp_path / f"{name}_iso.spec").exists()


def test_xas_spectra_allow_multiple_selection():
    """One-dimensional experiments (XAS) can plot several curves together, so the
    single-selection rule must not apply to them."""
    model = TreeModel()
    calculation = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="XAS",
        edge="L2,3 (2p)",
        parent=model.rootItem(),
    )
    spectra = {s.name: s for s in calculation.spectra.toCalculate.all}
    for name in ("Absorption", "Circular Dichroic"):
        spectra[name].setData(0, Qt.CheckState.Checked, Qt.CheckStateRole)
    assert spectra["Absorption"].isEnabled()
    assert spectra["Circular Dichroic"].isEnabled()
