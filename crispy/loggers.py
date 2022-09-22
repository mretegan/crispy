# coding: utf-8
###################################################################
# Copyright (c) 2016-2022 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Loggers"""

import logging
import os

from qtpy.QtCore import QObject, Signal

from crispy.config import Config


def setUpLoggers():
    """Setup the application loggers."""
    logger = logging.getLogger("crispy")
    # Set the top level logger to debug, and refine the handlers.
    # https://stackoverflow.com/questions/17668633/what-is-the-point-of-setlevel-in-a-python-logging-handler
    logger.setLevel(logging.DEBUG)
    # Don't pass events logged by this logger to the handlers of the ancestor loggers.
    # logger.propagate = False

    logfmt = "%(asctime)s.%(msecs)03d | %(name)s | %(levelname)s | %(message)s"
    datefmt = "%Y-%m-%d | %H:%M:%S"
    formatter = logging.Formatter(logfmt, datefmt=datefmt)

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logfile = os.path.join(Config().path, "crispy.log")
    handler = logging.FileHandler(logfile)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    message = f"Debug log file: {logfile}"
    logger.info(message)


# https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
# I just couldn't make this to work on PySide2 as you can't have several inheritance with QObject. To make it work I had to use old signals syntax like this
class Handler(logging.Handler, QObject):
    logUpdated = Signal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent=parent)
        logging.Handler.__init__(self)
        formatter = logging.Formatter("%(message)s")
        self.setFormatter(formatter)
        self.setLevel(logging.INFO)

    def emit(self, record):
        message = self.format(record)
        # self.logUpdated.emit()


class StatusBarHandler(Handler):
    pass


class OutputHandler(Handler):
    pass
