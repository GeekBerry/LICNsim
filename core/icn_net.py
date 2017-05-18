#!/usr/bin/python3
#coding=utf-8

import networkx
from core.data_structure import Bind
#=======================================================================================================================
class ICNNetHelper:
    def __init__(self):
        raise RuntimeError('不要实例化ICNNet')

    @staticmethod
    def setup(graph, NodeFactory, ChannelFactory):
        if not isinstance(graph, networkx.DiGraph):
            raise TypeError

        for nodename in graph:  # 构造节点
            node= NodeFactory(nodename)
            graph.node[nodename]['icn']= node

        # 构造信道, 要先建立所有节点再建立Channel
        for src,dst in graph.edges():
            channel= ChannelFactory(src, dst)
            graph.node[src]['icn'].api['Face::setOutChannel'](dst, channel)
            graph.node[dst]['icn'].api['Face::setInChannel'](src, channel)
            graph[src][dst]['icn']= channel

    @staticmethod
    def loadChannelAnnounce(graph, anno_name, function):
        for src,dst in graph.edges():
            graph[src][dst]['icn'].announces[anno_name].append( Bind(function, src, dst) )

    @staticmethod
    def loadNodeAnnounce(graph, anno_name, function):
        """
        node[node_name].announces[anno_name].append( Bind(function, node_name) )
        :param graph:
        :param anno_name:str 节点中的announce名称, 不存在也能执行
        :param function:def(nodename, *args)
        :return:None
        """
        for node_name in graph:
            graph.node[node_name]['icn'].announces[anno_name].append(Bind(function, node_name))

    @staticmethod
    def storeAPI(graph, api_name, function):
        """
        将节点 function 绑定到节点的 api 中, 即:
        node[nodename].api[api_name]( *_args ) <= function( nodename, *_args )
        :param graph:
        :param api_name:str 节点中的api名称
        :param function:def(nodename, *_args)
        :return:None
        """
        for nodename in graph:
            graph.node[nodename]['icn'].api[api_name]= Bind(function, nodename)

    @staticmethod
    def nodeItems(graph):
        for nodename in graph:
            yield nodename, graph.node[nodename]['icn']

    @staticmethod
    def node(graph, nodename):
        return graph.node[nodename]['icn']

    @staticmethod
    def nodes(graph):
        for nodename in graph:
            yield graph.node[nodename]['icn']

    @staticmethod
    def edgeItems(graph):
        for src,dst in graph.edges():
            yield (src,dst), graph[src][dst]['icn']

    @staticmethod
    def edges(graph):
        for src,dst in graph.edges():
            yield graph[src][dst]['icn']

    @staticmethod
    def edge(graph, src, dst):
        return graph[src][dst]['icn']


#=======================================================================================================================
from core.clock import clock
from core.data_structure import Timer
class AskGenerator:
    def __init__(self, graph, num_func, pos_func, packet, delta):
        """
        :param num_func: def(int)->int 请求量生成函数,
        :param pos_func: def(int)->[nodename,...] 位置生成函数
        """
        self.graph= graph
        self.num_func= num_func
        self.pos_func= pos_func
        self.packet= packet
        self.delta= delta
        self.timer= Timer(self._pulse)  # FIXME

    def start(self, delay):
        self.timer.timing(delay)

    def _pulse(self):
        nodenum= self.num_func( clock.time() )
        nodenames= self.pos_func(nodenum)
        for nodename in nodenames:
            ICNNetHelper.node(self.graph, nodename).api['APP::ask'](self.packet.fission())
        self.timer.timing(self.delta)

    def end(self):
        self.timer.cancel()


class StoreGenerator:  # TODO
    pass
