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


import re
import sys
import numpy as np
import transformations


class dict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


class Tensor(object):
    '''Class for tensor objects'''

    def __init__(self, tensor):
        self.tensor = tensor
        '''Start by diagonalizing the tensor. Next sort the eigenvalues
        according to some requirement specific to a particular tensor.
        This method is usually overloaded by the subclasses that inherit
        from Tensor. Finally calculate all the possible Euler angles.
        The rotation matrix resulted from the eigenvectors has to have a
        positive determinant in order to be considered a proper rotation.
        This can be achived by multipling the columns with -1.'''
        self.diagonalize()
        self.sort()
        self.euler_angles_and_eigenframes()

    def diagonalize(self):
        '''Diagonalize the tensor.'''
        self.eigvals, self.eigvecs = np.linalg.eig(
            (self.tensor.transpose() + self.tensor) / 2.0)
        self.eigvals = np.diag(np.dot(
            np.dot(self.eigvecs.transpose(), self.tensor), self.eigvecs))

    def sort(self):
        '''Sort the eigenvalues and eigenvectors according to the indexes
           that result in increasing eigenvalues in absolute value.'''
        self.ids = np.argsort(np.abs(self.eigvals))
        self.eigvals = self.eigvals[self.ids]
        self.eigvecs = self.eigvecs[:, self.ids]

    def euler_angles_and_eigenframes(self):
        '''Calculate the Euler angles only if the rotation matrix
           (eigenframe) has positive determinant.'''
        signs = np.array([[1, 1, 1], [-1, 1, 1], [1, -1, 1],
                          [1, 1, -1], [-1, -1, 1], [-1, 1, -1],
                          [1, -1, -1], [-1, -1, -1]])
        eulangs = []
        eigframes = []
        for i, sign in enumerate(signs):
            eigframe = np.dot(self.eigvecs, np.diag(sign))
            if np.linalg.det(eigframe) > 1e-4:
                eigframes.append(np.array(eigframe))
                eulangs.append(np.array(
                    transformations.euler_from_matrix(eigframe, axes='szyz')))

        self.eigframes = np.array(eigframes)
        # The sign has to be inverted to be consistent with ORCA and EasySpin.
        self.eulangs = -np.array(eulangs)


class DTensor(Tensor):
    '''Class to deal with D-tensors. The sort function has to be redefined.'''

    def __init__(self, tensor, make_traceless=True):
        self.make_traceless = make_traceless
        Tensor.__init__(self, tensor)

    def calculate_anisotropy_parameters(self):
        self.D = -0.5 * (self.eigvals[0] + self.eigvals[1]) + self.eigvals[2]
        self.E = 0.5 * (self.eigvals[0] - self.eigvals[1])
        if np.abs(self.D) < 1e-5:
            self.components = [self.D, self.E, 0]
        else:
            self.components = [self.D, self.E, self.E/self.D]

    def sort(self):
        if self.make_traceless:
            self.eigvals = self.eigvals - self.eigvals.mean()
            self.make_traceless = True

        self.ids = np.argsort(np.abs(self.eigvals))
        self.eigvals = self.eigvals[self.ids]
        self.eigvecs = self.eigvecs[:, self.ids]

        if self.make_traceless:
            self.calculate_anisotropy_parameters()


class gTensor(Tensor):
    '''Class to deal with g-tensors'''

    def __init__(self, tensor):
        tensor = np.dot(tensor.transpose(), tensor)
        Tensor.__init__(self, tensor)

    def sort(self):
        self.eigvals = np.sqrt(self.eigvals)
        self.ids = np.argsort(np.abs(self.eigvals))
        self.eigvals = self.eigvals[self.ids]
        self.eigvecs = self.eigvecs[:, self.ids]


class ATensor(Tensor):
    '''Class to deal with A-tensors.'''

    def __init__(self, tensor):
        Tensor.__init__(self, tensor)


