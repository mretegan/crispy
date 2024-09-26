import logging
from crispy.items import SelectableItem

logger = logging.getLogger(__name__)


class ExternalData(SelectableItem):
    def __init__(self, parent=None, name="Experiment", x=None, y=None):
        super().__init__(parent=parent, name=name)
        self.x = x
        self.y = y
        self.enable()

    def plot(self, plotWidget):
        index = self.childPosition()
        legend = f"{index + 1}-{self.name}"
        plotWidget.addCurve(self.x, self.y, legend=legend)
