#!/usr/bin/python3
#coding=utf-8


from debug import showCall

from random import randint
from PyQt5.QtWidgets import QGraphicsScene
from visualizer.ui_net import UINetHelper


class NetScene(QGraphicsScene):
    AREA_SIZE= 1000
    EDGE_LEN= 80  # 默认边长度
    NODE_SIZE= 0.5  # 默认Node大小
    SPACE_WIDTH= 200

    @showCall
    def __init__(self, graph):
        super().__init__()
        self.graph= graph

        for nodename, ui_node in UINetHelper.nodeItems(self.graph):
            ui_node.call_backs['ItemPositionHasChanged']= self._nodeMoved
            ui_node.call_backs['mouseDoubleClickEvent']= self._nodeMouseDoubleClickEvent
            self.addItem(ui_node)
            ui_node.setPos( randint(0, self.AREA_SIZE), randint(0, self.AREA_SIZE) )
            ui_node.setSize( self.NODE_SIZE )
            ui_node.setText( str(nodename) )

        for (src, dst), ui_edge in UINetHelper.edgeItems(self.graph):
            ui_edge.call_backs['mouseDoubleClickEvent']= self._edgeMouseDoubleClickEvent
            src_node= UINetHelper.node(self.graph, src)
            dst_node= UINetHelper.node(self.graph, dst)
            ui_edge.adjust( src_node.pos(), dst_node.pos() )
            self.addItem(ui_edge)

    def install(self, announces, api):
        self.api= api  # FIXME

    def adaptive(self):
        self.setSceneRect( self.itemsBoundingRect().adjusted(-self.SPACE_WIDTH, -self.SPACE_WIDTH, self.SPACE_WIDTH, self.SPACE_WIDTH) )
        self.update()
    # ------------------------------------------------------------------------------------------------------------------

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
    def _edgeMouseDoubleClickEvent(self, src, dst):
        self.api['Main::showEdgeInfo'](src, dst)

