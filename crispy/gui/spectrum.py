# coding: utf-8

import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg
                                                as FigureCanvas)


class Spectrum(object):

    _defaults = {'dpi': 100,
                 'alpha': 0.0,
                 'canvas': None,
                 'figure': None,
                 'ax': None}

    def __init__(self):
        self.__dict__.update(self._defaults)

        # Create the figure and canvas.
        self.fig = plt.figure()
        self.fig.set_dpi(self.dpi)
        self.fig.patch.set_alpha(self.alpha)
        self.canvas = FigureCanvas(self.fig)

    def clear(self):
        if self.ax:
            self.ax.cla()

    def plot(self, x, y, label=None):
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.plot(x, y, '-', label=label)

        self.ax.grid(True)
        self.ax.yaxis.set_ticklabels([])
        self.ax.set_xlabel('Energy (eV)')
        self.ax.set_ylabel('Absorbtion crossection (a.u.)')
        self.ax.legend(framealpha=self.alpha)
        self.ax.patch.set_alpha(self.alpha)

        self.canvas.draw()

    def export(self):
        pass
