# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2018 European Synchrotron Radiation Facility
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
__date__ = '06/12/2018'

import os
import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QStandardPaths

from ..version import version


class Config(object):

    def __init__(self):
        if sys.platform == 'win32':
            self.name = 'Crispy'
        else:
            self.name = 'crispy'

    def read(self):
        return QSettings(
            QSettings.IniFormat, QSettings.UserScope, self.name, 'settings')

    def removeOldFiles(self):
        configLocation = QStandardPaths.GenericConfigLocation
        root = QStandardPaths.standardLocations(configLocation)[0]

        path = os.path.join(root, self.name)

        if version < '0.7.0':
            try:
                os.remove(os.path.join(path, 'settings.json'))
                os.rmdir(path)
            except (IOError, OSError) as e:
                pass
