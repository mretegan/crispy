"""Tests for the axis widgets."""

import pytest

from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation
from crispy.quanty.main import AxisWidget


@pytest.fixture
def calculation(qapp):
    model = TreeModel()
    state = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="RIXS",
        edge="L2,3-M4,5 (2p3d)",
        parent=model.rootItem(),
    )
    yield state


@pytest.fixture
def axis_widget(qtbot):
    widget = AxisWidget()
    qtbot.addWidget(widget)
    return widget


@pytest.mark.parametrize("checked", [True, False])
def test_analyze_checkbox_reads_and_writes_value(calculation, axis_widget, checked):
    analyze = calculation.axes.yaxis.photon.analyze
    analyze.value = checked

    axis_widget.populate(calculation.axes.yaxis)
    checkbox = axis_widget.analyzeCheckBox
    assert not checkbox.isHidden()
    assert checkbox.isChecked() is checked

    checkbox.click()
    assert analyze.value is not checked
    checkbox.click()
    assert analyze.value is checked


def test_analyze_checkbox_repopulation_preserves_value(calculation, axis_widget):
    axis = calculation.axes.yaxis
    axis_widget.populate(axis)
    axis.photon.analyze.value = False

    for _ in range(3):
        axis_widget.populate(axis)
        assert not axis_widget.analyzeCheckBox.isChecked()
        assert axis.photon.analyze.value is False

    axis_widget.analyzeCheckBox.click()
    assert axis.photon.analyze.value is True


def test_analyze_checkbox_hidden_for_incident_photon(calculation, axis_widget):
    axis_widget.populate(calculation.axes.yaxis)
    axis_widget.populate(calculation.axes.xaxis)
    assert axis_widget.analyzeCheckBox.isHidden()


def test_analyze_checkbox_edits_current_calculation(calculation, axis_widget):
    axis_widget.populate(calculation.axes.yaxis)
    new = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="RIXS",
        edge="L2,3-M4,5 (2p3d)",
        parent=calculation.parent(),
    )
    new.axes.yaxis.photon.analyze.value = False

    axis_widget.populate(new.axes.yaxis)
    assert not axis_widget.analyzeCheckBox.isChecked()
    for checked in (True, False):
        axis_widget.analyzeCheckBox.click()
        assert new.axes.yaxis.photon.analyze.value is checked
        assert calculation.axes.yaxis.photon.analyze.value is True
