#!/usr/bin/python3
#coding=utf-8

from PyQt5.QtCore import QPointF, qrand
from PyQt5.QtWidgets import QGraphicsScene

from core.common import showCall

from visualizer.node_item import NodeItem
from visualizer.edge_item import EdgeItem, getEdgePair
#=======================================================================================================================
class UINet(QGraphicsScene):
    EDGE_LEN= 80  # 默认边长度
    NODE_SIZE= 40  # 默认Node大小

    def __init__(self, graph):
        super().__init__()
        self.graph= graph

        area_size= self.EDGE_LEN * len(graph)**0.5  # 来自方形网平均宽度
        # 构建Node
        for nodename in self.graph:
            node= NodeItem(nodename)
            node.setPos( qrand()%area_size, qrand()%area_size )
            node.setSize( self.NODE_SIZE )
            node.call_backs['ItemPositionHasChanged']= self._nodeMoved
            node.call_backs['mouseDoubleClickEvent']= self._nodeMouseDoubleClickEvent
            self.addItem(node)
            self.graph.node[nodename]['ui']= node
        # 构建Edge
        for src,dst in self.graph.edges():
            if 'ui' in self.graph[dst][src]:  # 反向已有, 不重复建立
                continue
            edge= EdgeItem( (src,dst,) )
            edge.adjust( self.graph.node[src]['ui'].pos(), self.graph.node[dst]['ui'].pos() )
            edge.call_backs['mouseDoubleClickEvent']= self._edgeMouseDoubleClickEvent
            self.addItem(edge)
            self.graph[src][dst]['ui'], self.graph[dst][src]['ui']= getEdgePair(edge)

        self.debug_init()  # DEBUG

    @showCall
    def debug_init(self):
        #---------------------------------------------------------------------------------------------------------------
        # DEBUG NodeItem
        for nodename, node in self.items():
            node.setName( str(nodename) )
            # node.setAbstract('0123456789\n0123456789')
        # DEBUG EdgeItem
        # for edge in self.edges():
        #     edge.setText( str(edge.getArrow()) )

    @showCall
    def install(self, announces, api):
        self.api= api  # FIXME

    #-------------------------------------------------------------------------------------------------------------------
    def items(self):
        for nodename in self.graph:
            yield nodename, self.graph.node[nodename]['ui']

    def nodes(self):
        for nodename in self.graph:
            yield self.graph.node[nodename]['ui']

    def node(self, nodename):
        return self.graph.node[nodename]['ui']

    def edges(self):
        for src,dst in self.graph.edges():
            yield self.graph[dst][src]['ui']

    def edge(self, src, dst):
        return self.graph[src][dst]['ui']
    #-------------------------------------------------------------------------------------------------------------------
    def graphLayout(self, times):
        if len(self.graph) > 1000:  # 节点数量太多, 不进行布局
            return

        ratio= self.EDGE_LEN * self.EDGE_LEN  # XXX ratio为此值时, 点之间距离大致为length
        for i in range(0, times):
            for node_name in self.graph:
                self._calculateForces(node_name, ratio)

        self.adaptive()

    def _calculateForces(self, node_name, ratio):  # 计算一个节点受力
        force= QPointF(0.0, 0.0)
        weight= len(self.graph[node_name])

        node_pos= self.graph.node[node_name]['ui'].pos()
        for other_name in self.graph.nodes():
            other_pos= self.graph.node[other_name]['ui'].pos()
            vec= other_pos - node_pos
            vls= vec.x()*vec.x() + vec.y()*vec.y()

            if 0 < vls < (2*self.EDGE_LEN) * (2*self.EDGE_LEN):  # vec.length() 小于 2*self.EDGE_LEN 才计算斥力; 2来自于经验
                force -= (vec/vls) * ratio  # 空间中节点间为排斥力

            if other_name in self.graph[node_name]:
                force += vec/weight  # 连接的节点间为吸引力

        self.graph.node[node_name]['ui'].setPos(node_pos + force * 0.4)  # force系数不能为1, 否则无法收敛; 0.4来自于经验,不会变化太快

    def adaptive(self):
        self.setSceneRect( self.itemsBoundingRect() )
        self.update()
    #-------------------------------------------------------------------------------------------------------------------
    def _nodeMoved(self, src):
        src_pos= self.graph.node[src]['ui'].pos()
        for dst in self.graph[src]:
            dst_pos= self.graph.node[dst]['ui'].pos()
            self.graph[src][dst]['ui'].adjust(src_pos, dst_pos)
            self.graph[dst][src]['ui'].adjust(dst_pos, src_pos)

    @showCall
    def _nodeMouseDoubleClickEvent(self, node_name):
        self.api['Main::showNodeInfo'](node_name)

    @showCall
    def _edgeMouseDoubleClickEvent(self, edge_name):
        # TODO
        pass


