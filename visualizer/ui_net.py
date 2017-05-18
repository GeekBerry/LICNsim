#!/usr/bin/python3
#coding=utf-8

from PyQt5.QtCore import QPointF, qrand

import networkx
from debug import showCall
#=======================================================================================================================
class UINetHelper:
    @staticmethod
    def setup(graph, NodeFactory, ChannelFactory):
        if not isinstance(graph, networkx.DiGraph):
            raise TypeError

        # 构建Node
        for nodename in graph:
            node= NodeFactory(nodename)
            graph.node[nodename]['ui']= node
        # 构建Edge
        for src,dst in graph.edges():
            graph[src][dst]['ui']= ChannelFactory(src,dst)

    @staticmethod
    def nodeItems(graph):
        for nodename in graph:
            yield nodename, graph.node[nodename]['ui']

    @staticmethod
    def node(graph, nodename):
        return graph.node[nodename]['ui']

    @staticmethod
    def nodes(graph):
        for nodename in graph:
            yield graph.node[nodename]['ui']

    @staticmethod
    def edgeItems(graph):
        for src,dst in graph.edges():
            yield (src,dst), graph[src][dst]['ui']

    @staticmethod
    def edge(graph, src, dst):
        return graph[src][dst]['ui']

    @staticmethod
    def edges(graph):
        for src, dst in graph.edges():
            yield graph[src][dst]['ui']
    #-------------------------------------------------------------------------------------------------------------------
    @classmethod
    def layout(cls, graph, times, edge_length):
        if len(graph) > 1000:  # 节点数量太多, 不进行布局
            return

        ratio= edge_length*edge_length  # XXX ratio为此值时, 点之间距离大致为length
        for i in range(0, times):
            for node_name in graph:
                cls.calculateForces(graph, node_name, ratio)

    @classmethod
    def calculateForces(cls, graph, node_name, ratio):  # 计算一个节点受力
        force = QPointF(0.0, 0.0)
        weight = len(graph[node_name])  # 邻居数量

        node_pos = cls.node(graph, node_name).pos()
        for other_name in graph.nodes():
            other_pos = cls.node(graph, other_name).pos()
            vec= other_pos - node_pos
            vls= vec.x()*vec.x() + vec.y()*vec.y()

            if 0 < vls < 4*ratio:  # vec.length() 小于 4*ratio才计算斥力; '4'来自于经验
                force -= (vec/vls) * ratio  # 空间中节点间为排斥力

            if other_name in graph[node_name]:
                force += vec/weight  # 连接的节点间为吸引力

        cls.node(graph, node_name).setPos(node_pos + force * 0.4)  # force系数不能为1, 否则无法收敛; 0.4来自于经验,不会变化太快





