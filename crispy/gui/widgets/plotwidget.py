# coding: utf-8

import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
            FigureCanvasQTAgg as FigureCanvas,
            NavigationToolbar2QT as NavigationToolbar)

from PyQt5.QtWidgets import QWidget


class PlotWidget(FigureCanvas):

    _defaults = {'dpi': 72,
                 'alpha': 0.0,
                 'canvas': None,
                 'figure': None,
                 'ax': None}

    def __init__(self, *args):
        self.__dict__.update(self._defaults)

        # Set the matplotlib style.
        plt.style.use('bmh')

        # Create the figure and canvas.
        self.fig = Figure(dpi=self.dpi, facecolor='w')
        super(PlotWidget, self).__init__(self.fig)

    def plot(self, x, y, label=None):
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.patch.set_alpha(self.alpha)

        self.ax.plot(x, y, '-', label=label)

        self.ax.grid(True)
        self.ax.yaxis.set_ticklabels([])
        self.ax.set_xlabel('Energy (eV)')
        self.ax.set_ylabel('Absorbtion crossection (a.u.)')
        self.ax.legend(framealpha=self.alpha)
        self.fig.tight_layout()
        self.draw()

    def clear(self):
        if self.ax:
            self.ax.cla()

    def export(self):
        pass
