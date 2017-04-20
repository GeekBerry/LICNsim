#!/usr/bin/python3
#coding=utf-8

from PyQt5.QtWidgets import QGraphicsScene
from debug import showCall
from visualizer.ui_net import UINetHelper

class NetScene(QGraphicsScene):
    EDGE_LEN= 80  # 默认边长度
    NODE_SIZE= 40  # 默认Node大小

    def __init__(self, graph):
        super().__init__()
        self.graph= graph
        UINetHelper.bindToScene(graph, self)

        for nodename, node in UINetHelper.nodeItems(graph):  # DEBUG
            node.setSize( self.NODE_SIZE )
            node.setName( str(nodename) )

    def install(self, announces, api):
        self.api= api  # FIXME

    def adaptive(self):
        self.setSceneRect( self.itemsBoundingRect().adjusted(-100, -100, 100, 100) )
        self.update()
    #-------------------------------------------------------------------------------------------------------------------
    def graphLayout(self, times=1):
        UINetHelper.layout(self.graph, times, self.EDGE_LEN)
        self.adaptive()

    def _nodeMoved(self, src):
        src_pos= UINetHelper.node(self.graph, src).pos()
        for dst in self.graph[src]:
            dst_pos= UINetHelper.node(self.graph, dst).pos()
            UINetHelper.edge(self.graph, src, dst).adjust(src_pos, dst_pos)
            UINetHelper.edge(self.graph, dst, src).adjust(dst_pos, src_pos)

    @showCall
    def _nodeMouseDoubleClickEvent(self, node_name):
        self.api['Main::showNodeInfo'](node_name)

    @showCall
    def _edgeMouseDoubleClickEvent(self, edge_name):
        # TODO
        pass
