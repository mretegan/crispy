"""Tests for the notebook API."""

import pytest

from crispy.models import TreeModel
from crispy.notebook import Hamiltonian, _resolve_edge
from crispy.quanty.calculation import Calculation


@pytest.fixture
def model(qapp):
    return TreeModel()


@pytest.mark.parametrize(
    ("edge", "expected"),
    [
        ("Kalpha (1s2p)", "Kα (1s2p)"),  # noqa: RUF001
        ("Kα (1s2p)", "Kα (1s2p)"),  # noqa: RUF001
        ("Kbeta (1s3p)", "Kβ (1s3p)"),
        ("L2,3 (2p)", "L2,3 (2p)"),
    ],
)
def test_resolve_edge_accepts_ascii_names(edge, expected):
    assert _resolve_edge(edge) == expected


@pytest.mark.parametrize("name", ["zeta(3d)", "ζ(3d)"])
def test_set_parameter_accepts_ascii_names(model, name):
    calculation = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="XAS",
        edge="L2,3 (2p)",
        parent=model.rootItem(),
    )

    Hamiltonian(calculation.hamiltonian).set_parameter(name, 0.5)

    values = [p.value for p in calculation.hamiltonian.findChild("ζ(3d)")]
    assert values
    assert all(value == 0.5 for value in values)
