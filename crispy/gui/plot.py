# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This module holds plotting related functionality."""
import sys

import matplotlib.lines as mlines
import numpy as np

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QMenu, QToolBar

from silx.gui.plot import PlotWidget, Profile
from silx.gui.plot.actions.control import (
    ColormapAction,
    CurveStyleAction,
    GridAction,
    KeepAspectRatioAction,
    ResetZoomAction,
    XAxisAutoScaleAction,
    YAxisAutoScaleAction,
    ZoomBackAction,
)
from silx.gui.plot.items.curve import Curve
from silx.gui.plot.items.image import ImageData
from silx.gui.plot.tools.toolbars import InteractiveModeToolBar, OutputToolBar

__authors__ = ["Marius Retegan"]
__license__ = "MIT"
__date__ = "11/05/2019"


class BasePlotWidget(PlotWidget):
    def __init__(self, parent=None, **kwargs):
        super(BasePlotWidget, self).__init__(
            parent=parent, backend="matplotlib", **kwargs
        )

        self.setActiveCurveHandling(False)
        self.setGraphGrid("both")

        # Create toolbars.
        self._interactiveModeToolBar = InteractiveModeToolBar(parent=self, plot=self)
        self.addToolBar(self._interactiveModeToolBar)

        self._toolBar = QToolBar("Curve or Image", parent=self)
        self._resetZoomAction = ResetZoomAction(parent=self, plot=self)
        self._toolBar.addAction(self._resetZoomAction)

        self._xAxisAutoScaleAction = XAxisAutoScaleAction(parent=self, plot=self)
        self._toolBar.addAction(self._xAxisAutoScaleAction)

        self._yAxisAutoScaleAction = YAxisAutoScaleAction(parent=self, plot=self)
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
        if event["event"] == "mouseMoved":
            x, y = event["x"], event["y"]
            xPixel, yPixel = event["xpixel"], event["ypixel"]
            self._updateStatusBar(x, y, xPixel, yPixel)

    def _updateStatusBar(self, x, y, xPixel, yPixel):
        selectedItems = self._getItems(kind=("curve", "image"))

        if not selectedItems:
            return

        distInPixels = (self._snap_threshold_dist * self._ratio) ** 2

        for item in selectedItems:
            if isinstance(item, Curve):
                messageFormat = "X: {:g}    Y: {:.3g}"
            elif isinstance(item, ImageData):
                messageFormat = "X: {:g}    Y: {:g}"
                continue

            xArray = item.getXData(copy=False)
            yArray = item.getYData(copy=False)

            closestIndex = np.argmin(pow(xArray - x, 2) + pow(yArray - y, 2))

            xClosest = xArray[closestIndex]
            yClosest = yArray[closestIndex]

            axis = item.getYAxis()

            closestInPixels = self.dataToPixel(xClosest, yClosest, axis=axis)
            if closestInPixels is not None:
                curveDistInPixels = (closestInPixels[0] - xPixel) ** 2 + (
                    closestInPixels[1] - yPixel
                ) ** 2

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
        self.setGraphXLabel("X")
        self.setGraphXLimits(0, 100)
        self.setGraphYLabel("Y")
        self.setGraphYLimits(0, 100)

    def addCurve(self, x, y, **kwargs):  # pylint: disable=arguments-differ
        super(BasePlotWidget, self).addCurve(x, y, **kwargs)
        self.addLegend()

    def replot(self):
        self.addLegend()
        super(BasePlotWidget, self).replot()

    def addLegend(self):
        """Add the legend to the Matplotlib axis."""
        ax = self.getWidgetHandle().ax
        # This avoids the log regarding the handles with no labels.
        legend = ax.legend(handles=[])

        images = self.getAllImages()
        if not images:
            legend.set_visible(True)
        else:
            legend.set_visible(False)

        curves = self.getAllCurves()
        if not curves:
            return

        handles = list()
        for curve in curves:
            label = curve.getLegend()
            style = curve.getCurrentStyle()
            marker = style.getSymbol()
            color = style.getColor()
            lineStyle = style.getLineStyle()
            handle = mlines.Line2D(
                [], [], ls=lineStyle, color=color, label=label, marker=marker
            )
            handles.append(handle)
        legend = ax.legend(handles=handles, fancybox=False)


class ProfileWindow(BasePlotWidget):
    def __init__(self, parent=None, **kwargs):
        super(ProfileWindow, self).__init__(parent=parent, **kwargs)

        self.setWindowTitle(str())

        if sys.platform == "darwin":
            self.setIconSize(QSize(24, 24))


class MainPlotWidget(BasePlotWidget):
    def __init__(self, parent=None, **kwargs):
        super(MainPlotWidget, self).__init__(parent=parent, **kwargs)

        # Add a profile toolbar.
        self._profileWindow = ProfileWindow()
        self._profileToolBar = Profile.ProfileToolBar(
            plot=self, profileWindow=self._profileWindow
        )
        # TODO: Check what the last element is.
        self._profileToolBar.actions()[-1].setVisible(False)

        self.removeToolBar(self._outputToolBar)
        self.addToolBar(self._profileToolBar)
        self.addToolBar(self._outputToolBar)
        self._outputToolBar.show()

        if sys.platform == "darwin":
            self.setIconSize(QSize(24, 24))

        # Create QAction for the context menu once for all.
        self._zoomBackAction = ZoomBackAction(plot=self, parent=self)

        # Retrieve PlotWidget's plot area widget.
        plotArea = self.getWidgetHandle()

        # Set plot area custom context menu.
        plotArea.setContextMenuPolicy(Qt.CustomContextMenu)
        plotArea.customContextMenuRequested.connect(self._contextMenu)

        # Use the viridis color map by default.
        colormap = {
            "name": "viridis",
            "normalization": "linear",
            "autoscale": True,
            "vmin": 0.0,
            "vmax": 1.0,
        }
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
