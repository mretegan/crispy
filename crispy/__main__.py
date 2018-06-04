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
__date__ = '05/12/2017'


def main():
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt, QLocale

    from .gui.main import MainWindow

    from silx.resources import register_resource_directory
    register_resource_directory('crispy', 'crispy.resources')

    locale = QLocale(QLocale.C)
    locale.setNumberOptions(QLocale.RejectGroupSeparator)
    QLocale.setDefault(locale)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
