#!/usr/bin/env python
# coding: utf-8

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def get_readme():
    _dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(_dir, 'README.rst'), 'r') as f:
        long_description = f.read()
    return long_description

def main():
    """The main entry point."""
    if sys.version_info[0] < 3:
        sys.exit('crispy currently requires Python 3.4+')

    skw = dict(
        name='crispy',
        version='0.1.0',
        description='Core-level spectRoscopy Simulations in Python',
        long_description=get_readme(),
        license='MIT',
        author='Marius Retegan',
        author_email='marius.retegan@esrf.eu',
        url='https://github.com/mretegan/crispy',
        download_url='https://github.com/mretegan/crispy/releases',
        platforms=['MacOS :: MacOS X',
            'Microsoft :: Windows',
            'POSIX :: Linux'],
        packages=['crispy',
            'crispy.gui',
            'crispy.resources',
            'crispy.gui.models',
            'crispy.gui.views',
            'crispy.gui.widgets'],
        package_data={'crispy.resources': ['gui/*.ui',
            'gui/icons/*.svg',
            'modules/quanty/parameters/*.json',
            'modules/quanty/templates/*.lua']},
        classifiers=['Development Status :: 4 - Beta',
            'Environment :: X11 Applications :: Qt',
            'Intended Audience :: Education',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.5',
            'Topic :: Scientific/Engineering :: Visualization'])

    # At the moment pip/setuptools doesn't play nice with shebang paths
    # containing white space.
    # See: https://github.com/pypa/pip/issues/2783
    #      https://github.com/xonsh/xonsh/issues/879
    # The most straight forward workaround is to have a .bat script to run
    # crispy on Windows.

    if 'win' not in sys.platform:
        skw['scripts'] = ['scripts/crispy']
    else:
        skw['scripts'] = ['scripts/crispy.bat']

    setup(**skw)

if __name__ == '__main__':
    main()
