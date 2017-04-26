#!/usr/bin/python3
#coding=utf-8

import sys
import debug
import constants

from core import Packet, Name, Monitor, AnnounceTableLog, Channel, ICNNetHelper, AskGenerator, clock
from core.algorithm import FixedAsk, UniformPosition, SamplePosition
from example_normal.node import Node

from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QApplication
from visualizer import MainWindow, UINetHelper
from visualizer.node_item import NodeItem
from visualizer.edge_item import EdgeItem

#=======================================================================================================================
from random import randint
def TestChannel(src, dst):
    return Channel(src, dst, rate= randint(1, 10), buffer_size= 1000, delay= SECOND//1000, loss= 0.5)

SECOND= 1000
ip_A= Packet(Name('/A'), Packet.INTEREST, 1)
dp_A= Packet(Name('/A'), Packet.DATA, 500)
#=======================================================================================================================
graph = constants.GraphGrid11X11().graph
# graph= constants.GraphBA50().graph
# graph= networkx.DiGraph( networkx.path_graph(2) )

ICNNetHelper.setup(graph, Node, TestChannel)  # 把graph变成icn graph
monitor= Monitor(graph)  # 数据库监听graph

logger= AnnounceTableLog()
logger.addHardwares( ICNNetHelper.nodes(graph) )
logger.addHardwares( ICNNetHelper.edges(graph) )

# 请求发生器
ICNNetHelper.node(graph, (0,0)).api['CS::store'](dp_A)  # 要在CS类型配置之后,才会被正确驱逐

ask_gen= AskGenerator(graph, FixedAsk(1), UniformPosition(graph), ip_A, delta= SECOND//100)
ask_gen.start(0)

# clock.timing(1000, ICNNetHelper.node(graph, 0).api['CS::setCapacity'], 0)

if __name__ == '__main__':
    USE_GUI= True
    if USE_GUI:
        app = QApplication(sys.argv)  # 必须放在MainWindow前

        UINetHelper.setup(graph, NodeItem, EdgeItem)  # 把graph变成ui graph
        main_window= MainWindow(graph, monitor, logger)

        for (x,y), node in UINetHelper.nodeItems(graph):
            node.setPos( QPointF(x*200, y*200) )
        main_window.scene.adaptive()

        main_window.show()

        debug.timeProfile('app.exec_()'); sys.exit()
        # sys.exit(app.exec_())
    else:
        import constants
        from core.clock import clock
        for i in range(0, constants.INF):
            clock.step()
            print('step: ', i)

