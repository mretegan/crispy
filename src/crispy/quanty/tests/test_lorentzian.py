#!/usr/bin/env python3

"""Tests for the energy dependent Lorentzian broadening."""

from math import ceil

import pytest
from silx.gui.qt import QDialogButtonBox, QLocale, QPoint

from crispy.models import TreeModel
from crispy.notebook import Axis as NotebookAxis
from crispy.quanty.calculation import Calculation
from crispy.quanty.lorentzian import (
    REMOVE_COLUMN,
    LorentzianDialog,
    formatNumber,
    stepPoints,
)

STEP = [(850.0, 0.48), (860.0, 0.48), (860.0, 0.78), (870.0, 0.78)]


def make_calculation(parent):
    return Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="XAS",
        edge="L2,3 (2p)",
        parent=parent,
    )


@pytest.fixture
def calculation(qapp):
    # Keep a reference to the model while the test runs.
    model = TreeModel()
    yield make_calculation(model.rootItem())


@pytest.fixture
def lorentzian(calculation):
    return calculation.axes.xaxis.lorentzian


def test_replacements_constant(lorentzian):
    axis = lorentzian.parent()
    lorentzian.value = 0.5
    replacements = lorentzian.replacements
    expected = f"{{{{{axis.start.value}, 0.5}}, {{{axis.stop.value}, 0.5}}}}"
    assert replacements["Lorentzian"] == expected
    assert replacements["Gamma"] == 0.1


def test_replacements_variable(lorentzian):
    lorentzian.points.value = STEP
    expected = "{{850.0, 0.48}, {860.0, 0.48}, {860.0, 0.78}, {870.0, 0.78}}"
    assert lorentzian.replacements["Lorentzian"] == expected


def test_input_contains_lorentzian_table(calculation):
    calculation.axes.xaxis.lorentzian.points.value = STEP
    table = "{{850.0, 0.48}, {860.0, 0.48}, {860.0, 0.78}, {870.0, 0.78}}"
    assert f"Lorentzian = {table} --" in calculation.input


def test_points_sorts_and_keeps_order_of_equal_energies(lorentzian):
    lorentzian.points.value = [(870, 0.78), (860, 0.48), (860, 0.78), (850, 0.48)]
    assert lorentzian.points.value == STEP
    assert lorentzian.isVariable


@pytest.mark.parametrize(
    "points",
    [[], [(850.0, 0.48), (860.0, 0.0)], [(860.0, -0.05)]]
    + [[(value, 0.5)] for value in (float("nan"), float("inf"), -float("inf"))]
    + [[(860.0, value)] for value in (float("nan"), float("inf"), -float("inf"))],
)
def test_points_rejects_invalid_input(lorentzian, points):
    lorentzian.points.value = STEP
    with pytest.raises(ValueError):
        lorentzian.points.value = points
    assert lorentzian.points.value == STEP


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_value_rejects_nonfinite_input(lorentzian, value):
    lorentzian.points.value = STEP
    previous = lorentzian.value
    with pytest.raises(ValueError, match="finite"):
        lorentzian.value = value
    assert lorentzian.value == previous
    assert lorentzian.points.value == STEP


@pytest.mark.parametrize("value", [0.0, -0.05])
def test_value_rejects_nonpositive_input(lorentzian, value):
    previous = lorentzian.value
    with pytest.raises(ValueError, match="positive"):
        lorentzian.value = value
    assert lorentzian.value == previous


@pytest.mark.parametrize("value", [0.05, 0.005, 0.0005])
def test_narrow_constant_broadening_increases_grid(calculation, value):
    axis = calculation.axes.xaxis
    axis.lorentzian.value = value
    assert axis.lorentzian.replacements["Gamma"] == value
    assert axis.npoints.value == axis.npoints.minimum
    assert axis.interval <= value / 5
    assert f"Gamma = {value} --" in calculation.input


def test_narrow_variable_broadening_increases_grid(calculation):
    axis = calculation.axes.xaxis
    points = [(850.0, 0.005), (870.0, 0.05)]
    NotebookAxis(axis).set_parameter("Lorentzian", points)
    assert axis.lorentzian.points.value == points
    assert axis.lorentzian.replacements["Gamma"] == 0.005
    assert axis.interval <= 0.005 / 5


