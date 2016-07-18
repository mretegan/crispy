# coding: utf-8

from silx.gui.plot import PlotWindow

class PlotWidget(PlotWindow):
    def __init__(self, *args):
        super(PlotWidget, self).__init__(logScale=False, grid=True,
                aspectRatio=False, yInverted=False, roi=False, mask=False,
                print_=False)
        self.setActiveCurveHandling(False)
        self.setGraphXLabel('Energy (eV)')
        self.setGraphYLabel('Absorption cross section (a.u.)')

    def plot(self, x, y, legend=None):
        self.addCurve(x, y, legend=legend)

    def clear(self):
        super(PlotWidget, self).clear()

