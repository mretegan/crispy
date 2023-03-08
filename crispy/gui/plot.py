###################################################################
# Copyright (c) 2016-2022 European Synchrotron Radiation Facility #
#                                                                 #
# Authors: Marius Retegan                                         #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Plotting related functionality."""

import sys

import matplotlib.lines as mlines
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMenu, QToolBar
from silx.gui.plot import PlotWidget, items
from silx.gui.plot.actions.control import (
    ColormapAction,
    CrosshairAction,
    CurveStyleAction,
    GridAction,
    KeepAspectRatioAction,
    ResetZoomAction,
    XAxisAutoScaleAction,
    YAxisAutoScaleAction,
    ZoomBackAction,
)
from silx.gui.plot.actions.io import CopyAction, SaveAction
from silx.gui.plot.actions.mode import PanModeAction, ZoomModeAction
from silx.gui.plot.tools.profile.manager import ProfileManager, ProfileWindow
from silx.gui.plot.tools.profile.rois import (
    ProfileImageCrossROI,
    ProfileImageHorizontalLineROI,
    ProfileImageLineROI,
    ProfileImageVerticalLineROI,
)


class CustomProfileWindow(ProfileWindow):
    def __init__(self, parent=None, backend=None):
        super().__init__(parent=parent, backend=backend)

        self.setWindowTitle("")

    def createPlot1D(self, parent, backend):
        return CustomPlotWidget(parent=parent, backend=backend)


