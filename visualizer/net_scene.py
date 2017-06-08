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
            ui_node.call_backs['mousePressEvent']= self._nodeMousePressEvent
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
        self.announces= announces
        # self.api= api  # FIXME

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
        self.announces['NodeDoubleClick'](node_name)

    @showCall
    def _nodeMousePressEvent(self, node_name):
        self.announces['NodeMousePress'](node_name)

    @showCall
    def _edgeMouseDoubleClickEvent(self, src, dst):
        self.announces['EdgeDoubleClick'](src, dst)

    @showCall
    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        if bool( event.pos() ) is False:  # XXX 场景在没有捕捉到Item时, event.pos()为QPointF(), 而非位置
            self.announces['SceneDoubleClick']()

    # def mousePressEvent(self, event):
    #     p= self.mouseGrabberItem()
    #     print(p)
    #
    #
    # @showCall
    # def nodeDBC(self, nodename):
    #     pass
