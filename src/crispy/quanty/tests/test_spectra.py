#!/usr/bin/env python3

"""Tests for the processing of the spectra."""

import numpy as np
import pytest

from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation
from crispy.quanty.spectra import Spectrum1D, Spectrum2D


@pytest.fixture(autouse=True)
def _qapp(qapp):
    """Ensure a QApplication (provided by pytest-qt) exists for every test."""
    return qapp


def make_calculation(model, experiment="XAS", edge="L2,3 (2p)"):
    return Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment=experiment,
        edge=edge,
        parent=model.rootItem(),
    )


def make_spectrum_1d(calculation):
    xaxis = calculation.axes.xaxis
    x = np.linspace(xaxis.start.value, xaxis.stop.value, xaxis.npoints.value + 1)
    # A narrow peak, so that the Gaussian broadening lowers its maximum.
    signal = np.exp(-((x - x.mean()) ** 2) / 0.01)
    spectrum = Spectrum1D(parent=calculation.spectra.toPlot, name="Absorption")
    spectrum.raw = np.column_stack([x, np.zeros_like(x), signal])
    spectrum.process()
    return spectrum


def make_spectrum_2d(calculation):
    nx = calculation.axes.xaxis.npoints.value + 1
    ny = calculation.axes.yaxis.npoints.value + 1
    signal = np.zeros((nx, ny), dtype=np.float64)
    signal[nx // 2, ny // 2] = 1.0
    # The 2D signal is read from raw[:, 2::2].
    columns = [np.zeros(nx), np.zeros(nx)]
    for column in signal.T:
        columns.extend([column, np.zeros(nx)])
    spectrum = Spectrum2D(parent=calculation.spectra.toPlot, name="Resonant Inelastic")
    spectrum.raw = np.column_stack(columns)
    spectrum.process()
    return spectrum


def test_maximum_normalization_holds_after_gaussian_1d():
    model = TreeModel()
    calculation = make_calculation(model)
    calculation.axes.normalization.value = "Maximum"
    spectrum = make_spectrum_1d(calculation)

    calculation.axes.xaxis.gaussian.value = 2.0

    assert np.abs(spectrum.signal).max() == pytest.approx(1.0)


def test_area_normalization_holds_after_gaussian_1d():
    model = TreeModel()
    calculation = make_calculation(model)
    calculation.axes.normalization.value = "Area"
    spectrum = make_spectrum_1d(calculation)

    calculation.axes.xaxis.gaussian.value = 2.0

    area = np.abs(np.trapezoid(spectrum.signal, spectrum.x))
    assert area == pytest.approx(1.0)


def test_maximum_normalization_holds_after_gaussian_2d():
    model = TreeModel()
    calculation = make_calculation(model, experiment="RIXS", edge="L2,3-M4,5 (2p3d)")
    calculation.axes.xaxis.npoints._value = 40
    calculation.axes.yaxis.npoints._value = 40
    calculation.axes.normalization.value = "Maximum"
    spectrum = make_spectrum_2d(calculation)

    calculation.axes.xaxis.gaussian.value = 2.0
    calculation.axes.yaxis.gaussian.value = 2.0

    assert np.abs(spectrum.signal).max() == pytest.approx(1.0)
