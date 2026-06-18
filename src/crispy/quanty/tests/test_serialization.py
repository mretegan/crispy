#!/usr/bin/env python3

"""Round-trip tests for saving and loading results to and from HDF5."""

import h5py
import numpy as np
import pytest

from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation
from crispy.quanty.external import ExternalData
from crispy.quanty.serialization import (
    FORMAT,
    FORMAT_VERSION,
    load_results,
    save_results,
)
from crispy.quanty.spectra import Spectrum1D, Spectrum2D


@pytest.fixture(autouse=True)
def _qapp(qapp):
    """Ensure a QApplication (provided by pytest-qt) exists for every test."""
    return qapp


def make_calculation(parent, experiment="XAS", edge="L2,3 (2p)", symmetry="Oh"):
    return Calculation(
        symbol="Ni",
        charge="2+",
        symmetry=symmetry,
        experiment=experiment,
        edge=edge,
        parent=parent,
    )


def find_term(calculation, name):
    for term in calculation.hamiltonian.terms.children():
        if term.name == name:
            return term
    raise AssertionError(f"Term {name!r} not found.")


def hamiltonian_state(calculation):
    """Collect every term check state and parameter value/scale factor."""
    state = {}
    for term in calculation.hamiltonian.terms.children():
        state[(term.name,)] = int(term.checkState.value)
        for subHamiltonian in term.children():
            for parameter in subHamiltonian.children():
                key = (term.name, subHamiltonian.name, parameter.name)
                state[key] = (parameter.value, parameter.scaleFactor)
    return state


def axes_state(calculation):
    axes = calculation.axes
    state = {
        "scale": axes.scale.value,
        "normalization": axes.normalization.value,
    }
    pairs = [("x", axes.xaxis)]
    if calculation.experiment.isTwoDimensional:
        pairs.append(("y", axes.yaxis))
    for prefix, axis in pairs:
        state[prefix + "shift"] = axis.shift.value
        state[prefix + "start"] = axis.start.value
        state[prefix + "stop"] = axis.stop.value
        state[prefix + "npoints"] = axis.npoints.value
        state[prefix + "gaussian"] = axis.gaussian.value
        state[prefix + "lorentzian"] = axis.lorentzian.value
        state[prefix + "k"] = tuple(axis.photon.k.value)
        state[prefix + "e1"] = tuple(axis.photon.e1.value)
        if hasattr(axis.photon, "analyze"):
            state[prefix + "analyze"] = axis.photon.analyze.value
    return state


def add_spectrum_1d(calculation, name, suffix, label):
    xaxis = calculation.axes.xaxis
    npoints = xaxis.npoints.value + 1
    x = np.linspace(xaxis.start.value, xaxis.stop.value, npoints)
    signal = np.exp(-((x - x.mean()) ** 2))
    raw = np.column_stack([x, np.zeros_like(x), signal])

    spectrum = Spectrum1D(parent=calculation.spectra.toPlot, name=name)
    spectrum.suffix = suffix
    spectrum.label = label
    spectrum.lineStyle = "-"
    spectrum.raw = raw
    spectrum.process()
    spectrum.enable()
    return spectrum


def add_spectrum_2d(calculation, name, suffix, label):
    xaxis = calculation.axes.xaxis
    yaxis = calculation.axes.yaxis
    nx = xaxis.npoints.value + 1
    ny = yaxis.npoints.value + 1
    # The 2D signal is read from raw[:, 2::2]; build a raw block of the matching
    # shape (nx rows, ny signal columns interleaved with placeholder columns).
    signal = np.arange(nx * ny, dtype=np.float64).reshape(nx, ny)
    columns = [np.zeros(nx), np.zeros(nx)]
    for column in signal.T:
        columns.append(column)
        columns.append(np.zeros(nx))
    raw = np.column_stack(columns)

    spectrum = Spectrum2D(parent=calculation.spectra.toPlot, name=name)
    spectrum.suffix = suffix
    spectrum.label = label
    spectrum.raw = raw
    spectrum.process()
    spectrum.enable()
    return spectrum


