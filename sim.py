from core.data_structure import AnnounceTable, CallTable

import networkx
from debug import showCall


class Simulator:
    def __init__(self):
        self.graph= networkx.DiGraph()

        self.api= CallTable()
        self.announces= AnnounceTable()
        self.module_table= {}
        # install
        self.api['Sim.getGraph']= lambda: self.graph

    def install(self, module_name, module):
        module.install(self.announces, self.api)
        self.module_table[module_name]= module

    def uninstall(self, module_name):
        module= self.module_table[module_name]
        module.uninstall(self.announces, self.api)
        del self.module_table[module_name]


class Module:
    def __init__(self):
        self.announces= None
        self.api= None

    def install(self, announces, api):
        self.announces= announces
        self.api= api
        pass

    def uninstall(self, announces, api):
        # self.announces= None
        # self.api= None
        pass


# ======================================================================================================================
import itertools


class TopologyModule(Module):
    def __init__(self):
        super().__init__()
        self.node_id_iter= itertools.count(start=0, step=1)

    def install(self, announces, api):
        super().install(announces, api)
        self.api['Topo::addSubGraph']= self.addSubGraph

    @showCall
    def addSubGraph(self, sub_graph):
        """
        添加一个子图
        :param sub_graph:networkx.Graph 要附加的子图
        :return: iterable(node_ids, ...), [edge_ids, ...]
        """
        node_id_map= {}  # {sub_graph.NodeName:node_id}
        egde_list= []  # [edge_id, ...]

        di_graph= self.api['Sim.getGraph']()
        assert isinstance(di_graph, networkx.DiGraph)  # DEBUG

        # 添加节点
        for node_name in sub_graph.nodes():
            index= next(self.node_id_iter)
            di_graph.add_node(index)
            node_id_map[node_name]= index

        # 添加边
        for src_name, dst_name in sub_graph.edges():
            src_id= node_id_map[src_name]
            dst_id= node_id_map[dst_name]
            # 正向边
            di_graph.add_edge(src_id, dst_id)
            egde_list.append( (src_id, dst_id,) )
            # 反向边
            di_graph.add_edge(dst_id, src_id)
            di_graph.add_edge(dst_id, src_id)

        return node_id_map.values(), egde_list


# ======================================================================================================================
class ICNNetModule(Module):
    def __init__(self):
        super().__init__()
        pass

    def install(self, announces, api):
        super().install(announces, api)
        api['ICNNet.addNet']= self.addNet
        api['ICNNet.nodeItems']= self.nodeItems
        api['ICNNet.edgeItems']= self.edgeItems

    def nodeItems(self):
        di_graph= self.api['Sim.getGraph']()
        assert isinstance(di_graph, networkx.DiGraph)  # DEBUG

        for node_id in di_graph:
            yield node_id, di_graph.node[node_id]

    def edgeItems(self):
        di_graph= self.api['Sim.getGraph']()
        assert isinstance(di_graph, networkx.DiGraph)  # DEBUG

        for src,dst in di_graph.edges():
            yield (src,dst), di_graph[src][dst]

    def addNet(self, top_graph, NodeType, ChannelType):
        node_ids, edge_ids= self.api['Topo::addSubGraph'](top_graph)

        di_graph= self.api['Sim.getGraph']()
        assert isinstance(di_graph, networkx.DiGraph)  # DEBUG

        # 先建立所有 Node
        for node_id in node_ids:
            icn_node= NodeType(node_id)
            di_graph.node[node_id]= icn_node
            self.announces['addICNNode'](node_id, icn_node)

        # 再建立 Channel
        for src_id, dst_id in edge_ids:
            icn_channel= ChannelType(src_id, dst_id)
            di_graph.node[src_id].api['Face::setOutChannel'](dst_id, icn_channel)  # src 节点通往 dst 的信道 Channel(src -> dst)
            di_graph.node[dst_id].api['Face::setInChannel'](src_id, icn_channel)  # dst 接收 src 的信道为 Channel(src -> dst)
            di_graph[src_id][dst_id]= icn_channel
            self.announces['addICNChannel'](src_id, dst_id, icn_channel)


# ======================================================================================================================
from collections import defaultdict
from core.data_structure import Bind


