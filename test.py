from core.common import *

# timeProfile('import sim')

# TODO 数据库
# TODO demo 数据采集
# TODO 物联网
# TODO 图形库

#=======================================================================================================================
# top_graph = networkx.random_graphs.barabasi_albert_graph(50, 1)
# top_graph= networkx.grid_2d_graph(10, 10)
# top_graph= networkx.balanced_tree(3, 4)
# top_graph= networkx.watts_strogatz_graph(20, 4, 0.3)
# top_graph= networkx.DiGraph(top_graph)
#
# pos = networkx.spring_layout(top_graph)
# networkx.draw(top_graph, pos, with_labels = True, node_size = 1)
# plt.show()
#
#
# def step(t):
#     # plt.clf()
#
#     global pos
#
#     a= plt.axis()
#     ret= plt.text(a[0],a[2], str(t))
#     pos = networkx.spring_layout(top_graph, pos= pos)
#     node_collection= networkx.draw_networkx_nodes(top_graph, pos, node_size = 1)
#     edge_collection = networkx.draw_networkx_edges(top_graph, pos, arrows= True)
#     # networkx.draw_networkx_labels(top_graph, pos)
#
#     return node_collection, edge_collection, ret
#     # plt.savefig( 'pic/%02d.png'%(i) )
#     # plt.show()
#     # plt.close()
#
#
# import matplotlib.animation as animation
# fig = plt.figure()
#
# ani = animation.FuncAnimation(
#     fig= fig, #(必要) 绘制的画布
#     func= step,# (必要) 每次执行此函数
#     fargs= None,# 每次调用func传给func 的参数
#     # frames= 100, #
#     # interval= 1, # 时间间隔
#     # init_func= init, #初始化画布
#     blit= True #重绘
# )
#
# plt.show()

#=======================================================================================================================
def nodeForce(graph, node, pos):
    link_vec= numpy.array([0.0, 0.0])
    space_vec= numpy.array([0.0, 0.0])

    for other in graph.nodes():
        if other != node:
            vec= pos[other]- pos[node]
            vls= numpy.sum(numpy.square(vec)) # vls= vector length square

            if True: #and vls < 0.001:
                space_vec -= vec/vls# 空间中节点间为排斥力

            if other in graph[node] :#and vls >0.001:
                link_vec += vec # 连接的节点间为吸引力

    # print(link_vec + space_vec)
    pos[node] += (link_vec + space_vec) * 0.8
    # pos[node] += link_vec/len( graph[node] ) + space_vec/( len(graph)-1 )


def graphLayout(graph, pos= None, iterations= 30):
    if pos is None:
        # pos = networkx.spring_layout(top_graph)
        pos= { node:numpy.random.rand(2) for node in graph }

    for i in range(0,iterations):
        for node in pos:
            nodeForce(graph, node, pos)

    return pos


# pos= graphLayout(graph)
# graph.draw(pos)




import networkx
import matplotlib.pyplot as plt

# top_graph = networkx.random_graphs.barabasi_albert_graph(50, 1)
top_graph= networkx.grid_2d_graph(10, 10)
# top_graph= networkx.balanced_tree(2, 4)
# top_graph= networkx.watts_strogatz_graph(20, 4, 0.3)

# top_graph= networkx.DiGraph(top_graph)


# net= ICNNet(top_graph, SimpleNode, NoQueueChannel)

# width= []
# for src, dst in top_graph.edges():
#     width.append( random.random() )
#
pos= networkx.spring_layout(top_graph)
networkx.draw(top_graph, pos, with_labels = True, node_size = 1)

from matplotlib.backends import pylab_setup

# backend_mod, new_figure_manager, draw_if_interactive, show = pylab_setup()
# show()

# import matplotlib.backends.backend_tkagg
# backend = matplotlib.get_backend() # validates, to match all_backends
# if backend.startswith('module://'):
#     backend_name = backend[9:]
# else:
#     backend_name = 'backend_'+backend
#     backend_name = backend_name.lower() # until we banish mixed case
#     backend_name = 'matplotlib.backends.%s'%backend_name.lower()
# print(backend_name)

# plt.show()


#=======================================================================================================================
import sys
import random

import matplotlib
matplotlib.use("Qt5Agg")

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyMplCanvas(FigureCanvas):
    """这是一个窗口部件，即QWidget"""
    def __init__(self, parent=None):
        fig = Figure(figsize=(10, 10), dpi=100)
        super().__init__(fig)
        self.setParent(parent)
        self.axes = fig.add_subplot(111)
        #self.axes.hold(False)# 每次plot()调用的时候，我们希望原来的坐标轴被清除(所以False)

        self.pos= networkx.spring_layout(top_graph)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.step)
        timer.start(100)

        self.init()

    def init(self):
        pass

    def step(self):#不能叫update
        self.axes.cla()# 清空当前坐标

        self.pos= graphLayout(top_graph, self.pos, 1)
        networkx.draw(top_graph, self.pos, ax= self.axes, node_size= 1, with_labels = False)

        # edge_labels= { edge:random.randint(0,99) for edge in top_graph.edges() }
        # networkx.draw_networkx_edge_labels(top_graph, self.pos, ax= self.axes, label_pos= 0.3,  edge_labels= edge_labels, rotate= False)

        self.draw()



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



if __name__ == '__main__':
    app = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.show()
    app.exec_()




# Successfully created project 'LICNsim' on GitHub, but initial commit failed:
# *** Please tell me who you are. Run
# git config --global user.email "you@example.com"
# git config --global user.name "Your Name"
# to set your accounts default identity.
# Omit --global
# to set the identity only in this repository.
# fatal: empty ident name (for (NULL)>) not allowed during executing
# git E:\program\Git\bin\git.exe -c core.quotepath=false commit -m "Initial commit" --
