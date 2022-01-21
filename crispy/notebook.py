# coding: utf-8
###################################################################
# Copyright (c) 2016-2022 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""The module provides an easy to use API to run calculations in Jupyter notebooks."""

from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation as _Calculation, Element


def prettify(data, level=0):
    output = str()
    indent = 2 * level * " "
    for key, value in data.items():
        if isinstance(value, dict):
            output += f"{indent}{key}:\n"
            output += prettify(value, level + 1)
        else:
            if isinstance(value, bool):
                value = "True" if value else "False"
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

    def print(self):
        print(self)

    def __iter__(self):
        return iter(self._terms)

    def __str__(self):
        data = Tree()
        for term in self._terms:
            data[term.name] = term.isEnabled()
        return prettify(data)


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

    def print(self):
        print(self)

    def __str__(self):
        data = Tree()
        general_data = Tree()
        general_data["Fk"] = self._hamiltonian.fk.value
        general_data["Gk"] = self._hamiltonian.gk.value
        general_data["Zeta"] = self._hamiltonian.zeta.value
        general_data["Number of States"] = self._hamiltonian.numberOfStates.value
        general_data[
            "Number of Configurations"
        ] = self._hamiltonian.numberOfConfigurations.value
        data["General"] = general_data
        for term in self._hamiltonian.terms.children():
            for hamiltonian in term.children():
                for parameter in hamiltonian.children():
                    parameter_data = [parameter.value]
                    scale_factor = getattr(parameter, "scaleFactor", None)
                    if scale_factor is not None:
                        parameter_data.append(scale_factor)
                    data["Terms"][term.name][hamiltonian.name][
                        parameter.name
                    ] = parameter_data
        return prettify(data)


class Axis:
    def __init__(self, axis):
        self._axis = axis

    def set_parameter(self, name=None, value=None):
        if name is None or value is None:
            return
        for parameter in self._axis.__dict__.values():
            if getattr(parameter, "name", None) == name:
                parameter.value = value

    def print(self):
        print(self)

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


class Spectra:
    def __init__(self, spectra):
        self.spectra = spectra
        self.has_data = False

    def enable(self, name=None):
        for spectrum in self.spectra.toCalculate.all:
            if spectrum.name == name:
                spectrum.enable()

    def disable(self, name=None):
        for spectrum in self.spectra.toCalculate.all:
            if spectrum.name == name:
                spectrum.disable()

    def get_calculated_data(self):
        if not self.has_data:
            return None
        data = Tree()
        for spectrum in self.spectra.toPlot.children():
            data[spectrum.name] = {
                "x": spectrum.x,
                "signal": spectrum.signal,
                "suffix": spectrum.suffix,
                "raw": spectrum,
            }
            if getattr(spectrum, "y", None) is not None:
                data[spectrum.name].update({"y": spectrum.y})
        return data

    def plot(self, spectra=None, ax=None):
        if ax is None:
            return
        for data in self.get_calculated_data().values():
            spectrum = data["raw"]
            if spectra is not None and spectrum.name not in spectra:
                continue
            ax.plot(spectrum.x, spectrum.signal, label=spectrum.name)

    def print(self):
        print(self)

    def __str__(self):
        data = Tree()
        for spectrum in self.spectra.toCalculate.all:
            data[spectrum.name] = spectrum.isEnabled()
        return prettify(data)


class Calculation:
    def __init__(self, element, symmetry, experiment, edge):
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
            if getattr(parameter, "name", None) == name:
                return parameter.value
            return None

    def get_output(self):
        return self._calculation.output

    def run(self):
        self._calculation.runner.output = str()
        self._calculation.run()
        self._calculation.runner.waitForFinished(-1)
        self.spectra.has_data = True

    def print(self):
        print(self)

    def __str__(self):
        data = {
            "Basename": self._calculation.value,
            "Temperature": self._calculation.temperature.value,
            "Magnetic Field": self._calculation.magneticField.value,
        }
        return prettify(data)


def calculation(element="Ni2+", symmetry="Oh", experiment="XAS", edge="L2,3 (2p)"):
    """Returns a Quanty calculation object.

    :param element:
    """
    return Calculation(element, symmetry, experiment, edge)


def main():
    pass


if __name__ == "__main__":
    main()
