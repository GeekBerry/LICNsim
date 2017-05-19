#!/usr/bin/python3
#coding=utf-8

from debug import showCall

from random import randint

from core import clock, AnnounceTable, CallTable
from core.icn_net import ICNNetHelper

from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtWidgets import QMainWindow, QAction

from visualizer.plugin import *
from visualizer.common import SpinBox
from visualizer.net_scene import NetScene
from visualizer.node_info_dialog import NodeInfoDialog
from visualizer.edge_info_dialog import EdgeInfoDialog


#=======================================================================================================================
class MainWindow(QMainWindow):
    @showCall
    def __init__(self, graph, monitor, logger=None):
        self.docks= {Qt.LeftDockWidgetArea:[], Qt.RightDockWidgetArea:[], Qt.TopDockWidgetArea:[], Qt.BottomDockWidgetArea:[]}
        super().__init__()

        from visualizer.ui.ui_main_window import Ui_main_window
        self.ui= Ui_main_window()
        self.ui.setupUi(self)

        self.install( AnnounceTable(), CallTable() )

        if logger is not None:
            logger.addAnnounceTable('MainWindow', self.announces)

        self.graph= graph
        self.monitor= monitor
        self.logger= logger

        self.scene= NetScene(self.graph)  # NetScene
        self.scene.install(self.announces, self.api)

        self.ui.view_net.setScene(self.scene)  # FIXME 由按钮进行scene管理和设置
        self.ui.view_net.install(self.announces, self.api)

        # ---------------------------------------------------------------------
        self.addPlugin(PlayerPlugin)
        self.addPlugin(PainterPlugin)
        self.addPlugin(ButtomWidgetPlugin)
        self.updateStatusBar()

    def install(self, announces, api):
        api['Main::showNodeInfo']= self.newNodeInfoDialog
        api['Main::showEdgeInfo']= self.newEdgeInfoDialog
        api['MainWindow::setLabelNetNode']= self.ui.label_net_node.setText  # 代理label_net实现install
        api['MainWindow::setLabelNetEdge']= self.ui.label_net_edge.setText  # 代理label_net实现install

        announces['playSteps'].append( self.updateStatusBar )

        self.announces= announces
        self.api= api

    @showCall
    def addPlugin(self, PluginFactory):
        PluginFactory(self).setup(self)

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

    def updateStatusBar(self, *unuse_args):
        self.statusBar().showMessage( f'steps:{clock.time()}' )

    def addDockWidget(self, dock_widget_area, dock_widget, orientation=None):  # 使得同一个方向的Dock合并在一起
        if orientation is None:
            super().addDockWidget(dock_widget_area, dock_widget)
        else:
            super().addDockWidget(dock_widget_area, dock_widget, orientation)

        for area, links in self.docks.items():
            if area == dock_widget_area:
                if links:
                    self.tabifyDockWidget(links[-1], dock_widget)
                links.append(dock_widget)
                break


