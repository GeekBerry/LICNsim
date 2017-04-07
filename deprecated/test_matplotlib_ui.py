import sys
import random

import matplotlib
matplotlib.use("Qt5Agg")

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import networkx, numpy
import matplotlib.pyplot as plt


# top_graph= networkx.path_graph(3)
# top_graph = networkx.random_graphs.barabasi_albert_graph(20, 1)
top_graph= networkx.grid_2d_graph(5, 5)
# top_graph= networkx.balanced_tree(2,2)
# top_graph= networkx.watts_strogatz_graph(20, 4, 0.3)

# top_graph= networkx.DiGraph(top_graph)


class MyMplCanvas(FigureCanvas):
    """这是一个窗口部件，即QWidget"""
    def __init__(self, parent=None):
        fig = Figure(figsize=(10, 10), dpi= 100)


        super().__init__(fig)
        self.setParent(parent)


        # self.axes= fig.add_subplot(111)
        self.axes = fig.add_axes([0, 0, 1, 1])

        #self.axes.hold(False)# 每次plot()调用的时候，我们希望原来的坐标轴被清除(所以False)

        # timer = QtCore.QTimer(self)
        # timer.timeout.connect(self.step)
        # timer.start(100)
        self.init()

    def type(self):
        return 3

    def init(self):
        # self.pos= _graphLayout(top_graph,iterations= 100)
        # self.pos= {0:numpy.array([0.0,0.0]), 1:numpy.array([1.0,0.0]) , 2:numpy.array([20.0,0.0])}
        self.pos= networkx.spring_layout(top_graph)

    def paint(self, painter, option, widget):
        pass

    def update(self):  # 不能叫update
        self.axes.cla()  # 清空当前坐标

        networkx.draw_networkx(top_graph, self.pos, ax= self.axes, node_size= 1, with_labels = True)

        array= [
        numpy.linalg.norm(self.pos[src]-self.pos[dst])
        for src,dst in top_graph.edges() ]
        array.sort()

        print(array[len(array)//2])

        # print( numpy.linalg.norm(self.pos[2,3]-self.pos[2,2]))
        # print( numpy.linalg.norm(self.pos[2,3]-self.pos[2,2]))

        # networkx.draw_networkx_nodes(top_graph, self.pos, ax= self.axes)
        # networkx.draw_networkx_edges(top_graph, self.pos, ax= self.axes)

        # edge_labels= { edge:random.randint(0,99) for edge in top_graph.edges() }
        # networkx.draw_networkx_edge_labels(top_graph, self.pos, ax= self.axes, label_pos= 0.3,  edge_labels= edge_labels, rotate= False)

        # self.draw()




class ApplicationWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.main_widget = QWidget(self)

        l = QVBoxLayout(self.main_widget)
        dc = MyMplCanvas(self.main_widget)
        l.addWidget(dc)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)



if __name__ == '__main__'  and 1:
    app = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.show()
    app.exec_()