class CustomPlotWidget(PlotWidget):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent=None, backend="matplotlib"):
        super().__init__(parent=parent, backend=backend)

        self.plotArea = self.getWidgetHandle()

        if sys.platform == "darwin":
            self.setIconSize(QSize(24, 24))

        self.setActiveCurveHandling(False)
        self.setGraphGrid("both")

        self.addInteractiveToolBar()
        self.addMainToolBar()
        self.addProfileToolBar()
        self.addOutputToolBar()

        self.sigContentChanged.connect(self.setProfileToolBarVisibility)
        self.sigPlotSignal.connect(self.plotEvent)

    def plotEvent(self, event):
        if event["event"] == "mouseMoved":
            x, y = event["x"], event["y"]
            xPixel, yPixel = event["xpixel"], event["ypixel"]
            self.showPositionInfo(x, y, xPixel, yPixel)

    def showPositionInfo(self, x, y, xPixel, yPixel):
        # For images get also the data at the x and y coordinates.
        condition = lambda item: isinstance(item, items.ImageBase)
        data = None
        for picked in self.pickItems(xPixel, yPixel, condition):
            image = picked.getItem()
            indices = picked.getIndices(copy=False)
            if indices is not None:
                row, col = indices[0][0], indices[1][0]
                data = image.getData(copy=False)[row, col]

        for item in self.getItems():
            if isinstance(item, items.Curve):
                message = f"X: {x:g}    Y: {y:g}"
            elif isinstance(item, items.ImageBase) and data is not None:
                message = f"X: {x:g}    Y: {y:g}    Data: {data:g}"
            else:
                message = None

            self.window().statusBar().showMessage(message)

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)

        zoomBackAction = ZoomBackAction(plot=self, parent=self)
        crosshairAction = CrosshairAction(plot=self, color="lime", parent=contextMenu)

        contextMenu.addAction(zoomBackAction)
        contextMenu.addAction(crosshairAction)

        contextMenu.exec_(event.globalPos())

    def addInteractiveToolBar(self):
        self.interactiveToolBar = QToolBar("Interaction", parent=self)

        zoomModeAction = ZoomModeAction(plot=self, parent=self.interactiveToolBar)
        panModeAction = PanModeAction(plot=self, parent=self.interactiveToolBar)

        self.interactiveToolBar.addAction(zoomModeAction)
        self.interactiveToolBar.addAction(panModeAction)

        self.addToolBar(self.interactiveToolBar)

    def addMainToolBar(self):
        self.mainToolBar = QToolBar("Curve or Image", parent=self)

        self.resetZoomAction = ResetZoomAction(plot=self, parent=self.mainToolBar)
        self.xAxisAutoScaleAction = XAxisAutoScaleAction(
            plot=self, parent=self.mainToolBar
        )
        self.yAxisAutoScaleAction = YAxisAutoScaleAction(
            plot=self, parent=self.mainToolBar
        )
        self.curveStyleAction = CurveStyleAction(plot=self, parent=self.mainToolBar)
        self.colormapAction = ColormapAction(plot=self, parent=self.mainToolBar)
        self.keepAspectRatioAction = KeepAspectRatioAction(
            plot=self, parent=self.mainToolBar
        )
        self.gridAction = GridAction(plot=self, parent=self.mainToolBar)

        self.mainToolBar.addAction(self.resetZoomAction)
        self.mainToolBar.addAction(self.xAxisAutoScaleAction)
        self.mainToolBar.addAction(self.yAxisAutoScaleAction)
        self.mainToolBar.addAction(self.gridAction)
        self.mainToolBar.addAction(self.curveStyleAction)
        self.mainToolBar.addAction(self.colormapAction)
        self.mainToolBar.addAction(self.keepAspectRatioAction)

        self.addToolBar(self.mainToolBar)

    def addOutputToolBar(self):
        self.outputToolBar = QToolBar("IO", parent=self)

        self.copyAction = CopyAction(plot=self, parent=self.outputToolBar)
        self.saveAction = SaveAction(plot=self, parent=self.outputToolBar)

        self.outputToolBar.addAction(self.copyAction)
        self.outputToolBar.addAction(self.saveAction)

        self.addToolBar(self.outputToolBar)

    def addProfileToolBar(self):
        self.profileToolBar = QToolBar("Profile", parent=self)

        profileManager = ProfileManager(plot=self, parent=self.profileToolBar)
        profileManager.setProfileWindowClass(CustomProfileWindow)
        profileManager.setItemType(image=True)
        profileManager.setActiveItemTracking(True)

        roiManager = profileManager.getRoiManager()
        roiManager.sigInteractiveRoiCreated.connect(self.configureRois)

        horizontalLineAction = profileManager.createProfileAction(
            ProfileImageHorizontalLineROI, parent=self.profileToolBar
        )
        verticalLineAction = profileManager.createProfileAction(
            ProfileImageVerticalLineROI, parent=self.profileToolBar
        )
        crossLineAction = profileManager.createProfileAction(
            ProfileImageCrossROI, parent=self.profileToolBar
        )
        freeLineAction = profileManager.createProfileAction(
            ProfileImageLineROI, parent=self.profileToolBar
        )
        cleanAction = profileManager.createClearAction(self.profileToolBar)
        editorAction = profileManager.createEditorAction(self.profileToolBar)

        self.profileToolBar.addAction(horizontalLineAction)
        self.profileToolBar.addAction(verticalLineAction)
        self.profileToolBar.addAction(crossLineAction)
        self.profileToolBar.addAction(freeLineAction)
        self.profileToolBar.addAction(cleanAction)
        self.profileToolBar.addAction(editorAction)

        self.profileToolBar.setVisible(False)
        self.addToolBar(self.profileToolBar)

    def setProfileToolBarVisibility(self):
        imageBaseItems = [
            item for item in self.getItems() if isinstance(item, items.ImageBase)
        ]
        if imageBaseItems:
            self.profileToolBar.setVisible(True)
        else:
            self.profileToolBar.setVisible(False)

    @staticmethod
    def configureRois(roi):
        roi.setName("")
        roi.setProfileMethod("sum")

    def reset(self):
        self.clear()
        self.setKeepDataAspectRatio(False)
        self.setGraphTitle()
        self.setGraphXLabel("X")
        self.setGraphXLimits(0, 100)
        self.setGraphYLabel("Y")
        self.setGraphYLimits(0, 100)
        legend = self.plotArea.ax.legend(handles=[])
        legend.set_visible(False)


class MainPlotWidget(CustomPlotWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.profileWindow = ProfileWindow()

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

    def addCurve(self, x, y, **kwargs):
        # pylint: disable=arguments-differ
        super().addCurve(x, y, **kwargs)
        self.addLegend()

    def replot(self):
        self.addLegend()
        super().replot()

    def isEmpty(self):
        return not self.getAllImages() + self.getAllCurves()

    def addLegend(self):
        """Add the legend to the Matplotlib axis."""
        if not self.getAllCurves():
            legend = self.plotArea.ax.legend(handles=[])
            legend.set_visible(False)
            return

        handles = []
        for curve in self.getAllCurves():
            label = curve.getLegend()
            style = curve.getCurrentStyle()
            marker = style.getSymbol()
            color = style.getColor()
            lineStyle = style.getLineStyle()
            handle = mlines.Line2D(
                [], [], ls=lineStyle, color=color, label=label, marker=marker
            )
            handles.append(handle)

        self.plotArea.ax.legend(handles=handles, fancybox=False, loc="upper right")
