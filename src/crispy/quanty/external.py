import logging

from crispy.items import SelectableItem

logger = logging.getLogger(__name__)


class ExternalData(SelectableItem):
    def __init__(self, data=None, parent=None, *, name="Experiment"):
        super().__init__(parent=parent, name=name)
        self.data = data
        self.enable()

    def plot(self, plotWidget):
        index = self.childPosition()
        legend = f"{index + 1} · {self.name}"
        x, y = self.data.T
        plotWidget.addCurve(x, y, legend=legend)
