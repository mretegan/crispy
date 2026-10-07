"""Tests for widget mappings."""

import pytest
from silx.gui.qt import QCoreApplication, QDataWidgetMapper, QEvent, QLocale

from crispy.items import BoolItem, ComboItem, DoubleItem
from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation
from crispy.views import Delegate, clearMappings, setMappings
from crispy.widgets import CheckBox, ComboBox, DoubleLineEdit, LineEdit


@pytest.fixture
def model(qapp):
    return TreeModel()


def test_mapping_rejects_detached_item(qtbot):
    widget = DoubleLineEdit()
    qtbot.addWidget(widget)
    item = DoubleItem(value=1.0)

    with pytest.raises(ValueError, match="without a model"):
        setMappings(((widget, item),))
    assert not widget.findChildren(QDataWidgetMapper)


@pytest.mark.parametrize("column", [-1, 2])
def test_mapping_rejects_invalid_column(model, qtbot, column):
    widget = DoubleLineEdit()
    qtbot.addWidget(widget)
    item = DoubleItem(value=1.0, parent=model.rootItem())
    with pytest.raises(ValueError, match=f"Cannot map column {column}"):
        setMappings(((widget, item),), column=column)
    assert not widget.findChildren(QDataWidgetMapper)


def test_mapping_edits_item_name(model, qtbot):
    widget = LineEdit()
    qtbot.addWidget(widget)
    item = DoubleItem(value=1.0, name="Original", parent=model.rootItem())
    mappers = setMappings(((widget, item),), column=0)

    assert widget.text() == "Original"
    widget.setText("Updated")
    assert mappers[0].submit()
    assert item.name == "Updated"
    assert item.value == 1.0
    clearMappings(mappers)


def test_mapping_edits_scale_factor(model, qtbot):
    calculation = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="XAS",
        edge="L2,3 (2p)",
        parent=model.rootItem(),
    )
    atomic = next(
        term
        for term in calculation.hamiltonian.terms.children()
        if term.name == "Atomic"
    )
    parameter = next(iter(atomic.parameters))
    parameter.scaleFactor = 0.75
    value = parameter.value
    widget = DoubleLineEdit()
    qtbot.addWidget(widget)
    mappers = setMappings(((widget, parameter),), column=2)

    assert QLocale().toDouble(widget.text()) == (0.75, True)
    widget.setText(QLocale().toString(0.5))
    assert mappers[0].submit()
    assert parameter.scaleFactor == 0.5
    assert parameter.value == value

    parameter.scaleFactor = 0.8
    assert QLocale().toDouble(widget.text()) == (0.8, True)
    clearMappings(mappers)


def test_checkbox_mapping_preserves_other_connections(model, qtbot):
    widget = CheckBox()
    qtbot.addWidget(widget)
    item = BoolItem(value=False, parent=model.rootItem())
    notifications = []
    widget.stateChanged.connect(notifications.append)
    mappers = setMappings(((widget, item),))

    widget.click()
    assert item.value is True
    assert len(notifications) == 1

    clearMappings(mappers)
    widget.click()
    assert item.value is True
    assert len(notifications) == 2
    assert mappers == []
    clearMappings(mappers)


def test_combo_mapping_preserves_other_connections(model, qtbot):
    widget = ComboBox()
    qtbot.addWidget(widget)
    item = ComboItem(value="first", parent=model.rootItem())
    item.items = ["first", "second"]
    notifications = []
    widget.currentTextChanged.connect(notifications.append)
    mappers = setMappings(((widget, item),))

    widget.setCurrentText("second")
    assert item.value == "second"
    assert notifications == ["second"]

    clearMappings(mappers)
    widget.setCurrentText("first")
    assert item.value == "second"
    assert notifications == ["second", "first"]


def test_repopulation_deletes_old_mappers_and_delegates(model, qtbot):
    widget = DoubleLineEdit()
    qtbot.addWidget(widget)
    item = DoubleItem(value=1.0, parent=model.rootItem())
    mappers = []

    for _ in range(3):
        clearMappings(mappers)
        mappers = setMappings(((widget, item),))
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        assert len(widget.findChildren(QDataWidgetMapper)) == 1
        assert len(widget.findChildren(Delegate)) == 1

    clearMappings(mappers)
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    assert not widget.findChildren(QDataWidgetMapper)
    assert not widget.findChildren(Delegate)
