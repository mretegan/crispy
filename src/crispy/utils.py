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

from silx.gui.qt import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDataWidgetMapper,
    QFontDatabase,
)

from crispy.views import Delegate

logger = logging.getLogger(__name__)


def setMappings(mappings):
    """Set the mappings between the model and widgets.
    TODO:
        - Should this be extended to accept other columns?
        - Check if it has a model already.
    """
    column = 1
    mappers = []
    for widget, obj in mappings:
        mapper = QDataWidgetMapper(widget)
        # logger.debug(obj.model())
        mapper.setModel(obj.model())
        mapper.addMapping(widget, column)
        delegate = Delegate(widget)
        mapper.setItemDelegate(delegate)
        mapper.setRootIndex(obj.parent().index())
        mapper.setCurrentModelIndex(obj.index())
        # QDataWidgetMapper needs a focus event to notice a change in the data.
        # To make sure the model is informed about the change, I connected the
        # stateChanged signal of the QCheckBox to the submit slot of the
        # QDataWidgetMapper. The same idea goes for the QComboBox.
        # https://bugreports.qt.io/browse/QTBUG-1818
        if isinstance(widget, QCheckBox):
            signal = widget.stateChanged
            try:
                signal.disconnect()
            except (TypeError, RuntimeError):
                pass
            signal.connect(mapper.submit)
        elif isinstance(widget, QComboBox):
            signal = widget.currentTextChanged
            try:
                signal.disconnect()
            except (TypeError, RuntimeError):
                pass
            signal.connect(mapper.submit)
        mappers.append(mapper)
    return mappers


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