def test_broadening_preserves_finer_grid(calculation):
    axis = calculation.axes.xaxis
    axis.lorentzian.value = 0.005
    axis.npoints.value = 2 * axis.npoints.minimum
    previous = axis.npoints.value
    axis.lorentzian.value = 0.05
    assert axis.npoints.value == previous


def test_wider_constant_broadening_reduces_automatic_grid(calculation):
    axis = calculation.axes.xaxis
    axis.lorentzian.value = 0.005
    previous = axis.npoints.value
    axis.lorentzian.value = 0.05
    assert axis.npoints.value < previous
    assert axis.npoints.value == axis.npoints.minimum


def test_wider_variable_broadening_reduces_automatic_grid(calculation):
    axis = calculation.axes.xaxis
    axis.lorentzian.points.value = [(850.0, 0.005), (870.0, 0.05)]
    previous = axis.npoints.value
    axis.lorentzian.points.value = [(850.0, 0.05), (870.0, 0.1)]
    assert axis.npoints.value < previous
    assert axis.npoints.value == axis.npoints.minimum


def test_smaller_range_reduces_automatic_grid(calculation):
    axis = calculation.axes.xaxis
    axis.lorentzian.value = 0.005
    previous = axis.npoints.value
    axis.stop.value -= 5.0
    assert axis.npoints.value < previous
    assert axis.npoints.value == axis.npoints.minimum


def test_copied_automatic_grid_follows_broadening(calculation):
    calculation.axes.xaxis.lorentzian.value = 0.005
    model = TreeModel()
    other = make_calculation(model.rootItem())
    other.copyFrom(calculation)
    axis = other.axes.xaxis
    previous = axis.npoints.value
    axis.lorentzian.value = 0.05
    assert axis.npoints.value < previous
    assert axis.npoints.value == axis.npoints.minimum


@pytest.mark.parametrize("limit", ["start", "stop"])
def test_wider_range_increases_grid(calculation, limit):
    axis = calculation.axes.xaxis
    axis.lorentzian.value = 0.005
    previous = axis.npoints.value
    parameter = getattr(axis, limit)
    parameter.value += -5.0 if limit == "start" else 5.0
    assert axis.npoints.value > previous
    assert axis.interval <= 0.005 / 5


@pytest.mark.parametrize("axis_name", ["xaxis", "yaxis"])
def test_notebook_rejects_variable_broadening_for_rixs(qapp, axis_name):
    model = TreeModel()
    calculation = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="RIXS",
        edge="L2,3-M4,5 (2p3d)",
        parent=model.rootItem(),
    )
    axis = getattr(calculation.axes, axis_name)
    previous = axis.lorentzian.replacements
    npoints = axis.npoints.value
    with pytest.raises(ValueError, match="two-dimensional"):
        NotebookAxis(axis).set_parameter("Lorentzian", STEP)
    assert axis.lorentzian.points.value == []
    assert axis.lorentzian.replacements == previous
    assert axis.npoints.value == npoints


def test_value_clears_points(lorentzian):
    lorentzian.points.value = STEP
    lorentzian.value = 0.5
    assert lorentzian.points.value == []
    assert not lorentzian.isVariable


def test_npoints_minimum_uses_smallest_fwhm(calculation):
    axis = calculation.axes.xaxis
    axis.start.value = axis.stop.value - 0.37
    axis.lorentzian.points.value = [(850.0, 0.02), (870.0, 0.8)]
    expected = ceil(5 * (axis.stop.value - axis.start.value) / 0.02)
    assert axis.npoints.minimum == expected
    with pytest.raises(ValueError):
        axis.npoints.value = expected - 1


@pytest.mark.parametrize("axis_name", ["xaxis", "yaxis"])
def test_narrow_rixs_broadening_increases_grid(qapp, axis_name):
    model = TreeModel()
    calculation = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="RIXS",
        edge="L2,3-M4,5 (2p3d)",
        parent=model.rootItem(),
    )
    axis = getattr(calculation.axes, axis_name)
    axis.lorentzian.value = 0.005
    assert axis.lorentzian.replacements["Gamma"] == 0.005
    assert axis.interval <= 0.005 / 5
    previous = axis.npoints.value
    axis.lorentzian.value = 0.05
    assert axis.npoints.value < previous
    assert axis.npoints.value == axis.npoints.minimum


