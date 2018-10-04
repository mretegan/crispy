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

from __future__ import absolute_import, division, unicode_literals

__authors__ = ['Marius Retegan']
__license__ = 'MIT'
__date__ = '03/10/2018'


# from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QComboBox, QLineEdit
from PyQt5.QtGui import QIntValidator, QDoubleValidator


class ComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super(ComboBox, self).__init__(*args, **kwargs)

    def setItems(self, items, currentItem):
        self.blockSignals(True)
        self.clear()
        self.addItems(items)
        self.setCurrentText(currentItem)
        self.blockSignals(False)


class LineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(LineEdit, self).__init__(*args, **kwargs)


class IntLineEdit(LineEdit):
    def __init__(self, *args, **kwargs):
        super(IntLineEdit, self).__init__(*args, **kwargs)
        self.setValidator(QIntValidator(self))

    def getValue(self):
        return int(self.text())

    def setValue(self, value):
        self.setText(str(value))


class DoubleLineEdit(LineEdit):
    def __init__(self, *args, **kwargs):
        super(DoubleLineEdit, self).__init__(*args, **kwargs)
        validator = QDoubleValidator(self)
        self.setValidator(validator)

    def getValue(self):
        return float(self.text())

    def setValue(self, value):
        self.setText(str(value))


class VectorLineEdit(LineEdit):
    def __init__(self, *args, **kwargs):
        super(VectorLineEdit, self).__init__(*args, **kwargs)

    def getVector(self):
        text = self.text()
        if '(' not in text or ')' not in text:
            raise ValueError

        text = text[1:-1].split(',')

        try:
            vector = list(map(int, text))
        except ValueError:
            try:
                vector = list(map(float, text))
            except ValueError:
                raise
            else:
                return vector
        else:
            return vector

    def setVector(self, vector):
        text = str(tuple(vector))
        self.setText(text)


class DoubleListLineEdit(LineEdit):
    def __init__(self, *args, **kwargs):
        super(DoubleListLineEdit, self).__init__(*args, **kwargs)

    def getList(self):
        text = self.text().split(',')
        try:
            values = list(map(float, text))
        except ValueError:
            raise
        else:
            return values

    def setList(self, values):
        if not isinstance(values, list):
            values = [values]
        self.setText(', '.join(map(str, values)))
