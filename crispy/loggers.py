# coding: utf-8
###################################################################
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Loggers"""

import logging

from PyQt5.QtCore import QObject, pyqtSignal


class Handler(logging.Handler, QObject):
    logUpdated = pyqtSignal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        logging.Handler.__init__(self)
        formatter = logging.Formatter("%(message)s")
        self.setFormatter(formatter)
        self.setLevel(logging.INFO)

    def emit(self, record):
        message = self.format(record)
        self.logUpdated.emit(message)


class StatusBarHandler(Handler):
    pass


class OutputHandler(Handler):
    pass
