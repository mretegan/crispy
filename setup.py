#!/usr/bin/env python
# coding: utf-8

import os
from setuptools import setup, find_packages


def get_readme():
    _dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(_dir, 'README.md'), 'r') as fp:
        long_description = fp.read()
    return long_description

setup(name='crispy',
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
      packages=find_packages(),
      package_data={'crispy.resources': [
          'parameters.json',
          'gui/icons/*.svg',
          'gui/uis/*.ui',
          'backends/quanty/templates/*.lua']},
      scripts=['crispy/scripts/crispy'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: X11 Applications :: Qt',
                   'Intended Audience :: Education',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Topic :: Scientific/Engineering :: Physics'])
