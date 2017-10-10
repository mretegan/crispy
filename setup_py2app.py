#!/usr/bin/env python
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
__date__ = '10/10/2017'

import os
import sys
import shutil

from setuptools import setup


def get_version():
    import version
    return version.strictversion


packages = ['matplotlib', 'silx', 'crispy']

plist = {
    'CFBundleIdentifier': 'com.github.mretegan.crispy',
    'CFBundleShortVersionString': get_version(),
    'CFBundleVersion': 'Crispy' + get_version(),
    'CFBundleGetInfoString': 'Crispy',
    'LSTypeIsPackage': True,
    'LSArchitecturePriority': 'x86_64',
    'LSMinimumSystemVersion': '10.9.0',
    'NSHumanReadableCopyright': 'MIT',
    'NSHighResolutionCapable': True,
    }

parent = os.path.dirname(os.getcwd())

options = {
    'py2app': {
        'iconfile': 'icons/crispy.icns',
        'bdist_base': os.path.join(parent, 'build', 'macOS'),
        'dist_dir': os.path.join(parent, 'dist', 'macOS'),
        'packages': packages,
        'plist': plist,
        'argv_emulation': False,
        'optimize':  2,
        'compressed': True,
        },
    }


def main():
    path = os.path.join(parent, 'build', 'macOS', 'python3.5-standalone')
    shutil.rmtree(path, ignore_errors=True)

    path = os.path.join(parent, 'dist', 'macOS', 'Crispy.app')
    shutil.rmtree(path, ignore_errors=True)

    sys.setrecursionlimit(2000)

    setup(name='Crispy',
          version=get_version(),
          app=['scripts/crispy'],
          options=options,
          )

    modules = [
        'QtBluetooth',
        'QtDBus',
        'QtDesigner',
        'QtHelp',
        'QtLocation',
        'QtMultimedia',
        'QtMultimediaWidgets',
        'QtNetwork',
        'QtNfc',
        'QtOpenGL',
        'QtPositioning',
        'QtQml',
        'QtQuick',
        'QtQuickWidgets',
        'QtSensors',
        'QtSerialPort',
        'QtSql',
        'QtTest',
        'QtWebChannel',
        'QtWebEngine',
        'QtWebEngineCore',
        'QtWebEngineWidgets',
        'QtWebSockets',
        'QtXml',
        'QtXmlPatterns',
        ]

    path = os.path.join(parent, 'dist', 'macOS', 'Crispy.app', 'contents', 'resources',
                        'lib', 'python3.5', 'pyqt5')
    for module in modules:
        os.remove(os.path.join(path, module + '.so'))

    path = os.path.join(parent, 'dist', 'macOS', 'Crispy.app', 'contents', 'resources',
                        'lib', 'python3.5', 'pyqt5', 'Qt', 'lib')
    for module in modules:
        for root, _, files in os.walk(os.path.join(
                path, module + '.framework')):
            for file in files:
                os.remove(os.path.join(root, file))

    os.chdir('..')
    os.system('hdiutil create Crispy_{}.dmg -volname Crispy -fs HFS+ -srcfolder {}'.format(get_version(), os.path.join('dist', 'macOS')))


if __name__ == '__main__':
    main()
