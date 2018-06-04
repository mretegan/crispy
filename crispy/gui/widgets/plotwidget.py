# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

from __future__ import absolute_import, division, unicode_literals

__authors__ = ['Marius Retegan']
__license__ = 'MIT'
__date__ = '05/06/2018'


from collections import OrderedDict as odict
from silx.gui.plot import PlotWindow
from silx.gui.plot.backends.BackendMatplotlib import (
    BackendMatplotlibQt as _BackendMatplotlibQt)
from silx.gui.plot.Profile import ProfileToolBar


class BackendMatplotlibQt(_BackendMatplotlibQt):

    def __init__(self, plot, parent=None):
        super(BackendMatplotlibQt, self).__init__(plot, parent)
        self._legends = odict()

    def addCurve(self, x, y, legend, *args, **kwargs):
        container = super(BackendMatplotlibQt, self).addCurve(
                x, y, legend, *args, **kwargs)

        # Remove the unique identifier from the legend.
        legend = legend[:-11]
        curve = container.get_children()[0]
        self._legends[curve] = legend
        self._updateLegends()

        return container

    def remove(self, container):
        super(BackendMatplotlibQt, self).remove(container)
        try:
            curve = container.get_children()[0]
            try:
                self._legends.pop(curve)
            except KeyError:
                pass
        except IndexError:
            pass
        self._updateLegends()

    def _updateLegends(self):
        curves = list()
        legends = list()

        for curve in self._legends:
            curves.append(curve)
            legends.append(self._legends[curve])

        legend = self.ax.legend(curves, legends, prop={'size': 'medium'})
        frame = legend.get_frame()
        frame.set_edgecolor('white')
        self.postRedisplay()


class PlotWidget(PlotWindow):
    def __init__(self, *args):
        super(PlotWidget, self).__init__(
            logScale=False, grid=True, yInverted=False,
            roi=False, mask=False, print_=False, backend=BackendMatplotlibQt)

        self.setActiveCurveHandling(False)
        self.setGraphGrid('both')
        profileWindow = PlotWindow(
            logScale=False, grid=True, yInverted=False, roi=False,
            mask=False, print_=False)
        profileWindow.setWindowTitle('')
        self.profile = ProfileToolBar(plot=self, profileWindow=profileWindow)
        self.addToolBar(self.profile)

    def reset(self):
        self.clear()
        self.setGraphTitle()
        self.setGraphXLabel('X')
        self.setGraphXLimits(0, 100)
        self.setGraphYLabel('Y')
        self.setGraphYLimits(0, 100)
        self.keepDataAspectRatio(False)
