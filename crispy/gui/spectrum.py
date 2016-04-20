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

    def plot(self, x, y, title=None):
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.plot(x, y, '-')

        self.ax.grid(True)
        self.ax.yaxis.set_ticklabels([])
        if title:
            self.ax.set_title(title)
        self.ax.set_xlabel('Energy (eV)')
        self.ax.patch.set_alpha(self.alpha)

        self.canvas.draw()

    def export(self):
        pass
