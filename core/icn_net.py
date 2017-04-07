#!/usr/bin/python3
#coding=utf-8

from core.data_structure import Bind
#=======================================================================================================================
class ICNNet:
    def __init__(self, graph, NodeType, ChannelType):
        self.graph= graph

        for nodename in self.graph:  # 构造节点
            node= NodeType()
            self.graph.node[nodename]['icn']= node

        # 构造信道, 要先建立所有节点再建立Channel
        for src,dst in self.graph.edges():
            if type( self.graph[dst][src] ) != ChannelType:  # 反向没有
                src_dst_channel= self.graph[src][dst]['icn']= ChannelType()
                dst_src_channel= self.graph[dst][src]['icn']= ChannelType()
                self.graph.node[src]['icn'].api['Face::create']( dst, dst_src_channel, src_dst_channel )
                self.graph.node[dst]['icn'].api['Face::create']( src, src_dst_channel, dst_src_channel )

    def install(self, announces, api)->None:
        """
        将所有子节点的所有Announce包装上nodename后发往announces
        :param announces:
        :param api:
        :return:
        """
        for nodename in self.graph:
            node= self.graph.node[nodename]['icn']
            for name, publish in node.announces.items():  # 监听节点所有操作
                publish.append( Bind(announces[name], nodename) )

        for src,dst in self.graph.edges():
            channel= self.graph[src][dst]['icn']
            channel.append( Bind(announces['transfer'], src, dst) )

        api['ICNNet::storeAPI']= self.storeAPI

    def storeAPI(self, api_name, function)->None:
        """
        将节点 function 绑定到节点的 api 中, 即:
        node[nodename].api[api_name]( *_args ) <= function( nodename, *_args )
        :param api_name: 节点中的api名称
        :param function: def(nodename, *_args)
        """
        for nodename in self.graph:
            self.graph.node[nodename]['icn'].api[api_name]= Bind(function, nodename)

    def nodes(self):
        for nodename in self.graph:
            yield self.graph.node[nodename]['icn']

    def node(self, nodename):
        return self.graph.node[nodename]['icn']


#=======================================================================================================================
from core.clock import clock
from core.data_structure import Timer
class AskGenerator:
    def __init__(self, icn_net, num_func, pos_func, packet, delta):
        """
        :param num_func: def(int)->int 请求量生成函数,
        :param pos_func: def(int)->[nodename,...] 位置生成函数
        """
        self.icn_net= icn_net
        self.num_func= num_func
        self.pos_func= pos_func
        self.packet= packet
        self.delta= delta
        self.timer= Timer(self._pulse)  # FIXME

    def start(self):
        self.timer.timing(0)

    def _pulse(self):
        nodenum= self.num_func( clock.time() )
        nodenames= self.pos_func(nodenum)
        for nodename in nodenames:
            self.icn_net.node(nodename).api['APP::ask']( self.packet.fission() )
        self.timer.timing(self.delta)

    def end(self):
        self.timer.cancel()
