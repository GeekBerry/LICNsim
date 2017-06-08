
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy

from constants import INF

from debug import showCall


class PolyLineCanvas(FigureCanvasQTAgg):  # issubclass(FigureCanvasQTAgg, QWidget)
    def __init__(self, parent=None):
        fig = Figure(figsize=(1, 1) )
        # fig = Figure()

        super().__init__(fig)
        self.setParent(parent)

        self.axes= fig.add_subplot(1,1,1)
        self.axes.set_xticks([])
        self.axes.set_yticks([])
        self.axes_max= 1

        self.twin_x= self.axes.twinx()
        self.twin_x.set_xticks([])
        self.twin_x.set_yticks([])
        self.twin_x_max= 1

        self.draw()

    @showCall
    def drawPolyLine(self, indexs, values, color='r', clear= True):
        if not values:
            return

        if clear:
            self.axes.cla()

        self.axes_max= max(max(values), self.axes_max)
        self.axes.set_ylim(0, self.axes_max)
        self.axes.plot(indexs, values, color)

        self.draw()

    def drawTwinX(self, indexs, values, color='b', clear= True):
        if not values:
            return

        if clear:
            self.twin_x.cla()

        self.twin_x_max= max(max(values), self.twin_x_max)
        self.twin_x.set_ylim(0, self.twin_x_max)
        self.twin_x.plot(indexs, values, color)

        self.draw()

    # def drawXLine(self, value, color='b'):
    #     self.axes.plot( self.axes.get_xbound(), [value,value], color)
    #     self.draw()

