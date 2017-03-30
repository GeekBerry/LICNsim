#!/usr/bin/python3
#coding=utf-8

import networkx

from core.data_structure import SheetTable
from core.common import Bind, debug, label
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

    def install(self, announces, api)->None:  # FIXME 是否过于简单除暴
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


#-----------------------------------------------------------------------------------------------------------------------
class MonitorDataBase:# TODO 对于时间的记录, TODO 持久化
    def install(self, announces, api):
        announces['csStore'].append(self._store)
        announces['csEvict'].append(self._evict)
        announces['csHit'].append(self._hit)
        announces['csMiss'].append(self._miss)
        announces['inPacket'].append(self._inPacket)
        announces['outPacket'].append(self._outPacket)
        announces['transfer'].append(self._transfer)

        api['DB::self']= lambda:self

        # 内容表 key:Name内容包名, pend:set(NodeName)等待节点集, content:set(NodeName)存储节点集, store:int存储量, evict:int驱逐量
        self.content_table= SheetTable(pend=set, content=set, store= int, evict=int)

        # 节点表 key:NodeName节点名, store:int存储量, evict:int驱逐量, hit:int内容命中量, miss:int内容缺失量, recv:int接收包量, send:int发送包量
        self.node_table= SheetTable(store=int, evict=int, hit=int, miss=int, recv=int, send=int)

        # 信道表 key:(NodeName, NodeName)源节点名,宿节点名, trans:int传送流量
        self.channel_table= SheetTable(trans=int)

    def _store(self, nodename, packet):
        entry= self.content_table[packet.name]
        entry.content.add(nodename)
        entry.store+= 1

    def _evict(self, nodename, packet):
        entry= self.content_table[packet.name]
        entry.content.discard(nodename)
        entry.evict+= 1

    def _hit(self, nodename, packet):
        self.node_table[nodename].hit+= 1

    def _miss(self, nodename, packet):
        self.node_table[nodename].miss+= 1

    def _inPacket(self, nodename, faceid, packet):
        self.node_table[nodename].recv+= 1

    def _outPacket(self, nodename, faceid, packet):
        self.node_table[nodename].send+= 1

    def _transfer(self, src, dst, packet):
        self.channel_table[src, dst].trans+= packet.size


#-----------------------------------------------------------------------------------------------------------------------

