#!/usr/bin/python3
#coding=utf-8

from debug import showCall

from core import clock, AnnounceTable, CallTable
from core.icn_net import ICNNetHelper

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow
from visualizer.net_scene import NetScene
from visualizer.node_info_dialog import NodeInfoDialog

#=======================================================================================================================
class MainWindow(QMainWindow):
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
        self.api['Main::setLabelNetNode']= self.ui.label_net_node.setText  # 代理label_net实现install
        self.api['Main::setLabelNetEdge']= self.ui.label_net_edge.setText  # 代理label_net实现install

        self.scene= NetScene(self.graph)  # NetScene
        self.scene.install(self.announces, self.api)

        self.ui.view_net.init(self.graph, self.scene, self.monitor)  # NetView
        self.ui.view_net.install(self.announces, self.api)

        self.ui.table_contents.init(self.monitor)  # CSTableWidget
        self.ui.table_contents.install(self.announces, self.api)

        self.ui.tree_packet_head.init(self.monitor) # PacketHeadTreeWidget
        self.ui.tree_packet_head.install(self.announces, self.api)

        self.updateStatusBar()

    @pyqtSlot()
    def playSteps(self):
        steps= 100  # TODO 获取steps
        for i in range(0, steps):
            clock.step()
        self.updateStatusBar()
        self.announces['playSteps'](steps)  # 一定要先step, 再publish

    @pyqtSlot()
    def viewNodes(self):
        self.ui.view_net.showNodes()

    @pyqtSlot()
    def viewName(self):
        self.ui.view_net.showName()

    @pyqtSlot()
    def viewHits(self):
        self.ui.view_net.showHitRatio()

    @pyqtSlot()
    def viewEdges(self):
        self.ui.view_net.showEdges()

    @pyqtSlot()
    def viewRate(self):
        self.ui.view_net.showRate()

    @pyqtSlot()
    def viewTransfer(self):
        self.ui.view_net.showTransfer()

    @showCall
    def newNodeInfoDialog(self, node_name):
        icn_node= ICNNetHelper.node(self.graph, node_name)
        dialog= NodeInfoDialog(self, icn_node, self.logger)  # 如果不以self为parent, 窗口会一闪而过
        dialog.show()

    def updateStatusBar(self):
        self.statusBar().showMessage( f'steps:{clock.time()}' )
