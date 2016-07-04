# coding: utf-8

from silx.gui.plot import PlotWindow

class PlotWidget(PlotWindow):
    def __init__(self, *args):
        super(PlotWidget, self).__init__()
        self.setActiveCurveHandling(False)
        self.setGraphXLabel('Energy (eV)')
        self.setGraphYLabel('Absorption cross section (a.u.)')

    def plot(self, x, y, legend=None):
        self.addCurve(x, y, legend=legend)

    def clear(self):
        super(PlotWidget, self).clear()

