import itertools
import networkx


class Simulator:
    ICN_FIELD= 'icn'

    def __init__(self):
        self.graph = networkx.DiGraph()
        self.node_id_iter = itertools.count(start=0, step=1)
        self.modules= {}

    def install(self, module_key, module):
        module.setup(self)
        self.modules[module_key]= module

    # -------------------------------------------------------------------------
    def getNode(self, node_id):
        assert node_id in self.graph
        return self.graph.node[node_id][self.ICN_FIELD]

    def getEdge(self, src_id, dst_id):
        return self.graph[src_id][dst_id][self.ICN_FIELD]

    def nodes(self):
        return iter(self.graph)

    def edges(self):
        return self.graph.edges()

    # -------------------------------------------------------------------------
    def addNode(self, NodeFactory):
        node_id = next(self.node_id_iter)
        assert node_id not in self.graph
        self.graph.add_node(node_id)
        self.graph.node[node_id][self.ICN_FIELD] = NodeFactory(node_id)
        return node_id

    def addEdge(self, src_id, dst_id, ChannelFactory):
        """
        FaceId is NodeId
        :param src_id:
        :param dst_id:
        :param ChannelFactory:
        :return: None
        """
        channel = ChannelFactory(src_id, dst_id)

        self.graph.add_edge(src_id, dst_id)
        self.graph[src_id][dst_id][self.ICN_FIELD] = channel

        self.getNode(src_id).setOutChannel(dst_id, channel)
        self.getNode(dst_id).setInChannel(src_id, channel)

    def addBiEdge(self, src_id, dst_id, ChannelFactory):
        self.addEdge(src_id, dst_id, ChannelFactory)
        self.addEdge(dst_id, src_id, ChannelFactory)

    def addGraph(self, graph, NodeFactory, ChannelFactory):
        """
        :param graph: nexworkx.Graph
        :param NodeFactory:
        :param ChannelFactory:
        :return: node_ids
        """
        id_map = {}  # {graph.node_id: self.graph.node_id}
        # 添加节点
        for old_id in graph.nodes():
            new_id = self.addNode(NodeFactory)
            id_map[old_id] = new_id
        # 添加边
        for src_id, dst_id in graph.edges():
            self.addEdge(id_map[src_id], id_map[dst_id], ChannelFactory)
            self.addEdge(id_map[dst_id], id_map[src_id], ChannelFactory)
        return id_map



from core import Bind, CallTable, AnnounceTable
from collections import defaultdict


class SuperSimulator(Simulator):
    def __init__(self):
        super().__init__()
        self.api= CallTable()
        self.announces= AnnounceTable()

        self.api['Sim.neighbor']= lambda: self.graph
        self.api['Sim.nodes']= self.nodes
        self.api['Sim.edges']= self.edges
        self.api['Sim.getNode']= self.getNode
        self.api['Sim.getEdge'] = self.getEdge

        self.node_anno= defaultdict(set)  # {anno_name:{func,...}, ...}
        self.edge_anno= defaultdict(set)  # {anno_name:{func,...}, ...}
        self.node_api= defaultdict(set)  # {api_name:[func,...], ...}

    def loadNodeAnnounce(self, anno_name, func):
        self.node_anno[anno_name].add(func)
        # XXX 是否要加载现有节点？
        # for node_id in self.nodes():
        #     node= self.getNode(node_id)
        #     node.announces[anno_name].append(Bind(func, node_id))

    def loadEdgeAnnounce(self, anno_name, func):
        self.edge_anno[anno_name].add(func)
        # XXX 是否要加载现有节点？

    def setNodeAPI(self, api_name, func):
        self.node_api[api_name]= func
        # XXX 是否要加载现有节点？

    # -------------------------------------------------------------------------
    def addNode(self, NodeFactory):
        node_id= super().addNode(NodeFactory)
        node= self.getNode(node_id)
        # 设置 Announce
        for anno_name, funcs in self.node_anno.items():
            for func in funcs:
                node.announces[anno_name].append( Bind(func, node_id) )  # XXX prepend ???
        # 设置 API
        for api_name, func in self.node_api.items():
            node.api[api_name] = Bind(func, node_id)

        self.announces['addICNNode'](node_id)
        return node_id

    def addEdge(self, src_id, dst_id, ChannelFactory):
        super().addEdge(src_id, dst_id, ChannelFactory)
        edge= self.getEdge(src_id, dst_id)

        for anno_name, funcs in self.edge_anno.items():
            for func in funcs:
                edge.announces[anno_name].append( Bind(func, src_id, dst_id) )  # XXX prepend ???

        self.announces['addICNChannel'](src_id, dst_id)

