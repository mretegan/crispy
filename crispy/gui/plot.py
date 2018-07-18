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
__date__ = '10/07/2018'


import sys
from collections import OrderedDict as odict
from PyQt5.QtWidgets import QMenu, QToolBar
from PyQt5.QtCore import Qt, QSize

from silx.gui.plot import PlotWidget
from silx.gui.plot import actions, backends, tools
from silx.gui.plot.Profile import ProfileToolBar
# from silx.gui.plot.PlotTools import PositionInfo


class BackendMatplotlibQt(backends.BackendMatplotlib.BackendMatplotlibQt):

    def __init__(self, plot, parent=None):
        super(BackendMatplotlibQt, self).__init__(plot, parent)
        self._legends = odict()

    def addCurve(self, x, y, legend, *args, **kwargs):
        container = super(BackendMatplotlibQt, self).addCurve(
                x, y, legend, *args, **kwargs)

        # Remove the unique identifier from the legend.
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
        if not legends:
            legend.remove()
        self.postRedisplay()


class BasePlotWidget(PlotWidget):
    def __init__(self, *args, **kwargs):
        super(BasePlotWidget, self).__init__(*args, **kwargs)

        self.setActiveCurveHandling(False)
        self.setGraphGrid('both')

        # Create toolbars.
        self._interactiveModeToolBar = tools.toolbars.InteractiveModeToolBar(
            parent=self, plot=self)
        self.addToolBar(self._interactiveModeToolBar)

        self._toolBar = QToolBar('Curve or Image', parent=self)
        self._resetZoomAction = actions.control.ResetZoomAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._resetZoomAction)

        self._xAxisAutoScaleAction = actions.control.XAxisAutoScaleAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._xAxisAutoScaleAction)

        self._yAxisAutoScaleAction = actions.control.YAxisAutoScaleAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._yAxisAutoScaleAction)

        self._gridAction = actions.control.GridAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._gridAction)

        self._curveStyleAction = actions.control.CurveStyleAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._curveStyleAction)

        self._colormapAction = actions.control.ColormapAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._colormapAction)

        self._keepAspectRatio = actions.control.KeepAspectRatioAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._keepAspectRatio)

        self.addToolBar(self._toolBar)

        self._outputToolBar = tools.toolbars.OutputToolBar(
            parent=self, plot=self)
        self.addToolBar(self._outputToolBar)

        # Add the position info.
        # positionInfo = PositionInfo(plot=self)
        # positionInfo.setSnappingMode(positionInfo.SNAPPING_CURVE)
        # self.statusBar().addWidget(positionInfo)


class MainPlotWidget(BasePlotWidget):
    def __init__(self, *args):
        super(MainPlotWidget, self).__init__(
            *args, backend=BackendMatplotlibQt)

        # Add a profile toolbar.
        _profileWindow = BasePlotWidget()
        _profileWindow.setWindowTitle(str())
        self._profileToolBar = ProfileToolBar(
            parent=self, plot=self, profileWindow=_profileWindow)
        self.removeToolBar(self._outputToolBar)
        self.addToolBar(self._profileToolBar)
        self.addToolBar(self._outputToolBar)
        self._outputToolBar.show()

        if sys.platform == 'darwin':
            self.setIconSize(QSize(24, 24))

        # Create QAction for the context menu once for all.
        self._zoomBackAction = actions.control.ZoomBackAction(
            plot=self, parent=self)

        # Retrieve PlotWidget's plot area widget.
        plotArea = self.getWidgetHandle()

        # Set plot area custom context menu.
        plotArea.setContextMenuPolicy(Qt.CustomContextMenu)
        plotArea.customContextMenuRequested.connect(self._contextMenu)

        # Use the viridis color map by default.
        colormap = {'name': 'viridis', 'normalization': 'linear',
                            'autoscale': True, 'vmin': 0.0, 'vmax': 1.0}
        self.setDefaultColormap(colormap)

    def _contextMenu(self, pos):
        """Handle plot area customContextMenuRequested signal.

        :param QPoint pos: Mouse position relative to plot area
        """
        # Create the context menu.
        menu = QMenu(self)
        menu.addAction(self._zoomBackAction)

        # Displaying the context menu at the mouse position requires
        # a global position.
        # The position received as argument is relative to PlotWidget's
        # plot area, and thus needs to be converted.
        plotArea = self.getWidgetHandle()
        globalPosition = plotArea.mapToGlobal(pos)
        menu.exec_(globalPosition)

    def reset(self):
        self.clear()
        self.setKeepDataAspectRatio(False)
        self.setGraphTitle()
        self.setGraphXLabel('X')
        self.setGraphXLimits(0, 100)
        self.setGraphYLabel('Y')
        self.setGraphYLimits(0, 100)
