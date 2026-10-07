"""Utility functions/mixins"""

import logging
import sys

from silx.gui.qt import (
    QApplication,
    QFontDatabase,
)

logger = logging.getLogger(__name__)


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
