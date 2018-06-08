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
__date__ = '08/06/2018'


import errno
import json
import os
import sys

from PyQt5.QtCore import QStandardPaths
from silx.resources import resource_filename as resourceFileName

from ..version import version
from ..utils.odict import odict


class Config(object):

    def __init__(self):
        self.loadSettings()

    @staticmethod
    def getConfigLocation():
        configLocation = QStandardPaths.GenericConfigLocation
        root = QStandardPaths.standardLocations(configLocation)[0]

        if sys.platform in ('win32', 'darwin'):
            path = os.path.join(root, 'Crispy')
        else:
            path = os.path.join(root, 'crispy')

        return path

    @staticmethod
    def quantyFindPath():
        if sys.platform in 'win32':
            executable = 'Quanty.exe'
        else:
            executable = 'Quanty'

        envPath = QStandardPaths.findExecutable(executable)
        localPath = QStandardPaths.findExecutable(
            executable, [resourceFileName(
                'crispy:' + os.path.join('modules', 'quanty', 'bin'))])

        # Check if Quanty is in the paths defined in the $PATH.
        if envPath:
            path = os.path.dirname(envPath)
        # Check if Quanty is bundled with Crispy.
        elif localPath:
            path = os.path.dirname(localPath)
        else:
            path = None

        return path, executable

    def setSetting(self, setting, value):
        self._settings[setting] = value

    def getSetting(self, setting):
        return self._settings[setting]

    def saveSettings(self):
        path = self.getConfigLocation()

        try:
            os.makedirs(path, mode=0o755)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

        configPath = os.path.join(path, 'settings.json')

        with open(configPath, 'w') as p:
            json.dump(self._settings, p)

    def loadSettings(self, defaults=False):
        if defaults:
            self._settings = odict()
            path, executable = self.quantyFindPath()
            self._settings['quantyPath'] = path
            self._settings['quantyExecutable'] = executable
            self._settings['quantyVerbosity'] = '0x0000'
            self._settings['currentPath'] = os.path.expanduser('~')
            self._settings['version'] = version
            self._settings['updateCheck'] = True
            return

        configPath = os.path.join(self.getConfigLocation(), 'settings.json')

        try:
            with open(configPath, 'r') as p:
                self._settings = json.loads(p.read(), object_pairs_hook=odict)
        except IOError as e:
            self.loadSettings(defaults=True)

        # Overwrite settings file written by previous versions of Crispy.
        if 'version' not in self._settings:
            self.loadSettings(defaults=True)

        self.saveSettings()