def test_data_shows_energy_dependence(lorentzian):
    assert lorentzian.data(1) == QLocale().toString(lorentzian.value)
    lorentzian.points.value = STEP
    assert lorentzian.data(1) == "Γ(E)"


def test_copy_from_copies_points(lorentzian, qapp):
    model = TreeModel()
    other = make_calculation(model.rootItem()).axes.xaxis.lorentzian
    lorentzian.points.value = STEP
    other.copyFrom(lorentzian)
    assert other.points.value == STEP
    assert other.points.value is not lorentzian.points.value


def test_step_points():
    assert stepPoints(860.0, 0.0, 0.48, 0.78) == [(860.0, 0.48), (860.0, 0.78)]
    assert stepPoints(860.0, 2.0, 0.48, 0.78) == [(859.0, 0.48), (861.0, 0.78)]


def test_notebook_axis(lorentzian):
    axis = NotebookAxis(lorentzian.parent())
    axis.set_parameter("Lorentzian", [(860.0, 0.78), (850.0, 0.48)])
    assert lorentzian.points.value == [(850.0, 0.48), (860.0, 0.78)]
    assert "Lorentzian: [(850.0, 0.48), (860.0, 0.78)]" in str(axis)

    axis.set_parameter("Lorentzian", 0.5)
    assert lorentzian.points.value == []
    assert lorentzian.value == 0.5


def test_dialog_prefills_table(lorentzian):
    axis = lorentzian.parent()
    value = lorentzian.value
    dialog = LorentzianDialog(lorentzian)
    assert not dialog.isVariable()
    assert dialog.value() == value

    dialog.variableRadioButton.setChecked(True)
    assert dialog.points() == [(axis.start.value, value), (axis.stop.value, value)]
    assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled()


def test_dialog_applies_step(lorentzian):
    dialog = LorentzianDialog(lorentzian)
    dialog.variableRadioButton.setChecked(True)
    dialog.stepEnergyLineEdit.setText(formatNumber(860.0))
    dialog.stepWidthLineEdit.setText(formatNumber(0.0))
    dialog.stepBelowLineEdit.setText(formatNumber(0.48))
    dialog.stepAboveLineEdit.setText(formatNumber(0.78))
    dialog.applyStepPushButton.click()
    assert dialog.points() == [(860.0, 0.48), (860.0, 0.78)]
    assert [m.getPosition() for m in dialog.markers] == [(860.0, 0.48), (860.0, 0.78)]


def test_dialog_sorts_and_validates_table(lorentzian):
    axis = lorentzian.parent()
    dialog = LorentzianDialog(lorentzian)
    dialog.variableRadioButton.setChecked(True)
    table = dialog.pointsTableWidget
    ok = dialog.buttonBox.button(QDialogButtonBox.Ok)

    # Move the first point after the last one.
    table.item(0, 0).setText(formatNumber(axis.stop.value + 1))
    assert dialog.points()[-1][0] == axis.stop.value + 1
    assert "outside" in dialog.messageLabel.text()
    assert ok.isEnabled()

    table.item(0, 1).setText(formatNumber(0.0))
    assert not ok.isEnabled()

    table.item(0, 1).setText("abc")
    assert not ok.isEnabled()
    assert dialog.messageLabel.text() == "Enter a number in each cell."


@pytest.mark.parametrize("text", ["nan", "inf", "-inf"])
@pytest.mark.parametrize("column", [0, 1])
def test_dialog_rejects_nonfinite_table_input(lorentzian, text, column):
    dialog = LorentzianDialog(lorentzian)
    dialog.variableRadioButton.setChecked(True)
    dialog.pointsTableWidget.item(0, column).setText(text)
    assert not dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled()
    assert not dialog.validate()[1]
    assert len(dialog.points()) == 1
    assert not lorentzian.isVariable


@pytest.mark.parametrize("text", ["nan", "inf", "-inf"])
def test_dialog_rejects_nonfinite_constant_input(lorentzian, text):
    dialog = LorentzianDialog(lorentzian)
    dialog.valueLineEdit.setText(text)
    assert dialog.value() is None
    assert not dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled()
    assert not dialog.validate()[1]


