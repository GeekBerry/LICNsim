#!/usr/bin/python3
#coding=utf-8

from debug import showCall

from random import randint

from core import clock, AnnounceTable, CallTable
from core.icn_net import ICNNetHelper

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QMainWindow, QAction

from visualizer.common import SpinBox
from visualizer.net_scene import NetScene
from visualizer.node_info_dialog import NodeInfoDialog
from visualizer.edge_info_dialog import EdgeInfoDialog


#=======================================================================================================================
class MainWindow(QMainWindow):
    FRAME_DELAY= 1000  # 单位(ms)
    DEFAULT_STEP_SIZE= 1000
    def __init__(self, graph, monitor, logger=None):
        super().__init__()
        from visualizer.ui.ui_main_window import Ui_main_window
        self.ui= Ui_main_window()
        self.ui.setupUi(self)

        self.api= CallTable()
        self.announces= AnnounceTable()
        if logger is not None:
            logger.addAnnounceTable('MainWindow', self.announces)

        self.graph= graph
        self.monitor= monitor
        self.logger= logger

        self.api['Main::showNodeInfo']= self.newNodeInfoDialog
        self.api['Main::showEdgeInfo']= self.newEdgeInfoDialog
        self.api['Main::setLabelNetNode']= self.ui.label_net_node.setText  # 代理label_net实现install
        self.api['Main::setLabelNetEdge']= self.ui.label_net_edge.setText  # 代理label_net实现install

        self.scene= NetScene(self.graph)  # NetScene
        self.scene.install(self.announces, self.api)

        self.ui.view_net.init(self.graph, self.scene, self.monitor)  # NetView
        self.ui.view_net.install(self.announces, self.api)

        self.ui.table_contents.init(self.monitor)  # CSTableWidget
        self.ui.table_contents.install(self.announces, self.api)

        self.ui.tree_packet_head.init(self.monitor)  # PacketHeadTreeWidget
        self.ui.tree_packet_head.install(self.announces, self.api)

        # ---------------------------------------------------------------------
        self.step_timer= QTimer(self)
        self.step_timer.timeout.connect(self.loopSteps)
        self.step_timer.setInterval(self.FRAME_DELAY)

        self.step_size= self.DEFAULT_STEP_SIZE
        steps_spin_box= SpinBox(self, 'step_size')
        steps_spin_box.setRange(0, 10*self.DEFAULT_STEP_SIZE)
        self.ui.toolbar_play.addWidget( steps_spin_box )

        self.updateStatusBar()


    @pyqtSlot(QAction)
    def playToolBarTriggered(self, action):
        if action == self.ui.action_step:
            self.playSteps()
        elif action == self.ui.action_play:
            if action.isChecked():
                self.loopSteps()
            else:
                self.step_timer.stop()

    def loopSteps(self):
        self.playSteps()
        self.step_timer.start()

    def playSteps(self):
        # TODO 锁住仪表盘
        steps= self.step_size
        for i in range(0, steps):
            clock.step()
        self.announces['playSteps'](steps)
        self.updateStatusBar()


    @pyqtSlot(QAction)
    def viewToolBarTriggered(self, action):
        if action is self.ui.action_node:
            self.ui.view_net.showNodes()
        elif action is self.ui.action_stores:
            self.ui.view_net.showName()
        elif action is self.ui.action_hits:
            self.ui.view_net.showHitRatio()

        elif action is self.ui.action_edge:
            self.ui.view_net.showEdges()
        elif action is self.ui.action_transfer:
            self.ui.view_net.showTransfer()
        elif action is self.ui.action_rate:
            self.ui.view_net.showRate()

    @showCall
    def newNodeInfoDialog(self, node_name):  # TODO 已经打开的,不再新建, 改为闪烁
        icn_node= ICNNetHelper.node(self.graph, node_name)
        dialog= NodeInfoDialog(self, icn_node, self.logger)
        dialog.install(self.announces, self.api)
        dialog.show()
        dialog.refresh()  # ???

    def newEdgeInfoDialog(self, src, dst):  # TODO 已经打开的,不再新建, 改为闪烁
        icn_edge= ICNNetHelper.edge(self.graph, src, dst)  # 正向边
        dialog= EdgeInfoDialog(self, icn_edge, self.logger)
        dialog.install(self.announces, self.api)
        dialog.show()
        dialog.refresh()

    def updateStatusBar(self):
        self.statusBar().showMessage( f'steps:{clock.time()}' )
