###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""The module provides an easy to use API to run calculations in Jupyter notebooks."""

from crispy.config import Config as _Config
from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation as _Calculation
from crispy.quanty.calculation import Element


def prettify(data, level=0):
    output = ""
    indent = 2 * level * " "
    for key, value in data.items():
        if isinstance(value, dict):
            output += f"{indent}{key}:\n"
            output += prettify(value, level + 1)
        else:
            if isinstance(value, bool):
                value = "✓︎" if value else "✗"
            output += f"{indent}{key}: {value}"
        if key != list(data)[-1]:
            output += "\n"
    return output


class Tree(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


class Terms:
    def __init__(self, value):
        self._terms = value

    def enable(self, name):
        for term in self._terms:
            if name in (term.name, "All"):
                term.enable()

    def disable(self, name):
        for term in self._terms:
            if term.name == name:
                term.disable()

    def __iter__(self):
        return iter(self._terms)

    def __str__(self):
        data = Tree()
        for term in self._terms:
            data[term.name] = term.isEnabled()
        return prettify(data)

    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else "...")


class Hamiltonian:
    def __init__(self, hamiltonian):
        self._hamiltonian = hamiltonian
        self.terms = Terms(self._hamiltonian.terms.children())

    def set_parameter(
        self, name=None, value=None, scale_factor=None, hamiltonian_name=None
    ):
        if name is None or value is None:
            return
        if name in ["Fk", "Gk", "Zeta"]:
            parameter = getattr(self._hamiltonian, name.lower(), None)
            if parameter is not None:
                parameter.value = value
                parameter.updateIndividualScaleFactors(value)

        if name == "Number of Configurations":
            self._hamiltonian.numberOfConfigurations.value = value

        if name == "Number of States":
            self._hamiltonian.numberOfStates.value = value

        parameters = list(self._hamiltonian.findChild(name))
        for parameter in parameters:
            hamiltonian = parameter.parent()
            if hamiltonian_name is None:
                pass
            elif hamiltonian_name not in hamiltonian.name:
                continue
            if parameter.name == name:
                if value is not None:
                    parameter.value = value
                if scale_factor is not None:
                    parameter.scaleFactor = scale_factor

    def __str__(self):
        data = Tree()
        general_data = Tree()
        general_data["Fk"] = self._hamiltonian.fk.value
        general_data["Gk"] = self._hamiltonian.gk.value
        general_data["Zeta"] = self._hamiltonian.zeta.value
        general_data["Number of States"] = self._hamiltonian.numberOfStates.value
        general_data["Number of Configurations"] = (
            self._hamiltonian.numberOfConfigurations.value
        )
        data["General"] = general_data
        for term in self._hamiltonian.terms.children():
            for hamiltonian in term.children():
                for parameter in hamiltonian.children():
                    parameter_data = [parameter.value]
                    scale_factor = getattr(parameter, "scaleFactor", None)
                    if scale_factor is not None:
                        parameter_data.append(scale_factor)
                    data["Terms"][term.name][hamiltonian.name][parameter.name] = (
                        parameter_data
                    )
        return prettify(data)

    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else "...")


class Axis:
    def __init__(self, axis):
        self._axis = axis

    def set_parameter(self, name=None, value=None):
        if name is None or value is None:
            return
        for parameter in self._axis.__dict__.values():
            if getattr(parameter, "name", None) == name:
                parameter.value = value

    def __str__(self):
        data = Tree()
        data[self._axis.name] = {
            "Start": self._axis.start.value,
            "Stop": self._axis.stop.value,
            "Number of Points": self._axis.npoints.value,
            "Gaussian": self._axis.gaussian.value,
            "Lorentzian": self._axis.lorentzian.value,
        }
        return prettify(data)

    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else "...")


class Spectra:
    def __init__(self, spectra):
        self._spectra = spectra
        self.has_data = False

    def enable(self, name=None):
        for spectrum in self._spectra.toCalculate.all:
            if spectrum.name == name:
                spectrum.enable()

    def disable(self, name=None):
        for spectrum in self._spectra.toCalculate.all:
            if spectrum.name == name:
                spectrum.disable()

    def get_all_calculated(self):
        if not self.has_data:
            return None
        data = []
        for spectrum in self._spectra.toPlot.all:
            data.append(spectrum)
        return data

    def plot(self, spectra=None, ax=None):
        calculation = self._spectra.parent()
        i = calculation.childPosition()
        if ax is None:
            return
        for spectrum in self.get_all_calculated():
            if spectra is not None and spectrum.name not in spectra:
                continue
            ax.plot(
                spectrum.x,
                spectrum.signal,
                label=spectrum.name,
                color=f"C{i}",
                linestyle=spectrum.lineStyle,
            )

    def __str__(self):
        data = Tree()
        for spectrum in self._spectra.toCalculate.all:
            data[spectrum.name] = spectrum.isEnabled()
        return prettify(data)

    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else "...")


class Calculation:
    def __init__(
        self, element="Ni2+", symmetry="Oh", experiment="XAS", edge="L2,3 (2p)"
    ):
        config = _Config()
        config.prune()

        element = Element(parent=None, value=element)
        self._model = TreeModel()
        self._calculation = _Calculation(
            element.symbol,
            element.charge,
            symmetry,
            experiment,
            edge,
            parent=self._model.rootItem(),
        )
        self.xaxis = Axis(self._calculation.axes.xaxis)
        self.hamiltonian = Hamiltonian(self._calculation.hamiltonian)
        self.spectra = Spectra(self._calculation.spectra)

    def __dir__(self):
        return (
            "get_input",
            "get_output",
            "hamiltonian",
            "output",
            "run",
            "set_parameter",
            "spectra",
            "xaxis",
        )

    def set_parameter(self, name=None, value=None):
        if name is None or value is None:
            return
        if name == "Basename":
            self._calculation.value = value
        else:
            for parameter in self._calculation.__dict__.values():
                if getattr(parameter, "name", None) == name:
                    parameter.value = value

    def get_parameter(self, name=None):
        if name is None:
            return None
        if name == "Basename":
            return self._calculation.value
        for parameter in self._calculation.__dict__.values():
            return parameter.value if getattr(parameter, "name", None) == name else None

    def get_input(self):
        return self._calculation.input

    def get_output(self):
        return self._calculation.output

    def run(self):
        self._calculation.runner.output = ""
        self._calculation.run()
        self._calculation.runner.waitForFinished(-1)
        self.spectra.has_data = True

    def __str__(self):
        data = {
            "Basename": self._calculation.value,
            "Temperature": self._calculation.temperature.value,
            "Magnetic Field": self._calculation.magneticField.value,
        }
        return prettify(data)

    def _repr_pretty_(self, p, cycle):
        p.text(str(self) if not cycle else "...")


def calculation(element, symmetry, experiment, edge):
    """Returns a Quanty calculation object.

    :param element:
    """
    return Calculation(element, symmetry, experiment, edge)


class Config:
    def default(self):
        settings = _Config()
        settings.default()

    def set_setting(self, name, value):
        if name == "Shift Spectra":
            name = "ShiftSpectra"
        elif name == "Remove Files":
            name = "RemoveFiles"
        else:
            print(f"Unknown setting: {name}")
            return

        settings = _Config().read()
        settings.setValue(f"Quanty/{name}", value)
        settings.sync()


def main():
    pass


if __name__ == "__main__":
    main()