def test_round_trip_one_dimensional(tmp_path, qapp):
    model = TreeModel()
    calculation = make_calculation(model.rootItem())

    # Keep the spectra small and fast.
    calculation.axes.xaxis.npoints._value = 40

    # Edit a spread of parameters across the tree.
    calculation.value = "custom_name"
    calculation.labelSuffix = "scan 1"
    calculation.temperature.value = 300
    calculation.magneticField.value = 1.5  # writes Bx/By/Bz and enables the term
    calculation.hamiltonian.fk.value = 0.95
    calculation.hamiltonian.fk.updateIndividualScaleFactors(0.95)
    calculation.hamiltonian.numberOfStates.value = 5
    calculation.hamiltonian.numberOfStates.auto.value = False
    calculation.axes.scale.value = 2.0
    calculation.axes.normalization.value = "Area"
    calculation.axes.xaxis.start._value = -12.34
    calculation.axes.xaxis.gaussian.value = 0.3
    calculation.runner.output = "Quanty log output"

    atomic = find_term(calculation, "Atomic")
    atomic_parameter = next(iter(atomic.parameters))
    atomic_parameter.value = 7.77

    crystal_field = find_term(calculation, "Crystal Field")
    next(p for p in crystal_field.parameters if p.name == "10Dq(3d)").value = 1.23

    # Select a different set of spectra to calculate.
    calculation.spectra.toCalculate.selected = {"Absorption", "Circular Dichroic"}

    # A computed result spectrum.
    spectrum = add_spectrum_1d(calculation, "Absorption", "k", "Absorption")
    expected_x = spectrum.x.copy()
    expected_signal = spectrum.signal.copy()

    expected_hamiltonian = hamiltonian_state(calculation)
    expected_axes = axes_state(calculation)

    path = str(tmp_path / "results.h5")
    save_results([calculation], path)

    new_model = TreeModel()
    loaded = load_results(path, new_model.rootItem())

    assert len(loaded) == 1
    [result] = loaded
    assert result is not calculation
    assert isinstance(result, Calculation)
    assert result.parent() is new_model.rootItem()

    # Identity and scalars.
    assert result.element.symbol == "Ni"
    assert result.element.charge == "2+"
    assert result.symmetry.value == "Oh"
    assert result.experiment.value == "XAS"
    assert result.edge.value == "L2,3 (2p)"
    assert result.value == "custom_name"
    assert result.labelSuffix == "scan 1"
    assert result.temperature.value == 300
    assert result.magneticField.value == 1.5
    assert result.hamiltonian.numberOfStates.value == 5
    assert result.hamiltonian.numberOfStates.auto.value is False
    assert result.runner.output == "Quanty log output"

    # Axes and Hamiltonian round-trip in full.
    assert axes_state(result) == expected_axes
    assert hamiltonian_state(result) == expected_hamiltonian

    # The magnetic-field term is enabled and its Bz matches.
    assert find_term(result, "Magnetic Field").isEnabled()

    # Spectra selection.
    assert set(result.spectra.toCalculate.selected) == {
        "Absorption",
        "Circular Dichroic",
    }

    # The computed result is reconstructed and reprocessed identically.
    [loaded_spectrum] = result.spectra.toPlot.children()
    assert isinstance(loaded_spectrum, Spectrum1D)
    assert loaded_spectrum.name == "Absorption"
    assert loaded_spectrum.suffix == "k"
    assert loaded_spectrum.label == "Absorption"
    assert loaded_spectrum.isEnabled()
    assert np.allclose(loaded_spectrum.x, expected_x)
    assert np.allclose(loaded_spectrum.signal, expected_signal)


