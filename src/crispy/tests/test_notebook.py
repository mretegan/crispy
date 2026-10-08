"""Tests for the notebook API."""

import pytest

from crispy import notebook
from crispy.models import TreeModel
from crispy.notebook import Hamiltonian, resolve_edge
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
    assert resolve_edge(edge) == expected


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


def test_set_parameter_rejects_unknown_names(model):
    calculation = Calculation(
        symbol="Ni",
        charge="2+",
        symmetry="Oh",
        experiment="XAS",
        edge="L2,3 (2p)",
        parent=model.rootItem(),
    )
    hamiltonian = Hamiltonian(calculation.hamiltonian)

    hamiltonian.set_parameter("Fk", 0.7)
    hamiltonian.set_parameter("ζ(3d)", 0.5, hamiltonian_name="Final Hamiltonian")

    with pytest.raises(ValueError, match="Ea2"):
        hamiltonian.set_parameter("Ea2(4f)", 0.4)
    with pytest.raises(ValueError, match="Missing"):
        hamiltonian.set_parameter("ζ(3d)", 0.5, hamiltonian_name="Missing")


def test_calculation_and_axis_reject_unknown_names(qapp):
    calc = notebook.calculation("Ni2+", "Oh", "XAS", "L2,3 (2p)")

    calc.set_parameter("Temperature", 300)
    calc.xaxis.set_parameter("Gaussian", 0.2)

    with pytest.raises(ValueError, match="Temperatur"):
        calc.set_parameter("Temperatur", 300)
    with pytest.raises(ValueError, match="Gausian"):
        calc.xaxis.set_parameter("Gausian", 0.2)
