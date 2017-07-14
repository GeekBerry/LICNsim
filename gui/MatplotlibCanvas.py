from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from debug import showCall


# ======================================================================================================================
class PolyLineCanvas(FigureCanvasQTAgg):  # issubclass(FigureCanvasQTAgg, QWidget)
    def __init__(self, parent=None):
        fig = Figure(figsize=(1, 1) )
        # fig = Figure()

        super().__init__(fig)
        self.setParent(parent)

        self.axes= fig.add_subplot(1,1,1)
        self.axes.set_xticks([])
        self.axes.set_yticks([])

        self.twin_x= self.axes.twinx()
        self.twin_x.set_xticks([])
        self.twin_x.set_yticks([])

        self.draw()

    def drawPolyLine(self, indexs, values, color='r', clear= True):
        if not values:
            return

        if clear:
            self.axes.cla()

        self.axes.set_ylim(-0.1*max(values), 1.1*max(values)+1)
        self.axes.plot(indexs, values, color)

        # self.axes.bar(indexs, values)  # FIXME 好不好用???

        self.draw()

    def drawTwinX(self, indexs, values, color='b', clear= True):
        if not values:
            return

        if clear:
            self.twin_x.cla()

        self.twin_x.set_ylim(-0.1*max(values), 1.1*max(values)+1)
        self.twin_x.plot(indexs, values, color)

        self.draw()

    # def drawXLine(self, value, color='b'):
    #     self.axes.plot( self.axes.get_xbound(), [value,value], color)
    #     self.draw()
