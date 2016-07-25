#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

setup(name='crispy',
      version='0.1.0',
      description='Core-level spectRoscopy Simulations in Python',
      long_description='Core-level spectRoscopy Simulations in Python',
      license='MIT',
      author='Marius Retegan',
      author_email='marius.retegan@esrf.eu',
      url='https://github.com/mretegan/crispy',
      download_url='https://github.com/mretegan/crispy',
      packages=find_packages(),
      package_data={'crispy.resources': [
          'parameters.json',
          'gui/icons/*.svg',
          'gui/uis/*.ui',
          'backends/quanty/templates/*.lua']},
      scripts=['crispy/scripts/crispy'],
      )