def test_round_trip_two_dimensional(tmp_path, qapp):
    model = TreeModel()
    calculation = make_calculation(
        model.rootItem(), experiment="RIXS", edge="L2,3-M4,5 (2p3d)"
    )

    calculation.axes.xaxis.npoints._value = 5
    calculation.axes.yaxis.npoints._value = 4
    calculation.axes.yaxis.photon.analyze.value = False

    spectrum = add_spectrum_2d(
        calculation, "Resonant Inelastic", "k", "Resonant Inelastic"
    )
    expected_x = spectrum.x.copy()
    expected_y = spectrum.y.copy()
    expected_signal = spectrum.signal.copy()

    path = str(tmp_path / "rixs.h5")
    save_results([calculation], path)

    new_model = TreeModel()
    [result] = load_results(path, new_model.rootItem())

    assert result.experiment.value == "RIXS"
    assert result.axes.yaxis.photon.analyze.value is False

    [loaded_spectrum] = result.spectra.toPlot.children()
    assert isinstance(loaded_spectrum, Spectrum2D)
    assert np.allclose(loaded_spectrum.x, expected_x)
    assert np.allclose(loaded_spectrum.y, expected_y)
    assert np.allclose(loaded_spectrum.signal, expected_signal)


def test_round_trip_external_data(tmp_path, qapp):
    model = TreeModel()
    raw = np.column_stack([np.linspace(0, 10, 25), np.random.default_rng(0).random(25)])
    external = ExternalData(raw=raw, parent=model.rootItem(), name="experiment")

    path = str(tmp_path / "external.h5")
    save_results([external], path)

    new_model = TreeModel()
    [result] = load_results(path, new_model.rootItem())

    assert isinstance(result, ExternalData)
    assert result.name == "experiment"
    assert result.isEnabled()
    assert np.allclose(result.raw, raw)


def test_round_trip_empty_selection(tmp_path, qapp):
    """No spectra selected writes a zero-length string dataset that must reload
    as an empty selection."""
    model = TreeModel()
    calculation = make_calculation(model.rootItem())
    calculation.spectra.toCalculate.selected = set()
    assert list(calculation.spectra.toCalculate.selected) == []

    path = str(tmp_path / "empty.h5")
    save_results([calculation], path)

    new_model = TreeModel()
    [result] = load_results(path, new_model.rootItem())
    assert list(result.spectra.toCalculate.selected) == []


def test_round_trip_multiple_result_spectra(tmp_path, qapp):
    """Several computed spectra (as produced for dichroic or hybridized edges)
    round-trip in order with their individual check states."""
    model = TreeModel()
    calculation = make_calculation(model.rootItem())
    calculation.axes.xaxis.npoints._value = 20

    names = ["Circular Dichroic (R-L)", "Right Polarized (R)", "Left Polarized (L)"]
    for index, name in enumerate(names):
        spectrum = add_spectrum_1d(calculation, name, "cd", name)
        # Only the first spectrum is checked.
        spectrum.disable() if index else spectrum.enable()

    path = str(tmp_path / "multi.h5")
    save_results([calculation], path)

    new_model = TreeModel()
    [result] = load_results(path, new_model.rootItem())
    spectra = result.spectra.toPlot.children()
    assert [spectrum.name for spectrum in spectra] == names
    assert [spectrum.isEnabled() for spectrum in spectra] == [True, False, False]


def test_mixed_items_preserve_order(tmp_path, qapp):
    model = TreeModel()
    calculation = make_calculation(model.rootItem())
    calculation.axes.xaxis.npoints._value = 20
    external = ExternalData(
        raw=np.column_stack([np.arange(5.0), np.arange(5.0)]),
        parent=model.rootItem(),
        name="reference",
    )

    path = str(tmp_path / "mixed.h5")
    save_results([calculation, external], path)

    new_model = TreeModel()
    loaded = load_results(path, new_model.rootItem())
    assert [type(item) for item in loaded] == [Calculation, ExternalData]
    assert loaded[1].name == "reference"


def test_load_rejects_foreign_file(tmp_path, qapp):
    path = str(tmp_path / "foreign.h5")
    with h5py.File(path, "w") as h5:
        h5["data"] = np.arange(10)

    model = TreeModel()
    with pytest.raises(ValueError, match="not a Crispy results file"):
        load_results(path, model.rootItem())


def test_load_rejects_newer_version(tmp_path, qapp):
    path = str(tmp_path / "newer.h5")
    with h5py.File(path, "w") as h5:
        h5.attrs["format"] = FORMAT
        h5.attrs["format_version"] = FORMAT_VERSION + 1

    model = TreeModel()
    with pytest.raises(ValueError, match="newer version"):
        load_results(path, model.rootItem())