@pytest.mark.parametrize("variable", [False, True])
def test_dialog_accepts_narrow_broadening(lorentzian, variable):
    dialog = LorentzianDialog(lorentzian)
    dialog.valueLineEdit.setText(formatNumber(0.0005))
    dialog.variableRadioButton.setChecked(variable)
    assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled()
    assert dialog.validate()[1]
    if variable:
        assert all(fwhm == 0.0005 for _, fwhm in dialog.points())
    else:
        assert dialog.value() == 0.0005


def test_dialog_drag_preserves_narrow_fwhm(lorentzian, qtbot):
    lorentzian.points.value = [(850.0, 0.005), (870.0, 0.005)]
    dialog = LorentzianDialog(lorentzian)
    marker = dialog.markers[0]
    marker.setPosition(850.0, 0.0004)
    dialog.pointMoved(0, marker)
    qtbot.waitUntil(lambda: dialog.points()[0] == (850.0, 0.0004))
    assert dialog.validate()[1]


@pytest.mark.parametrize("text", ["nan", "inf", "-inf"])
@pytest.mark.parametrize(
    "field",
    [
        "stepEnergyLineEdit",
        "stepWidthLineEdit",
        "stepBelowLineEdit",
        "stepAboveLineEdit",
    ],
)
def test_dialog_rejects_nonfinite_step_input(lorentzian, text, field):
    dialog = LorentzianDialog(lorentzian)
    dialog.variableRadioButton.setChecked(True)
    previous = dialog.points()
    getattr(dialog, field).setText(text)
    dialog.applyStepPushButton.click()
    assert dialog.points() == previous
    assert "finite" in dialog.messageLabel.text()


def test_dialog_drag_rounds_fwhm_to_pixel(lorentzian, qtbot):
    lorentzian.points.value = [(850.0, 0.48), (870.0, 0.78)]
    dialog = LorentzianDialog(lorentzian)
    marker = dialog.markers[0]
    # One pixel of the FWHM axis is a few meV, so the drag keeps three decimals.
    marker.setPosition(850.0, 0.612345)
    dialog.pointMoved(0, marker)
    qtbot.waitUntil(lambda: dialog.points()[0] == (850.0, 0.612))
    assert dialog.pointsTableWidget.item(0, 1).text() == formatNumber(0.612)


def test_dialog_point_moves(lorentzian, qtbot):
    lorentzian.points.value = [(850.0, 0.48), (860.0, 0.48), (860.0, 0.78)]
    dialog = LorentzianDialog(lorentzian)

    # Move the upper side of the step (row 2) in both directions.
    point = next(m for m in dialog.markers if m.getPosition() == (860.0, 0.78))
    point.setPosition(865.004, 1.004)
    dialog.pointMoved(2, point)
    qtbot.waitUntil(
        lambda: dialog.points() == [(850.0, 0.48), (860.0, 0.48), (865.0, 1.004)]
    )

    # Move a point past its neighbor. The table sorts the rows again.
    point = next(m for m in dialog.markers if m.getPosition() == (850.0, 0.48))
    point.setPosition(862.0, 0.6)
    dialog.pointMoved(0, point)
    qtbot.waitUntil(
        lambda: dialog.points() == [(860.0, 0.48), (862.0, 0.6), (865.0, 1.004)]
    )

    # A drag below zero keeps the original positive FWHM.
    point = dialog.markers[0]
    point.setPosition(855.0, 0.0)
    assert point.getPosition() == (855.0, 0.48)


def test_dialog_plot_menu(lorentzian, qtbot):
    lorentzian.points.value = [(850.0, 0.48), (870.0, 0.78)]
    dialog = LorentzianDialog(lorentzian)
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)

    def pixel(energy, fwhm):
        x, y = dialog.plot.dataToPixel(energy, fwhm, check=False)
        return QPoint(round(x), round(y))

    # Away from the points, the menu can only add a point.
    [add] = dialog.plotMenu(pixel(860.0, 0.6)).actions()
    assert add.text() == "Add Point"
    add.trigger()
    points = dialog.points()
    assert len(points) == 3
    assert points[1] == pytest.approx((860.0, 0.6), abs=0.1)

    # On a point, the menu can also remove it.
    actions = dialog.plotMenu(pixel(850.0, 0.48)).actions()
    assert [action.text() for action in actions] == ["Add Point", "Remove Point"]
    actions[1].trigger()
    assert dialog.points() == points[1:]

    dialog.constantRadioButton.setChecked(True)
    assert dialog.plotMenu(pixel(860.0, 0.6)) is None


