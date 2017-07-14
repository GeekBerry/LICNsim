import random
import numpy
from core import Name, clock
from common import Hardware
from module import *


class Simulator(Hardware):
    def __init__(self):
        super().__init__('')
        self.clients= []
        self.routers= []
        self.servers= []
        self.data_names= []

        self.install('topology', TopologyModule())
        self.install('icn_net', ICNNetModule())
        self.install('hub', HubModule())
        self.install('database', DataBaseModule())
        self.install('monitor', MonitorModule())  # 与 database 不同, 用 monitor 执行实时的, 不需储存的监控行为
        self.install('gui', GUIModule())

    def createAndLinkNode(self, NodeType, EdgeType, dst_id):
        src_id = self.api['ICNNet.createNode'](NodeType)
        self.api['ICNNet.addEdge'](src_id, dst_id, EdgeType)
        return src_id

    def generateData(self, node_id, name, delta):
        icn_node = self.api['ICNNet.getNode'](node_id)
        icn_node.api['Generate.store'](name, delta)

    def startAskData(self, node_id, name):
        icn_node = self.api['ICNNet.getNode'](node_id)
        icn_node.api['Generate.ask'](name)

    def stopAskData(self, node_id):
        icn_node = self.api['ICNNet.getNode'](node_id)
        icn_node.api['Generate.stop']()




    def createRouterNet(self, graph, NodeType, EdgeType):
        routers, edge_ids = self.api['ICNNet.addNet'](graph, NodeType, EdgeType)
        self.routers.extend(routers)

    def createClientNodes(self, count, NodeType, EdgeType):
        for i in range(count):
            node_id= self.api['ICNNet.createNode'](NodeType)
            router_id= random.choice(self.routers)
            self.api['ICNNet.addEdge'](node_id, router_id, EdgeType)
            self.clients.append(node_id)

    def createServerNodes(self, count, NodeType, EdgeType):
        for i in range(count):
            node_id= self.api['ICNNet.createNode'](NodeType)
            router_id= random.choice(self.routers)
            self.api['ICNNet.addEdge'](node_id, router_id, EdgeType)
            self.servers.append(node_id)

    def startGenerateData(self, delta):
        for type_id, node_id in enumerate(self.servers):
            data_name= Name.fromArgs('multicast', type_id)
            icn_node = self.api['ICNNet.getNode'](node_id)
            icn_node.api['Generate.store']( data_name, delta )
            self.data_names.append(data_name)

    def startGenerateAsk(self, lam, alpha):
        node_num= numpy.random.poisson(lam)
        node_ids= random.sample(self.clients, node_num)

        for node_id in node_ids:
            icn_node = self.api['ICNNet.getNode'](node_id)
            index= numpy.random.zipf(alpha)
            if 0 <= index < len(self.data_names):
                data_name= self.data_names[index]
                icn_node.api['Generate.ask'](data_name, 10_000)

        clock.timing(10_000, self.startGenerateAsk, lam, alpha)
