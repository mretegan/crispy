# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2019 European Synchrotron Radiation Facility
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
__date__ = '14/01/2019'


import copy
import csv
import json
import numpy as np
import os
import re
import subprocess
import unittest
from collections import OrderedDict
from silx.utils.testutils import parameterize
from silx.resources import resource_filename as resourceFileName

# from ....utils.odict import odict
from ....gui.config import Config


class TestQuanty(unittest.TestCase):

    def __init__(self, methodName='runTest',
                 index=None, parameters=None):
        unittest.TestCase.__init__(self, methodName)
        self.index = index
        self.parameters = parameters

    @property
    def template(self):
        subshell = self.parameters['subshell']
        symmetry = self.parameters['symmetry']
        experiment = self.parameters['experiment']
        edge = self.parameters['edge']
        edge = re.search(r'\((.*?)\)', edge).group(1)

        templateName = '{}_{}_{}_{}.lua'.format(
            subshell, symmetry, experiment, edge)

        templatePath = resourceFileName('quanty:templates/{}'.format(
            templateName))

        with open(templatePath) as fp:
            return fp.read()

    @property
    def replacements(self):
        replacementsPath = os.path.join(self.rootPath, 'input.json')
        with open(replacementsPath) as fp:
            return json.load(fp, object_pairs_hook=OrderedDict)

    @property
    def rootPath(self):
        cwd = os.path.dirname(__file__)
        return os.path.join(cwd, 'tests', self.index)

    def loadSpectrum(self, fileName):
        experiment = self.parameters['experiment']
        if experiment == 'XAS':
            spectrum = np.loadtxt(fileName, skiprows=5, usecols=2)
        return spectrum

    def setUp(self):
        self.input = copy.deepcopy(self.template)
        for replacement in self.replacements:
            value = self.replacements[replacement]
            self.input = self.input.replace(replacement, str(value))

        self.inputName = os.path.join(self.rootPath, 'input.lua')

        with open(self.inputName, 'w') as fp:
            fp.write(self.input)

        self.runQuanty()

    def runQuanty(self):
        os.chdir(self.rootPath)

        config = Config()
        settings = config.read()
        executable = settings.value('Quanty/Path')

        try:
            output = subprocess.check_output([executable, self.inputName])
        except subprocess.CalledProcessError:
            raise

        self.output = output.decode('utf-8').splitlines()

    def testEnergy(self):
        output = iter(self.output)

        for line in output:
            if 'Analysis' in line:
                lines_to_skip = 3
                for i in range(lines_to_skip):
                    next(output)
                line = next(output)
                energy = float(line.split()[1])

        reference = float(self.parameters['energy'])

        message = 'testEnergy failed for test #{}'.format(self.index)
        self.assertEqual(energy, reference, message)

    def testSpectrum(self):
        suffix = self.parameters['suffix']

        spectrumName = 'input_{}.spec'.format(suffix)
        spectrumPath = os.path.join(self.rootPath, spectrumName)
        spectrum = self.loadSpectrum(spectrumPath)

        referenceName = 'reference_{}.spec'.format(suffix)
        referencePath = os.path.join(self.rootPath, referenceName)
        reference = self.loadSpectrum(referencePath)

        delta = np.max(np.abs(spectrum - reference))

        message = 'testSpectrum failed for test #{} with delta {}'.format(
            self.index, delta)
        self.assertTrue(delta < 5e-7, message)


def suite():
    test_suite = unittest.TestSuite()

    tests = OrderedDict()
    with open(resourceFileName('quanty:test/tests/manifest.csv')) as fp:
        reader = csv.DictReader(fp, quotechar='"', quoting=csv.QUOTE_ALL,
                                skipinitialspace=True)
        for line in reader:
            index = line['index']
            line.pop('index', None)
            tests[index] = line

    for test in tests:
        parameters = tests[test]
        test_suite.addTest(parameterize(TestQuanty, test, parameters))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
