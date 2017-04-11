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
__date__ = '10/04/2017'

import crispy
import os
import silx
import sys
from cx_Freeze import setup, Executable


def get_version():
    import version
    return version.strictversion

packages = ['matplotlib', 'PyQt5.QtPrintSupport']
includes = []
excludes = ['tkinter']

modules = [crispy, silx]
modules_path = [os.path.dirname(module.__file__) for module in modules]
include_files = [(module, os.path.basename(module)) for module in modules_path]

options = {
    'build_exe': {
        'packages': packages,
        'includes': includes,
        'excludes': excludes,
        'include_files': include_files,
        'include_msvcr': True,
        },
    }

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable(
        'scripts/crispy',
        base=base,
        icon='icons/crispy.ico',
        ),
    ]


def main():
    setup(name='crispy',
          version=get_version(),
          options=options,
          executables=executables)

if __name__ == '__main__':
    main()