class HubModule(Module):
    """
    将网络中每个 Node 或 channel 的指定 Announce 绑定上节点或信道的id, 发送到 sim 的 announces 上
    在监听到网络中有 addICNNode 和 addICNChannel 时, 自动为新增 Node 和 Channel 添加绑定

    >>> api['Hub.loadNodeAnnounce']('inPacket', print)  # Node(10).announces['inPacket'](faceid, packet) => print(10, faceid, packet)
    >>> api['Hub.loadChannelAnnounce']('begin', print) # Channel(10, 15).announces['begin'](order, packet) => print(10, 15, order, packet)
    """
    def __init__(self):
        super().__init__()
        self.node_anno_table= defaultdict(set) # {AnnounceName:set(function, ...), ...}
        self.channel_anno_table= defaultdict(set) # {AnnounceName:set(function, ...), ...}

    def install(self, announces, api):
        super().install(announces, api)
        announces['addICNNode'].append(self._addICNNodeEvent)
        announces['addICNChannel'].append(self._addICNChannelEvent)

        api['Hub.loadNodeAnnounce']= self.loadNodeAnnounce
        api['Hub.loadChannelAnnounce']= self.loadChannelAnnounce

    def loadNodeAnnounce(self, anno_name, function):
        node_items= self.api['ICNNet.nodeItems']()
        for node_id, icn_node in node_items:
            icn_node.announces[anno_name].pushHead( Bind(function, node_id) )
        self.node_anno_table[anno_name].add(function)  # 记录追踪过的AnnounceName 和对应 function

    def loadChannelAnnounce(self, anno_name, function):
        edge_items= self.api['ICNNet.edgeItems']()
        for (src_id, dst_id), icn_channel in edge_items:
            icn_channel.announces[anno_name].pushHead( Bind(function, src_id, dst_id) )
        self.channel_anno_table[anno_name].add(function)   # 记录追踪过的AnnounceName 和对应 function

    def _addICNNodeEvent(self, node_id, icn_node):
        for anno_name, functions in self.node_anno_table.items():
            for function in functions:
                icn_node.announces[anno_name].pushHead( Bind(function, node_id) )

    def _addICNChannelEvent(self, src_id, dst_id, icn_channel):
        for anno_name, functions in self.channel_anno_table.items():
            for function in functions:
                icn_channel.announces[anno_name].pushHead( Bind(function, src_id, dst_id) )


# ======================================================================================================================
from core.clock import clock
from core.data_base import DataBaseTable


class DataBaseModule(Module):
    def __init__(self):
        super().__init__()
        self.database= dict()

        # time:int时间, node_id:int节点ID -> store:int存储量, evict:int驱逐量, hit:int内容命中量, miss:int内容缺失量, recv:int接收包量, send:int发送包量
        self.database['node_t']= DataBaseTable().create('time', 'node_id', store=0, evict=0, hit=0, miss=0, recv=0, send=0)

    def install(self, announces, api):
        api['Hub.loadNodeAnnounce']('csHit', self._hitEvent)
        api['Hub.loadNodeAnnounce']('csMiss', self._missEvent)

    def _hitEvent(self, node_id, packet):
        self.database['node_t'][clock.time(), node_id]['hit']+= 1

    def _missEvent(self, node_id, packet):
        self.database['node_t'][clock.time(), node_id]['miss']+= 1


# ======================================================================================================================
import sys
from PyQt5.QtWidgets import QApplication
from gui.QuiWidget import MainWindow


class GUIModule(Module):
    def __init__(self):
        super().__init__()

    def install(self, announces, api):
        super().install(announces, api)
        api['Gui::start']= self.start

    def start(self):
        app = QApplication(sys.argv)  # 必须放在MainWindow前

        main_window= MainWindow()
        main_window.install(self.announces, self.api )
        main_window.show()

        return app.exec_()


# ======================================================================================================================
# if __name__ == '__main__':
#     import random
#     from core.clock import clock
#     from example_normal.main import ip_A, ip_B, dp_A, dp_B
#     from example_normal.node import TestNode
#     from example_normal.main import TestChannel
#
#     sim= Simulator()
#     sim.install( 'topology', TopologyModule() )
#     sim.install( 'icn_net', ICNNetModule() )
#     sim.install( 'monitor', HubModule() )
#     sim.install( 'database', DataBaseModule() )
#
#     sim.api['ICNNet.addNet']( networkx.grid_2d_graph(11, 11), TestNode, TestChannel )
#
#     sim.api['Hub.loadNodeAnnounce']('ask', Bind(print, 'ask') )
#     sim.api['Hub.loadNodeAnnounce']('respond', Bind(print, 'respond') )
#     sim.api['Hub.loadNodeAnnounce']('inPacket', Bind(print, 'inPacket') )
#     sim.api['Hub.loadNodeAnnounce']('outPacket', Bind(print, 'outPacket') )
#
#     sim.graph.node[0].api['CS::store'](dp_A)
#
#     for i in range(1000):
#         if i < 100:
#             node_id= random.randint(0,10)
#             sim.graph.node[node_id].api['APP::ask'](ip_A.fission())
#         clock.step()
#
#     print(sim.module_table['database'].database['node_t'].db_table.records)


if __name__ == '__main__':
    sim= Simulator()
    sim.install( 'topology', TopologyModule() )
    sim.install( 'icn_net', ICNNetModule() )
    sim.install( 'monitor', HubModule() )
    sim.install( 'database', DataBaseModule() )
    sim.install( 'gui', GUIModule() )
    sim.api['Gui::start']()



















