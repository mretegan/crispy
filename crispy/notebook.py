# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Running calculations in the notebook."""

import logging

import matplotlib.pyplot as plt

from crispy.gui.models import TreeModel
from crispy.gui.quanty.calculation import Calculation, Element
from crispy.main import setUpLoggers

logger = logging.getLogger("crispy.notebook")


class Quanty:
    def __init__(self, element, symmetry, experiment, edge):
        element = Element(parent=None, value=element)

        self.model = TreeModel()
        self.calculation = Calculation(
            element.symbol,
            element.charge,
            symmetry,
            experiment,
            edge,
            parent=self.model.rootItem(),
        )

    def __dir__(self):
        return sorted(("run", "spectra"))

    @property
    def spectra(self):
        return self.calculation.spectra.toPlot.children()

    def run(self):
        self.calculation.run()
        self.calculation.runner.waitForFinished()

    def plot(self, ax=None):
        if ax is None:
            _, ax = plt.subplots()
        for spectrum in self.spectra:
            ax.plot(spectrum.x, spectrum.signal, label=spectrum.suffix)
        ax.legend()


def main():
    setUpLoggers()

    calculation = Quanty("Fe2+", "D3h", "XAS", "L2,3 (2p)")
    calculation.run()
    calculation.plot()

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
