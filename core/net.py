#!/usr/bin/python3
#coding=utf-8

import networkx

from core.common import Bind, label
from core.data_structure import SheetTable

#=======================================================================================================================
class ICNNet:
    def __init__(self, graph, NodeType, ChannelType):
        self.graph= graph

        for nodename in self.graph:# 构造节点
            node= NodeType()
            label[node]= "Node"+str(nodename)
            self.graph.node[nodename]['icn']= node

        # 构造信道, 要先建立所有节点再建立Channel
        for src,dst in self.graph.edges():
            if type( self.graph[dst][src] ) != ChannelType:# 反向没有
                src_dst_channel= self.graph[src][dst]['icn']= ChannelType()
                dst_src_channel= self.graph[dst][src]['icn']= ChannelType()
                self.graph.node[src]['icn'].api['Face::create']( dst, src_dst_channel, dst_src_channel )
                self.graph.node[dst]['icn'].api['Face::create']( src, dst_src_channel, src_dst_channel )

    def listen(self, function):
        for src,dst in self.graph.edges():
            self.graph[src][dst]['icn'].append( Bind(function, src, dst) )


    def loadAnnounce(self, anno_name, function, pushhead= False)->None:
        """ 将节点 announces 中的 evict_callback 连接到固定函数, 即:
        node[nodename].annouces[anno_name](*_args) => function( nodename, *_args )
        :param anno_name: 节点中的Announce名
        :param function:def(nodename, *_args) 映射函数名
        :param pushhead:bool 是否将func排在节点的 announces 头部
        """
        for nodename in self.graph:
            announce= self.graph.node[nodename]['icn'].announces[anno_name]
            if pushhead:
                announce.insert(0, Bind(function, nodename))
            else:
                announce.append(Bind(function, nodename))

    def storeAPI(self, api_name, function)->None:
        """
        将节点 function 绑定到节点的 api 中, 即:
        node[nodename].api[api_name]( *_args ) <= function( nodename, *_args )
        :param api_name: 节点中的api名称
        :param function: def(nodename, *_args)
        """
        for nodename in self.graph:
            self.graph.node[nodename]['icn'].api[api_name]= Bind(function, nodename)


    # def nodeNames(self):
    #     return self.graph.nodes()
    #
    def nodes(self):
        for nodename in self.graph:
            yield self.graph.node[nodename]['icn']

    def node(self, nodename):
        return self.graph.node[nodename]['icn']
    #
    # def edgeNames(self):# -> edgename
    #     return self.graph.edges()
    #
    # def edges(self):
    #     for src, dst in self.edgeNames():
    #         yield self.graph[src][dst]['icn']
    #
    # def edge(self, scr, dst):
    #     return self.graph[scr][dst]['icn']

#-----------------------------------------------------------------------------------------------------------------------
class MonitorDataBase:# TODO 对于时间的记录,  TODO 持久化
    def __init__(self, net):
        net.loadAnnounce('csStore', self._store)
        net.loadAnnounce('csEvict', self._evict)
        net.loadAnnounce('csHit',   self._hit)
        net.loadAnnounce('csMiss',  self._miss)
        net.loadAnnounce('inPacket',  self._inPacket)
        net.loadAnnounce('outPacket', self._outPacket)
        net.listen(self._listen)

        self.content_table= SheetTable(pend=set, content=set, store= int, evict=int)
        self.node_table= SheetTable(store=int, evict=int, hit=int, miss=int, recv=int, send=int)
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

    def _listen(self, src, dst, packet):
        self.channel_table[src, dst].trans+= packet.size


#-----------------------------------------------------------------------------------------------------------------------
# class LogMonitor:
#     def __init__(self, ui_net):
#         for node in ui_net.nodes():
#             node.announces['_inInterest'].insert( 0, Bind(self.__print, label[node], '_inInterest') )
#             node.announces['_inData'].insert( 0, Bind(self.__print, label[node], '_inData') )
#             node.announces['outData'].insert( 0, Bind(self.__print, label[node], 'outData') )
#             node.announces['outInterest'].insert( 0, Bind(self.__print, label[node], 'outInterest') )
#
#     def __print(self, nodelable, name, *args):
#         print( clock.life_time(), nodelable, name, *args )
#

