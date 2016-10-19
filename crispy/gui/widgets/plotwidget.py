# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from silx.gui.plot import PlotWindow


class PlotWidget(PlotWindow):
    def __init__(self, *args):
        super(PlotWidget, self).__init__(
            logScale=False, grid=True, aspectRatio=False, yInverted=False,
            roi=False, mask=False, print_=False)
        self.setActiveCurveHandling(False)
        self.setGraphGrid('both')