def test_dialog_add_and_remove_buttons(lorentzian):
    lorentzian.points.value = [(850.0, 0.48), (860.0, 0.6), (870.0, 0.78)]
    dialog = LorentzianDialog(lorentzian)
    table = dialog.pointsTableWidget

    # The new point copies the last point and gets a remove button.
    dialog.addPushButton.click()
    assert dialog.points()[-1] == (870.0, 0.78)
    assert table.cellWidget(3, REMOVE_COLUMN) is not None

    # A remove button removes its row and keeps the text of the other rows.
    table.item(2, 1).setText("abc")
    table.cellWidget(1, REMOVE_COLUMN).click()
    assert table.rowCount() == 3
    assert table.item(1, 1).text() == "abc"
    assert dialog.points() == [(850.0, 0.48), (870.0, 0.78)]


def test_dialog_plot_does_not_zoom(lorentzian, qtbot):
    lorentzian.points.value = [(850.0, 0.48), (870.0, 0.78)]
    dialog = LorentzianDialog(lorentzian)
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    plot = dialog.plot
    point = plot.dataToPixel(870.0, 0.78, check=False)
    # silx picks the items on the drawn canvas, so wait for the first draw.
    qtbot.waitUntil(lambda: any(True for _ in plot.pickItems(*point)))
    limits = plot.getXAxis().getLimits(), plot.getYAxis().getLimits()

    # A drag in an empty area and a wheel turn do not change the limits.
    x0, y0 = plot.dataToPixel(855.0, 0.2, check=False)
    x1, y1 = plot.dataToPixel(865.0, 0.4, check=False)
    plot.onMousePress(x0, y0, "left")
    plot.onMouseMove(x1, y1)
    plot.onMouseRelease(x1, y1, "left")
    plot.onMouseWheel(x1, y1, 15.0)
    assert (plot.getXAxis().getLimits(), plot.getYAxis().getLimits()) == limits

    # A drag on a point still moves it, in both directions.
    x1, y1 = plot.dataToPixel(868.0, 0.6, check=False)
    plot.onMousePress(*point, "left")
    plot.onMouseMove(x1, y1)
    plot.onMouseRelease(x1, y1, "left")
    qtbot.waitUntil(lambda: dialog.points()[1] == pytest.approx((868.0, 0.6), abs=0.02))


def test_dialog_plot_curves_ignore_clicks(lorentzian, qtbot):
    lorentzian.points.value = [(850.0, 0.48), (870.0, 0.78)]
    dialog = LorentzianDialog(lorentzian, overlay=([845.0, 880.0], [0.0, 1.0]))
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    plot = dialog.plot
    point = plot.dataToPixel(870.0, 0.78, check=False)
    # silx picks the items on the drawn canvas, so wait for the first draw.
    qtbot.waitUntil(lambda: any(True for _ in plot.pickItems(*point)))

    events = []
    plot.sigPlotSignal.connect(lambda event: events.append(event["event"]))
    # Click on the FWHM line and on the spectrum.
    positions = [
        plot.dataToPixel(860.0, 0.63, check=False),
        plot.dataToPixel(862.5, 0.5, axis="right", check=False),
    ]
    for x, y in positions:
        plot.onMousePress(x, y, "left")
        plot.onMouseRelease(x, y, "left")
    assert "curveClicked" not in events
    assert events.count("mouseClicked") == 2


def test_dialog_reset(lorentzian):
    lorentzian.points.value = STEP
    dialog = LorentzianDialog(lorentzian)
    dialog.reset()
    assert not dialog.isVariable()
    assert dialog.value() == lorentzian.parent().coreholeWidth
    assert dialog.pointsTableWidget.rowCount() == 0
