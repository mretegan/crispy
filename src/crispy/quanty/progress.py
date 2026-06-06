"""A dialog showing the progress of the calculation."""

import logging
import os
from itertools import cycle

import qtawesome as qta
from silx.gui.qt import QApplication, QDialog, QSize, QTimer

from crispy import resourceAbsolutePath
from crispy.uic import loadUi

logger = logging.getLogger(__name__)


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        uiPath = os.path.join("quanty", "uis", "progress.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.message = "The calculation is running. Please wait"
        dots = [".", "..", "..."]
        self.dots = cycle(dots)
        self.currentMessage = self.message + next(self.dots)

        self.label.setText(self.currentMessage)
        # Reserve room for the longest message so the cycling dots do not change
        # the label width and shift the cancel button while the dialog is shown.
        longest = self.message + max(dots, key=len)
        self.label.setMinimumWidth(self.label.fontMetrics().horizontalAdvance(longest))
        self.cancelButton.setIcon(qta.icon("fa6s.stop", color="#e53935"))
        # Scale the icon to the text height; the default button icon size is too
        # large and renders the stop square as an oversized block.
        iconSize = self.cancelButton.fontMetrics().ascent()
        self.cancelButton.setIconSize(QSize(iconSize, iconSize))
        self.cancelButton.clicked.connect(self.reject)

        timer = QTimer(self, interval=750, timeout=self.changeMessage)
        timer.start()

        # The .ui geometry is shorter than the content needs at the actual font
        # size; size the dialog to its content before it is shown so it does not
        # briefly appear compressed on first display.
        self.adjustSize()

    def changeMessage(self):
        self.currentMessage = self.message + next(self.dots)
        self.label.setText(self.currentMessage)

    def showEvent(self, event):
        super().showEvent(event)
        parent = self.parent()
        if parent is not None:
            geometry = self.frameGeometry()
            geometry.moveCenter(parent.window().frameGeometry().center())
            self.move(geometry.topLeft())

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
