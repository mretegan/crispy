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

# The application should be built from a virtual environment containing
# only the required packages.
# TODO: Find a way to read the system's PATH.

from __future__ import absolute_import, division, unicode_literals

__authors__ = ['Marius Retegan']
__license__ = 'MIT'
__date__ = '23/10/2017'

import os
import sys
import shutil

from setuptools import setup


def get_version():
    import version
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
        root, 'dist', 'macOS', 'Crispy.app', 'Contents', 'Resources', 'lib',
        'python3.6', 'PyQt5')

    for module in modules:
        os.remove(os.path.join(pyqt_dir, module + '.so'))

        shutil.rmtree(
            os.path.join(pyqt_dir, 'Qt', 'lib', module + '.framework'))


def make_dmg(root, dist_dir):
    dmg_name = 'Crispy-{}.dmg'.format(get_version())
    dmg_path = os.path.join(root, 'downloads', dmg_name)

    command = (
        'hdiutil create {} -volname Crispy -fs HFS+ -srcfolder {}'.format(
         dmg_path, dist_dir))
    os.system(command)


def main():
    # Workaround the recursion error happening during the build process.
    sys.setrecursionlimit(2000)

    # Define the root folder and corresponding subfolders.
    root = os.path.dirname(os.getcwd())
    dist_dir = os.path.join(root, 'dist', 'macOS')
    build_dir = os.path.join(root, 'build', 'macOS')

    # Remove previously built application.
    clean_folders([build_dir, os.path.join(dist_dir, 'Crispy.app')])

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

    options = {
        'py2app': {
            'iconfile': 'icons/crispy.icns',
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

    # Package the application.
    make_dmg(root, dist_dir)


if __name__ == '__main__':
    main()
