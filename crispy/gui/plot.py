# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""This module provides plotting related functionality."""
import sys

import matplotlib.lines as mlines
import numpy as np

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QMenu, QToolBar

from silx.gui.plot import PlotWidget
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
from silx.gui.plot.actions.mode import ZoomModeAction, PanModeAction
from silx.gui.plot.actions.io import CopyAction, SaveAction
from silx.gui.plot.items.curve import Curve
from silx.gui.plot.items.image import ImageData

__authors__ = ["Marius Retegan"]
__license__ = "MIT"
__date__ = "13/05/2019"


class BasePlotWidget(PlotWidget):  # pylint: disable=too-many-instance-attributes
    SNAP_THRESHOLD_DIST = 5

    def __init__(self, parent=None, **kwargs):
        super(BasePlotWidget, self).__init__(
            parent=parent, backend="matplotlib", **kwargs
        )

        self.setActiveCurveHandling(False)
        self.setGraphGrid("both")

        # Add the interactive mode toolbar.
        self.interactionModeToolBar = QToolBar("Interaction", parent=self)

        self.zoomModeAction = ZoomModeAction(self, parent=self.interactionModeToolBar)
        self.interactionModeToolBar.addAction(self.zoomModeAction)

        self.panModeAction = PanModeAction(self, parent=self.interactionModeToolBar)
        self.interactionModeToolBar.addAction(self.panModeAction)

        self.addToolBar(self.interactionModeToolBar)

        # Add a custom toolbar for curves and images.
        self.mainToolBar = QToolBar("Curve or Image", parent=self)

        self.resetZoomAction = ResetZoomAction(self, parent=self.mainToolBar)
        self.mainToolBar.addAction(self.resetZoomAction)

        self.xAxisAutoScaleAction = XAxisAutoScaleAction(self, parent=self.mainToolBar)
        self.mainToolBar.addAction(self.xAxisAutoScaleAction)

        self.yAxisAutoScaleAction = YAxisAutoScaleAction(self, parent=self.mainToolBar)
        self.mainToolBar.addAction(self.yAxisAutoScaleAction)

        self.gridAction = GridAction(self, parent=self.mainToolBar)
        self.mainToolBar.addAction(self.gridAction)

        self.curveStyleAction = CurveStyleAction(self, parent=self.mainToolBar)
        self.mainToolBar.addAction(self.curveStyleAction)

        self.colormapAction = ColormapAction(self, parent=self.mainToolBar)
        self.mainToolBar.addAction(self.colormapAction)

        self.keepAspectRatio = KeepAspectRatioAction(self, parent=self.mainToolBar)
        self.mainToolBar.addAction(self.keepAspectRatio)

        self.addToolBar(self.mainToolBar)

        # Add the output toolbar.
        self.outputToolBar = QToolBar("IO", parent=self)

        self.copyAction = CopyAction(self, parent=self.outputToolBar)
        self.outputToolBar.addAction(self.copyAction)

        self.saveAction = SaveAction(self, parent=self.outputToolBar)
        self.outputToolBar.addAction(self.saveAction)

        self.addToolBar(self.outputToolBar)

        windowHandle = self.window().windowHandle()
        if windowHandle is not None:
            self.ratio = windowHandle.devicePixelRatio()
        else:
            self.ratio = QGuiApplication.primaryScreen().devicePixelRatio()

        self.plotArea = self.getWidgetHandle()

        self.sigPlotSignal.connect(self.plotEvent)

    def plotEvent(self, event):
        if event["event"] == "mouseMoved":
            x, y = event["x"], event["y"]
            xPixel, yPixel = event["xpixel"], event["ypixel"]
            self.updateStatusBar(x, y, xPixel, yPixel)

    def updateStatusBar(self, x, y, xPixel, yPixel):
        selectedItems = self.getItems()

        if not selectedItems:
            return

        distInPixels = (self.SNAP_THRESHOLD_DIST * self.ratio) ** 2

        # TODO: Add the intensity for images.
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
                xDistInPixels = closestInPixels[0] - xPixel
                yDistInPixels = closestInPixels[1] - yPixel
                curveDistInPixels = xDistInPixels ** 2 + yDistInPixels ** 2

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
        images = self.getAllImages()
        curves = self.getAllCurves()

        if not curves or images:
            legend = self.plotArea.ax.legend(handles=[])
            legend.set_visible(False)
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
        self.plotArea.ax.legend(handles=handles, fancybox=False)


class ProfileWindow(BasePlotWidget):
    def __init__(self, parent=None, **kwargs):
        super(ProfileWindow, self).__init__(parent=parent, **kwargs)

        self.setWindowTitle(str())

        if sys.platform == "darwin":
            self.setIconSize(QSize(24, 24))


class MainPlotWidget(BasePlotWidget):
    def __init__(self, parent=None, **kwargs):
        super(MainPlotWidget, self).__init__(parent=parent, **kwargs)
        self.profileWindow = ProfileWindow()

        # Instantiate the profile manager.
        # profileManager = manager.ProfileManager(self, self)
        # profileManager.setItemType(image=True)
        # profileManager.setActiveItemTracking(True)

        # profileWindow = ProfileWindow()
        # self.profileToolBar = ProfileToolBar(
        #     parent=self, plot=self, profileWindow=profileWindow
        # )
        # self.profileToolBar.clear()
        # for action in profileManager.createImageActions(self.profileToolBar):
        #     self.profileToolBar.addAction(action)

        # action = profileManager.createClearAction(self.profileToolBar)
        # self.profileToolBar.addAction(action)
        # action = profileManager.createEditorAction(self.profileToolBar)
        # self.profileToolBar.addAction(action)

        # self.removeToolBar(self.outputToolBar)
        # self.addToolBar(self.profileToolBar)
        # self.addToolBar(self.outputToolBar)
        # self.outputToolBar.show()

        if sys.platform == "darwin":
            self.setIconSize(QSize(24, 24))

        # Create QAction for the context menu once for all.
        self.zoomBackAction = ZoomBackAction(plot=self, parent=self)

        # Set plot area custom context menu.
        self.plotArea.setContextMenuPolicy(Qt.CustomContextMenu)
        self.plotArea.customContextMenuRequested.connect(self.contextMenu)

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
        self.profileWindow.close()

    def contextMenu(self, pos):
        """Handle plot area customContextMenuRequested signal.

        :param QPoint pos: Mouse position relative to plot area
        """
        # Create the context menu.
        menu = QMenu(self)
        menu.addAction(self.zoomBackAction)

        # Displaying the context menu at the mouse position requires
        # a global position.
        # The position received as argument is relative to PlotWidget's
        # plot area, and thus needs to be converted.
        globalPosition = self.plotArea.mapToGlobal(pos)
        menu.exec_(globalPosition)
