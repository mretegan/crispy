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


import unittest
import json
import os
import subprocess
import numpy as np
from silx.utils.testutils import parameterize
from silx.resources import resource_filename as resourceFileName

from ....utils.odict import odict
from ....gui.config import Config


class TestQuanty(unittest.TestCase):

    def __init__(self, methodName='runTest',
                 index=None, parameters=None):
        unittest.TestCase.__init__(self, methodName)
        self.index = index
        self.parameters = parameters

    def setUp(self):
        # Go to the test directory.
        path = os.path.join(
            os.path.dirname(__file__), 'tests', self.index)
        os.chdir(path)

        # Load the template.
        templateName = '{}_{}_{}_{}.lua'.format(
            self.parameters['subshell'],
            self.parameters['symmetry'],
            self.parameters['experiment'],
            self.parameters['edge'],
        )
        templatePath = resourceFileName('quanty:templates/{}'.format(
            templateName))
        with open(templatePath) as fp:
            template = fp.read()

        # Load the replacements.
        with open('replacements.json') as fp:
            replacements = json.load(fp, object_pairs_hook=odict)

        for replacement in replacements:
            template = template.replace(
                replacement, str(replacements[replacement]))

        # Write the input file.
        self.inputName = 'input.lua'
        with open(self.inputName, 'w') as fp:
            fp.write(template)

        # Run Quanty.
        config = Config()
        settings = config.read()
        self.executable = settings.value('Quanty/Path')
        self.runQuanty()

        # Customize the error message.
        self.message = 'in test #{} failed.'.format(self.index)

    def runQuanty(self):
        try:
            output = subprocess.check_output([self.executable, self.inputName])
        except subprocess.CalledProcessError:
            raise
        self.output = output.decode('utf-8').splitlines()
        return self.output

    def testEnergy(self):
        output = iter(self.output)
        for line in output:
            if 'Analysis' in line:
                lines_to_skip = 3
                for i in range(lines_to_skip):
                    next(output)
                line = next(output)
                energy = float(line.split()[1])
        expected = self.parameters['energy']
        message = 'testEnergy {}'.format(self.message)
        self.assertEqual(energy, expected, message)

    def loadSpectrum(self, fileName):
        experiment = self.parameters['experiment']
        if experiment == 'XAS':
            spectrum = np.loadtxt(fileName, skiprows=5, usecols=2)
        return spectrum

    def testSpectrum(self):
        spectrumName = 'input_{}.spec'.format(self.parameters['spectrum'])
        spectrum = self.loadSpectrum(spectrumName)
        referenceName = 'reference_{}.spec'.format(self.parameters['spectrum'])
        reference = self.loadSpectrum(referenceName)
        message = 'testSpectrum {}'.format(self.message)
        np.testing.assert_allclose(spectrum, reference, err_msg=message)


def suite():
    test_suite = unittest.TestSuite()

    with open(resourceFileName('quanty:test/tests/tests.json')) as fp:
        tests = json.loads(fp.read(), object_pairs_hook=odict)

    for test in tests:
        parameters = tests[test]
        test_suite.addTest(parameterize(TestQuanty, test, parameters))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite', verbosity=2)
