###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""Utility functions/mixins"""

import logging
import sys
import warnings

from silx.gui.qt import (
    QApplication,
    QFontDatabase,
)

logger = logging.getLogger(__name__)


def disconnectSignal(signal):
    """Disconnect all slots from a signal, ignoring the case where none are connected.

    PyQt raises TypeError/RuntimeError when nothing is connected, while PySide6
    instead emits a RuntimeWarning from libpyside. Handle both so the signal can
    be cleared silently before reconnecting.
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            signal.disconnect()
    except (TypeError, RuntimeError):
        pass


def fixedFont():
    font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
    if sys.platform == "darwin":
        font.setPointSize(font.pointSize() + 2)
    return font


def findQtObject(name=None):
    """Find a Qt object by name."""
    assert name is not None, "The object name must be provided."

    app = QApplication.instance()
    for widget in app.allWidgets():
        if widget.objectName() == name:
            return widget
    return None
