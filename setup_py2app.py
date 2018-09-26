#!/usr/bin/env python
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

# The application should be built from a virtual environment containing
# only the required packages.
# TODO: Find a way to read the system's PATH.

from __future__ import absolute_import, division, unicode_literals

__authors__ = ['Marius Retegan']
__license__ = 'MIT'
__date__ = '25/09/2018'

import os
import sys
import shutil

from setuptools import setup


def get_version():
    from crispy import version
    return version.strictversion


def clean_folders(folders):
    for folder in folders:
        shutil.rmtree(folder, ignore_errors=True)


def prune_app(root):

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
        'QtQuickControls2',
        'QtQuickParticles',
        'QtQuickTemplates2',
        'QtQuickTest',
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

    # TODO: detect the Python version
    pyqt_dir = os.path.join(
        root, 'dist', 'Crispy.app', 'Contents', 'Resources', 'lib',
        'python3.5', 'PyQt5')

    for module in modules:
        try:
            os.remove(os.path.join(pyqt_dir, module + '.so'))
        except OSError:
            pass

        shutil.rmtree(
            os.path.join(pyqt_dir, 'Qt', 'lib', module + '.framework'))


def main():
    # Workaround the recursion error happening during the build process.
    sys.setrecursionlimit(2000)

    # Define the root folder and corresponding subfolders.
    root = os.path.dirname(os.getcwd())
    dist_dir = os.path.join(root, 'dist')
    build_dir = os.path.join(root, 'build')
    artifacts_dir = os.path.join(root, 'artifacts')

    # Remove previously built application.
    clean_folders([build_dir, dist_dir, artifacts_dir])

    packages = ['matplotlib', 'silx', 'crispy', 'h5py']

    plist = {
        'CFBundleIdentifier': 'com.github.mretegan.crispy',
        'CFBundleShortVersionString': get_version(),
        'CFBundleVersion': 'Crispy' + get_version(),
        'CFBundleGetInfoString': 'Crispy',
        'LSTypeIsPackage': True,
        'LSArchitecturePriority': 'x86_64',
        'LSMinimumSystemVersion': '10.10.0',
        'NSHumanReadableCopyright': 'MIT',
        'NSHighResolutionCapable': True,
        }

    options = {
        'py2app': {
            'iconfile': os.path.join('assets', 'crispy.icns'),
            'bdist_base': build_dir,
            'dist_dir': dist_dir,
            'packages': packages,
            'plist': plist,
            'argv_emulation': False,
            'optimize':  2,
            'compressed': True,
            },
        }

    setup(
        name='Crispy',
        version=get_version(),
        app=['scripts/crispy'],
        options=options,
        )

    # Remove unused modules.
    prune_app(root)


if __name__ == '__main__':
    main()
