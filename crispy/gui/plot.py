# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2019 European Synchrotron Radiation Facility
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
__date__ = '26/06/2019'


import numpy as np
import sys
from collections import OrderedDict as odict
from PyQt5.QtWidgets import QMenu, QToolBar
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QGuiApplication

from silx.gui.plot import PlotWidget, Profile
from silx.gui.plot.actions.control import (
    ResetZoomAction, XAxisAutoScaleAction, YAxisAutoScaleAction, GridAction,
    CurveStyleAction, ColormapAction, KeepAspectRatioAction, ZoomBackAction)
from silx.gui.plot.backends import BackendMatplotlib
from silx.gui.plot.items.curve import Curve
from silx.gui.plot.items.image import ImageData
from silx.gui.plot.tools.toolbars import InteractiveModeToolBar, OutputToolBar


class BackendMatplotlibQt(BackendMatplotlib.BackendMatplotlibQt):

    def __init__(self, plot, parent=None):
        super(BackendMatplotlibQt, self).__init__(plot, parent=parent)
        self._legends = odict()

    def addCurve(self, x, y, legend, *args, **kwargs):
        container = super(BackendMatplotlibQt, self).addCurve(
            x, y, legend, *args, **kwargs)

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
    def __init__(self, parent=None, **kwargs):
        super(BasePlotWidget, self).__init__(parent=parent, **kwargs)

        self.setActiveCurveHandling(False)
        self.setGraphGrid('both')

        # Create toolbars.
        self._interactiveModeToolBar = InteractiveModeToolBar(
            parent=self, plot=self)
        self.addToolBar(self._interactiveModeToolBar)

        self._toolBar = QToolBar('Curve or Image', parent=self)
        self._resetZoomAction = ResetZoomAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._resetZoomAction)

        self._xAxisAutoScaleAction = XAxisAutoScaleAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._xAxisAutoScaleAction)

        self._yAxisAutoScaleAction = YAxisAutoScaleAction(
            parent=self, plot=self)
        self._toolBar.addAction(self._yAxisAutoScaleAction)

        self._gridAction = GridAction(parent=self, plot=self)
        self._toolBar.addAction(self._gridAction)

        self._curveStyleAction = CurveStyleAction(parent=self, plot=self)
        self._toolBar.addAction(self._curveStyleAction)

        self._colormapAction = ColormapAction(parent=self, plot=self)
        self._toolBar.addAction(self._colormapAction)

        self._keepAspectRatio = KeepAspectRatioAction(parent=self, plot=self)
        self._toolBar.addAction(self._keepAspectRatio)

        self.addToolBar(self._toolBar)

        self._outputToolBar = OutputToolBar(parent=self, plot=self)
        self.addToolBar(self._outputToolBar)

        windowHandle = self.window().windowHandle()
        if windowHandle is not None:
            self._ratio = windowHandle.devicePixelRatio()
        else:
            self._ratio = QGuiApplication.primaryScreen().devicePixelRatio()

        self._snap_threshold_dist = 5

        self.sigPlotSignal.connect(self._plotEvent)

    def _plotEvent(self, event):
        if event['event'] == 'mouseMoved':
            x, y = event['x'], event['y']
            xPixel, yPixel = event['xpixel'], event['ypixel']
            self._updateStatusBar(x, y, xPixel, yPixel)

    def _updateStatusBar(self, x, y, xPixel, yPixel):
        selectedItems = self._getItems(kind=('curve', 'image'))

        if not selectedItems:
            return

        distInPixels = (self._snap_threshold_dist * self._ratio) ** 2

        for item in selectedItems:
            if isinstance(item, Curve):
                messageFormat = 'X: {:g}    Y: {:.3g}'
            elif isinstance(item, ImageData):
                messageFormat = 'X: {:g}    Y: {:g}'
                continue

            xArray = item.getXData(copy=False)
            yArray = item.getYData(copy=False)

            closestIndex = np.argmin(
                pow(xArray - x, 2) + pow(yArray - y, 2))

            xClosest = xArray[closestIndex]
            yClosest = yArray[closestIndex]

            axis = item.getYAxis()

            closestInPixels = self.dataToPixel(xClosest, yClosest, axis=axis)
            if closestInPixels is not None:
                curveDistInPixels = (
                    (closestInPixels[0] - xPixel)**2 +
                    (closestInPixels[1] - yPixel)**2)

                if curveDistInPixels <= distInPixels:
                    # If close enough, snap to data point coordinates.
                    x, y = xClosest, yClosest
                    distInPixels = curveDistInPixels

        message = messageFormat.format(x, y)
        self.window().statusBar().showMessage(message)

    def reset(self):
        self.clear()
        self.setKeepDataAspectRatio(False)
        self.setGraphTitle()
        self.setGraphXLabel('X')
        self.setGraphXLimits(0, 100)
        self.setGraphYLabel('Y')
        self.setGraphYLimits(0, 100)


class ProfileWindow(BasePlotWidget):
    def __init__(self, parent=None, **kwargs):
        super(ProfileWindow, self).__init__(parent=parent, **kwargs)

        self.setWindowTitle(str())
        if sys.platform == 'darwin':
            self.setIconSize(QSize(24, 24))


class MainPlotWidget(BasePlotWidget):
    def __init__(self, parent=None, **kwargs):
        super(MainPlotWidget, self).__init__(
            parent=parent, backend=BackendMatplotlibQt, **kwargs)

        # Add a profile toolbar.
        self._profileWindow = ProfileWindow()
        self._profileToolBar = Profile.ProfileToolBar(
            plot=self, profileWindow=self._profileWindow)
        self._profileToolBar.actions()[-1].setVisible(False)

        self.removeToolBar(self._outputToolBar)
        self.addToolBar(self._profileToolBar)
        self.addToolBar(self._outputToolBar)
        self._outputToolBar.show()

        if sys.platform == 'darwin':
            self.setIconSize(QSize(24, 24))

        # Create QAction for the context menu once for all.
        self._zoomBackAction = ZoomBackAction(plot=self, parent=self)

        # Retrieve PlotWidget's plot area widget.
        plotArea = self.getWidgetHandle()

        # Set plot area custom context menu.
        plotArea.setContextMenuPolicy(Qt.CustomContextMenu)
        plotArea.customContextMenuRequested.connect(self._contextMenu)

        # Use the viridis color map by default.
        colormap = {'name': 'viridis', 'normalization': 'linear',
                    'autoscale': True, 'vmin': 0.0, 'vmax': 1.0}
        self.setDefaultColormap(colormap)

    def closeProfileWindow(self):
        self._profileWindow.close()

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