class OutputData(object):
    '''Extract data from the ORCA output.'''

    def __init__(self, output):
        self.output = open(output, 'r')
        self.parse()

    def _skip_lines(self, n):
        '''Skip a number of lines from the output.'''
        for i in range(n):
            self.line = next(self.output)
        return self.line

    def _parse_tensor(self, indices=False):
        '''Parse a tensor.'''
        if indices:
            self.line = self._skip_lines(1)

        tensor = np.zeros((3, 3))
        for i in range(3):
            tokens = self.line.split()
            if indices:
                tensor[i][0] = float(tokens[1])
                tensor[i][1] = float(tokens[2])
                tensor[i][2] = float(tokens[3])
            else:
                tensor[i][0] = float(tokens[0])
                tensor[i][1] = float(tokens[1])
                tensor[i][2] = float(tokens[2])
            self.line = self._skip_lines(1)
        return tensor

    def _parse_components(self):
        tokens = self.line.split()
        components = np.zeros((3,))
        components[0] = float(tokens[1])
        components[1] = float(tokens[2])
        components[2] = float(tokens[3])
        self.line = self._skip_lines(1)
        return components

    def parse(self):
        '''Iterate over the lines and extract the required data.'''
        for self.line in self.output:
            # Parse general data: charge, multiplicity, coordinates, etc.
            self.index = 0

            if self.line[1:13] == 'Total Charge':
                tokens = self.line.split()
                self.charge = int(tokens[-1])

            if (self.line[1:13] or self.line[0:12]) == 'Multiplicity':
                tokens = self.line.split()
                self.multiplicity = int(tokens[-1])

            if self.line[0:33] == 'CARTESIAN COORDINATES (ANGSTROEM)':
                if not hasattr(self, 'names'):
                    self.names = dict()
                if not hasattr(self, 'coords'):
                    self.coords = dict()
                self.line = self._skip_lines(2)
                names = list()
                coords = list()
                while self.line.strip():
                    tokens = self.line.split()
                    names.append(tokens[0])
                    x = float(tokens[1])
                    y = float(tokens[2])
                    z = float(tokens[3])
                    coords.append((x, y, z))
                    self.line = next(self.output)
                self.names = np.array(names)
                self.coords[self.index] = np.array(coords)

            if self.line[22:50] == 'MULLIKEN POPULATION ANALYSIS':
                if not hasattr(self, 'populations'):
                    self.populations = dict()
                self.line = self._skip_lines(6)
                populations = list()
                while self.line.strip() and 'Sum' not in self.line:
                    tokens = self.line.split()
                    populations.append((float(tokens[-2]), float(tokens[-1])))
                    self.line = next(self.output)
                self.populations['mulliken'][self.index] = np.array(populations) # noqa

            # Parse data from the EPR/NMR module
            if self.line[37:44] == 'EPR/NMR':
                self.eprnmr = dict()

            if self.line[0:19] == 'ELECTRONIC G-MATRIX':
                self.line = self._skip_lines(4)
                self.eprnmr['g']['tensor'] = self._parse_tensor()

            if self.line[0:27] == 'ZERO-FIELD-SPLITTING TENSOR':
                self.line = self._skip_lines(4)
                self.eprnmr['zfs']['tensor'] = self._parse_tensor()

            if self.line[1:8] == 'Nucleus':
                tokens = self.line.split()
                nucleus = int(re.findall(r'\d+', tokens[1])[0])
                while 'Raw HFC' not in self.line:
                    self.line = self._skip_lines(1)
                self.line = self._skip_lines(2)
                self.eprnmr['hfc'][nucleus]['tensor'] = self._parse_tensor()
                self.line = self._skip_lines(1)
                self.eprnmr['hfc'][nucleus]['fc'] = self._parse_components()
                self.eprnmr['hfc'][nucleus]['sd'] = self._parse_components()
                self.line = self._skip_lines(1)
                self.eprnmr['hfc'][nucleus]['orb'] = self._parse_components()
                self.eprnmr['hfc'][nucleus]['dia'] = self._parse_components()

            # Parse data from the MRCI module
            if self.line[36:43] == 'M R C I':
                self.mrci = dict()

            if self.line[1:19] == 'SPIN-SPIN COUPLING':
                self.line = self._skip_lines(4)
                self.mrci['zfs']['ssc']['tensor'] = self._parse_tensor()

            if self.line[1:30] == '2ND ORDER SPIN-ORBIT COUPLING':
                while 'Second' not in self.line:
                    self.line = self._skip_lines(1)
                self.line = self._skip_lines(1)
                self.mrci['zfs']['soc']['second_order']['0']['tensor'] = self._parse_tensor() # noqa
                self.line = self._skip_lines(2)
                self.mrci['zfs']['soc']['second_order']['m']['tensor'] = self._parse_tensor() # noqa
                self.line = self._skip_lines(2)
                self.mrci['zfs']['soc']['second_order']['p']['tensor'] = self._parse_tensor() # noqa

            if self.line[1:42] == 'EFFECTIVE HAMILTONIAN SPIN-ORBIT COUPLING':
                self.line = self._skip_lines(4)
                self.mrci['zfs']['soc']['heff']['tensor'] = self._parse_tensor() # noqa


def main():
    data = OutputData(sys.argv[1])
    print(data.__dict__)


if __name__ == '__main__':
    main()
