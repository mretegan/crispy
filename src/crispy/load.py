"""Dialog to load data from an ASCII file."""

import html
import logging
import os
from itertools import islice

from silx.gui.qt import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QPoint,
    QSize,
    QTextEdit,
)

from crispy import resourceAbsolutePath
from crispy.config import Config
from crispy.uic import loadUi
from crispy.utils import fixedFont

logger = logging.getLogger(__name__)

# Number of lines shown in the file preview.
PREVIEW_LINES = 100

# Colors used to highlight the selected columns in the preview.
X_COLOR = "#1f77b4"
Y_COLOR = "#d62728"

# Common column separators as (label, delimiter passed to numpy.loadtxt).
SEPARATORS = (
    ("Whitespace", None),
    ("Comma", ","),
    ("Semicolon", ";"),
    ("Tab", "\t"),
)


class LoadDataDialog(QDialog):
    """Collect the parameters used to load data from an ASCII file."""

    def __init__(self, parent=None):
        super().__init__(parent)

        uiPath = os.path.join("uis", "load.ui")
        loadUi(resourceAbsolutePath(uiPath), baseinstance=self)

        self.path = None

        self.previewTextEdit.setFont(fixedFont())
        self.previewTextEdit.setLineWrapMode(QTextEdit.NoWrap)

        # Tie the column labels to the colors used in the preview.
        self.xAxisLabel.setStyleSheet(f"color: {X_COLOR};")
        self.yAxisLabel.setStyleSheet(f"color: {Y_COLOR};")

        for label, value in SEPARATORS:
            self.separatorComboBox.addItem(label, value)

        self.fileBrowsePushButton.clicked.connect(self.selectFile)

        self.commentLineEdit.textChanged.connect(self.updatePreview)
        self.separatorComboBox.currentIndexChanged.connect(self.updatePreview)
        self.xAxisSpinBox.valueChanged.connect(self.updatePreview)
        self.yAxisSpinBox.valueChanged.connect(self.updatePreview)

        self.okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.okButton.clicked.connect(self.accept)
        # Nothing can be loaded until a file is selected.
        self.okButton.setEnabled(False)

        cancel = self.buttonBox.button(QDialogButtonBox.Cancel)
        cancel.clicked.connect(self.reject)

    def showEvent(self, event):
        self.loadSettings()
        super().showEvent(event)

    def accept(self):
        self.saveSettings()
        super().accept()

    def loadSettings(self):
        settings = Config().read()
        settings.beginGroup("LoadData")

        size = settings.value("Size")
        if size is not None:
            self.resize(QSize(size))

        pos = settings.value("Position")
        if pos is not None:
            self.move(QPoint(pos))

        self.commentLineEdit.setText(settings.value("Comment", "#"))
        self.separatorComboBox.setCurrentText(settings.value("Separator", "Whitespace"))
        self.xAxisSpinBox.setValue(settings.value("XAxis", 0, type=int))
        self.yAxisSpinBox.setValue(settings.value("YAxis", 1, type=int))

        settings.endGroup()

    def saveSettings(self):
        settings = Config().read()
        settings.beginGroup("LoadData")
        settings.setValue("Comment", self.commentLineEdit.text())
        settings.setValue("Separator", self.separatorComboBox.currentText())
        settings.setValue("XAxis", self.xAxisSpinBox.value())
        settings.setValue("YAxis", self.yAxisSpinBox.value())
        settings.setValue("Size", self.size())
        settings.setValue("Position", self.pos())
        settings.endGroup()
        settings.sync()

    def selectFile(self):
        settings = Config().read()
        directory = settings.value("CurrentPath") or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(self, "Select File", directory)
        if not path:
            return

        settings.setValue("CurrentPath", os.path.dirname(path))
        settings.sync()

        self.path = path
        self.fileLineEdit.setText(path)
        self.fileLineEdit.setCursorPosition(0)
        self.updatePreview()
        self.okButton.setEnabled(True)

    def updatePreview(self):
        if self.path is None:
            return

        try:
            with open(self.path) as handle:
                lines = list(islice(handle, PREVIEW_LINES))
        except OSError:
            logger.error(f"Failed to read {self.path}")
            self.previewTextEdit.clear()
            return

        comment = self.comment
        separator = self.separator

        rows = []
        for line in lines:
            line = line.rstrip("\n")
            if comment is not None and line.lstrip().startswith(comment):
                rows.append(f'<span style="color: gray;">{html.escape(line)}</span>')
                continue
            tokens = line.split(separator)
            visibleSeparator = html.escape(" " if separator is None else separator)
            rows.append(visibleSeparator.join(self.colorize(tokens)))

        self.previewTextEdit.setHtml("<pre>" + "\n".join(rows) + "</pre>")

    def colorize(self, tokens):
        """Wrap the selected columns in colored spans."""
        rendered = []
        for index, token in enumerate(tokens):
            escaped = html.escape(token)
            if index == self.xAxis:
                escaped = f'<span style="color: {X_COLOR};">{escaped}</span>'
            elif index == self.yAxis:
                escaped = f'<span style="color: {Y_COLOR};">{escaped}</span>'
            rendered.append(escaped)
        return rendered

    @property
    def comment(self):
        """Comment character, or None to disable comment parsing."""
        return self.commentLineEdit.text() or None

    @property
    def separator(self):
        """Column separator, or None to split on any whitespace."""
        return self.separatorComboBox.currentData()

    @property
    def xAxis(self):
        return self.xAxisSpinBox.value()

    @property
    def yAxis(self):
        return self.yAxisSpinBox.value()
