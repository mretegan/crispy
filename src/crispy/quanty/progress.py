###################################################################
# Copyright (c) 2016-2024 European Synchrotron Radiation Facility #
#                                                                 #
# Author: Marius Retegan                                          #
#                                                                 #
# This work is licensed under the terms of the MIT license.       #
# For further information, see https://github.com/mretegan/crispy #
###################################################################
"""A dialog showing the progress of the calculation."""

import logging
import os
from itertools import cycle

from silx.gui.qt import QApplication, QDialog, QTimer

from crispy import resourceAbsolutePath
from crispy.uic import loadUi

logger = logging.getLogger(__name__)


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        uiPath = os.path.join("quanty", "uis", "progress.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.message = "The calculation is running. Please wait"
        self.dots = cycle([".", "..", "..."])
        self.currentMessage = self.message + next(self.dots)

        self.label.setText(self.currentMessage)
        self.cancelButton.clicked.connect(self.reject)

        timer = QTimer(self, interval=750, timeout=self.changeMessage)
        timer.start()

    def changeMessage(self):
        self.currentMessage = self.message + next(self.dots)
        self.label.setText(self.currentMessage)

    def closeEvent(self, event):
        self.reject()
        super().closeEvent(event)


def main():
    app = QApplication([])

    dialog = ProgressDialog()
    dialog.show()

    app.exec()


if __name__ == "__main__":
    main()
