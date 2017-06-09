#!/usr/bin/python3
#coding=utf-8

import sys
import debug
import constants

from core.packet import Packet
from core.name import Name
from core import Monitor, Channel,  clock
from core.icn_net import ICNNetHelper,AskGenerator
from core.algorithm import FixedAsk, ExponentAsk, UniformPosition, SamplePosition
from example_normal.node import TestNode

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
ip_A= Packet(Name('/A/'), Packet.INTEREST, 1)
ip_B= Packet(Name('/A/a'), Packet.INTEREST, 1)

dp_A= Packet(Name('/A/'), Packet.DATA, 500)
dp_B= Packet(Name('/A/a'), Packet.DATA, 500)

# ======================================================================================================================
graph = constants.GraphGrid11X11().graph
# graph= constants.GraphBA50().graph
# graph= networkx.DiGraph( networkx.path_graph(2) )

ICNNetHelper.setup(graph, TestNode, TestChannel)  # 把graph变成icn graph
monitor= Monitor(graph)  # 数据库监听graph

# logger= AnnounceTableLog()
# logger.addHardwares( ICNNetHelper.nodes(graph) )
# logger.addHardwares( ICNNetHelper.edges(graph) )

# 请求发生器
ICNNetHelper.node(graph, (0,0)).api['CS::store'](dp_A)
ICNNetHelper.node(graph, (5,5)).api['CS::store'](dp_B)

ask_gen_A= AskGenerator(graph, FixedAsk(1), UniformPosition(graph), ip_A)
ask_gen_A.start(delta=SECOND // 100, delay=0)

ask_gen_B= AskGenerator(graph, FixedAsk(1), UniformPosition(graph), ip_B)
ask_gen_B.start(delta=SECOND // 200, delay=0)

# clock.timing(1000, ICNNetHelper.node(graph, 0).api['CS::setCapacity'], 0)

if __name__ == '__main__':
    USE_GUI= True
    if USE_GUI:
        app = QApplication(sys.argv)  # 必须放在MainWindow前

        UINetHelper.setup(graph, NodeItem, EdgeItem)  # 把graph变成ui graph
        main_window= MainWindow(graph, monitor, logger=None)

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

