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
__date__ = '17/01/2017'

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_readme():
    _dir = os.path.dirname(os.path.abspath(__file__))
    long_description = ''
    with open(os.path.join(_dir, 'README.rst')) as f:
        for line in f:
            if 'image::' not in line:
                long_description += line
    return long_description


def get_version():
    import version
    return version.strictversion


def main():
    """The main entry point."""
    if sys.version_info < (2, 7):
        sys.exit('crispy requires at least Python 2.7')
    elif sys.version_info[0] == 3 and sys.version_info < (3, 4):
        sys.exit('crispy requires at least Python 3.4')

    kwargs = dict(
        name='crispy',
        version=get_version(),
        description='Core-level spectRoscopy Simulations in Python',
        long_description=get_readme(),
        license='MIT',
        author='Marius Retegan',
        author_email='marius.retegan@esrf.eu',
        url='https://github.com/mretegan/crispy',
        download_url='https://github.com/mretegan/crispy/releases',
        platforms=[
            'MacOS :: MacOS X',
            'Microsoft :: Windows',
            'POSIX :: Linux',
            ],
        packages=[
            'crispy',
            'crispy.gui',
            'crispy.gui.models',
            'crispy.gui.views',
            'crispy.gui.widgets',
            'crispy.resources',
            ],
        package_data={
            'crispy.resources': [
                'gui/uis/*.ui',
                'gui/icons/*.svg',
                'modules/quanty/parameters/*.json',
                'modules/quanty/templates/*.lua',
                ],
            },
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: X11 Applications :: Qt',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Scientific/Engineering :: Visualization',
            ]
        )

    # At the moment pip/setuptools doesn't play nice with shebang paths
    # containing white spaces.
    # See: https://github.com/pypa/pip/issues/2783
    #      https://github.com/xonsh/xonsh/issues/879
    # The most straight forward workaround is to have a .bat script to run
    # crispy on Windows.

    if 'win32' in sys.platform:
        kwargs['scripts'] = ['scripts/crispy.bat']
    else:
        kwargs['scripts'] = ['scripts/crispy']

    setup(**kwargs)

if __name__ == '__main__':
    main()
