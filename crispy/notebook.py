# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""The module provides an easy to use API to run calculations from Jupyter notebooks."""

from crispy.models import TreeModel
from crispy.quanty.calculation import Calculation as _Calculation, Element


def prettify(data, level=0):
    output = str()
    indent = 2 * level * " "
    for key, value in data.items():
        if isinstance(value, dict):
            output += f"{indent}{key}\n"
            output += prettify(value, level + 1)
        else:
            if isinstance(value, bool):
                value = "\u2611" if value else "\u2610"
            output += f"{indent}{key}: {value}\n"
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
        self.terms = value

    def enable(self, name):
        for term in self.terms:
            if name in (term.name, "all"):
                term.enable()

    def disable(self, name):
        for term in self.terms:
            if term.name == name:
                term.disable()

    def show(self):
        return self

    def __repr__(self):
        data = Tree()
        for term in self.terms:
            data[term.name] = term.isEnabled()
        return prettify(data)


class Hamiltonian:
    def __init__(self, hamiltonian):
        self.hamiltonian = hamiltonian
        self.terms = Terms(self.hamiltonian.terms.children())

    def parameters(self):
        return self

    def parameter(self, name=None, value=None, scale_factor=None, where=None):
        if name is None:
            return self

        if name in ["Fk", "Gk", "Zeta"]:
            parameter = getattr(self.hamiltonian, name.lower(), None)
            if parameter is not None:
                parameter.value = value
                parameter.updateIndividualScaleFactors(value)
                return True

        if name == "Number of Configurations":
            self.hamiltonian.numberOfConfigurations.value = value
            return True

        if name == "Number of States":
            self.hamiltonian.numberOfStates.value = value
            return True

        parameters = list(self.hamiltonian.findChild(name))
        for parameter in parameters:
            hamiltonian = parameter.parent()
            if where is None:
                pass
            elif where not in hamiltonian.name:
                continue
            if parameter.name == name:
                if value is not None:
                    parameter.value = value
                if scale_factor is not None:
                    parameter.scaleFactor = scale_factor
        return True

    def __repr__(self):
        data = Tree()
        general_data = Tree()
        general_data["Fk"] = self.hamiltonian.fk.value
        general_data["Gk"] = self.hamiltonian.gk.value
        general_data["Zeta"] = self.hamiltonian.zeta.value
        general_data["Number of States"] = self.hamiltonian.numberOfStates.value
        general_data[
            "Number of Configurations"
        ] = self.hamiltonian.numberOfConfigurations.value
        data["General"] = general_data
        for term in self.hamiltonian.terms.children():
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
        self.axis = axis

    def parameters(self):
        return self

    def parameter(self, name=None, value=None):
        if name is None or value is None:
            return self
        for parameter in self.axis.__dict__.values():
            if getattr(parameter, "name", None) == name:
                parameter.value = value
        return True

    def __repr__(self):
        data = Tree()
        data[self.axis.name] = {
            "Start": self.axis.start.value,
            "Stop": self.axis.stop.value,
            "Number of points": self.axis.npoints.value,
            "Gaussian": self.axis.gaussian.value,
            "Lorentzian": self.axis.lorentzian.value,
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

    def calculated(self):
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
        for data in self.calculated().values():
            spectrum = data["raw"]
            if spectra is not None and spectrum.name not in spectra:
                continue
            ax.plot(spectrum.x, spectrum.signal, label=spectrum.suffix)

    def show(self):
        return self

    def __repr__(self):
        if not self.has_data:
            data = Tree()
            for spectrum in self.spectra.toCalculate.all:
                data[spectrum.name] = spectrum.isEnabled()
            return prettify(data)
        return prettify(self.calculated())


class Calculation:
    def __init__(self, element, symmetry, experiment, edge):
        element = Element(parent=None, value=element)

        self.model = TreeModel()
        self.calculation = _Calculation(
            element.symbol,
            element.charge,
            symmetry,
            experiment,
            edge,
            parent=self.model.rootItem(),
        )
        self.hamiltonian = Hamiltonian(self.calculation.hamiltonian)

        self.xaxis = Axis(self.calculation.axes.xaxis)
        self.spectra = Spectra(self.calculation.spectra)

    def __dir__(self):
        return (
            "xaxis",
            "hamiltonian",
            "run",
            "output",
            "spectra",
        )

    def parameters(self):
        return self

    def parameter(self, name=None, value=None):
        if name is None or value is None:
            return self
        for parameter in self.calculation.__dict__.values():
            if getattr(parameter, "name", None) == name:
                parameter.value = value
        return True

    def temperature(self, value=None):
        if value is None:
            return self.calculation.temperature.value
        self.calculation.temperature.value = value
        return True

    def magnetic_field(self, value=None):
        if value is None:
            return self.calculation.magneticField.value
        self.calculation.magneticField.value = value
        return True

    def run(self):
        self.calculation.runner.output = str()
        self.calculation.run()
        self.calculation.runner.waitForFinished()
        self.spectra.has_data = True
        return True

    def output(self):
        print(self.calculation.output)

    def __repr__(self):
        data = {
            "Temperature": self.calculation.temperature.value,
            "Magnetic Field": self.calculation.magneticField.value,
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
