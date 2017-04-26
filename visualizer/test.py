#!/usr/bin/python3
#coding=utf-8


import debug
from core.database import AnnounceTableLog
from core.channel import OneStepChannel
from core.algorithm import FixedAsk, UniformPosition
from core.icn_net import ICNNetHelper, AskGenerator
from example_CB.experiment_net import ExperimentMonitor
from example_CB.experiment_node import SimulatCSUnit, ExperimentNode


import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QPointF
from visualizer.ui_net import UINetHelper
from visualizer.main_window import MainWindow
from visualizer.node_item import NodeItem
from visualizer.edge_item import EdgeItem
#=======================================================================================================================
# graph_info = constants.GraphBA50()
graph_info = constants.GraphGrid11X11()

ICNNetHelper.setup(graph_info.graph, ExperimentNode, OneStepChannel)  # 把graph变成icn graph
monitor= ExperimentMonitor(graph_info.graph)  # 数据库监听graph

logger= AnnounceTableLog()
logger.addHardwares( ICNNetHelper.nodes(graph_info.graph) )
logger.addHardwares( ICNNetHelper.edges(graph_info.graph) )
# -----------------------------------------------------------------------------
# 初始化缓存
for node in ICNNetHelper.nodes(graph_info.graph):
    node.api['CS::setMode'](SimulatCSUnit.MODE.FIFO)
    node.api['CS::setLifeTime'](100*graph_info.diameter)
ICNNetHelper.node(graph_info.graph, graph_info.center).api['CS::setMode'](SimulatCSUnit.MODE.MANUAL)  # 要在设置全局mode之后
ICNNetHelper.node(graph_info.graph, graph_info.center).api['CS::store'](constants.debug_dp)  # 要在CS类型配置之后,才会被正确驱逐
# 请求发生器
ask_gen= AskGenerator(graph_info.graph, FixedAsk(1), UniformPosition(graph_info.graph), constants.debug_ip, delta=4 * graph_info.diameter)
ask_gen.start(0)
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    USE_GUI= True

    if USE_GUI:
        app = QApplication(sys.argv)  # 必须放在MainWindow前
        UINetHelper.setup(graph_info.graph, NodeItem, EdgeItem)  # 把graph变成ui graph
        main_window= MainWindow(graph_info.graph, monitor, logger)

        for (x,y), node in UINetHelper.nodeItems(graph_info.graph):
            node.setPos( QPointF(x*200, y*200) )
        main_window.scene.adaptive()

        main_window.show()
        debug.timeProfile('app.exec_()')
        sys.exit()
        # sys.exit(app.exec_())
    else:
        import constants
        from core.clock import clock
        for i in range(0, constants.INF):
            clock.step()
