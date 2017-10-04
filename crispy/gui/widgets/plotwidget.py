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
__date__ = '04/10/2017'


from silx.gui.plot import PlotWindow
# from silx.gui.plot.PlotTools import PositionInfo
from PyQt5.QtWidgets import QComboBox
# from PyQt5.QtCore import Qt


class PlotWidget(PlotWindow):
    def __init__(self, *args):
        super(PlotWidget, self).__init__(
            logScale=False, grid=True, yInverted=False,
            roi=False, mask=False, print_=False)
        self.setActiveCurveHandling(True)
        self.setGraphGrid('both')

        self.spectraComboBox = QComboBox()
        self.spectraComboBox.setMinimumWidth(150)

        # toolBar = self.toolBar()
        # toolBar = QToolBar()
        # self.addToolBar(Qt.TopToolBarArea, toolBar)
        # toolBar.addSeparator()
        # position = PositionInfo(plot=self)
        # toolBar.addWidget(position)

        # limitsToolBar = LimitsToolBar(plot=self)
        # self.addToolBar(Qt.BottomToolBarArea, limitsToolBar)

        # toolbar = self.toolBar()
        # toolbar.addSeparator()
        # toolbar.addWidget(self.spectraComboBox)

    def reset(self):
        self.clear()
        self.setGraphTitle()
        self.setGraphXLabel('X')
        self.setGraphXLimits(0, 100)
        self.setGraphYLabel('Y')
        self.setGraphYLimits(0, 100)
        # self.keepDataAspectRatio(False)
