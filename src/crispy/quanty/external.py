import logging

from silx.gui.qt import Qt

from crispy.items import SelectableItem

logger = logging.getLogger(__name__)


class ExternalData(SelectableItem):
    def __init__(self, raw=None, parent=None, *, name="Experiment"):
        super().__init__(parent=parent, name=name)
        self.raw = raw
        self.enable()

    def flags(self, column):
        # Allow the title (column 0) to be edited; the name setter emits
        # dataChanged, which replots and refreshes the legend.
        flags = super().flags(column)
        if column == 0:
            return flags | Qt.ItemIsEditable
        return flags

    def plot(self, plotWidget):
        index = self.childPosition()
        legend = f"{index + 1} · {self.name}"
        x, y = self.raw.T
        plotWidget.addCurve(x, y, legend=legend)
