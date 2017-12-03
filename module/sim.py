import networkx
from core import CallTable, AnnounceTable


class Simulator:
    ICN_FIELD= 'icn'

    def __init__(self):
        self.graph = networkx.DiGraph()
        self.modules= {}
        self.api= CallTable()
        self.announces= AnnounceTable()

        self.api['Sim.graph']= lambda: self.graph
        self.api['Sim.node']= self.node
        self.api['Sim.edge'] = self.edge
        self.api['Sim.nodes']= self.nodes
        self.api['Sim.edges']= self.edges

    def install(self, module_key, module):
        module.setup(self)
        self.modules[module_key]= module

    # -------------------------------------------------------------------------
    def node(self, node_id):
        return self.graph.node[node_id][self.ICN_FIELD]

    def edge(self, edge_id):
        src_id, dst_id= edge_id
        return self.graph[src_id][dst_id][self.ICN_FIELD]

    def nodes(self):
        return self.graph.nodes()

    def edges(self):
        return self.graph.edges()

    # -------------------------------------------------------------------------
    def addICNNode(self, node_id, icn_node):
        assert node_id not in self.graph
        self.graph.add_node(node_id)
        self.graph.node[node_id][self.ICN_FIELD] = icn_node
        self.announces['addICNNode'](node_id)

    def addICNEdge(self, src_id, dst_id, icn_edge):
        assert (src_id,dst_id) not in self.edges()

        self.graph.add_edge(src_id, dst_id)
        self.graph[src_id][dst_id][self.ICN_FIELD] = icn_edge

        self.node(src_id).api['Face.setOutChannel'](dst_id, icn_edge)
        self.node(dst_id).api['Face.setInChannel'](src_id, icn_edge)

        self.announces['addICNEdge']( (src_id, dst_id,) )

    # -------------------------------------------------------------------------
    def createGraph(self, graph, NodeType, ChannelType):
        for node_id in graph:
            self.createNode(node_id, NodeType)
            for neibor_id in graph[node_id]:
                self.createNode(neibor_id, NodeType)
                self.createEdge(node_id, neibor_id, ChannelType)
                self.createEdge(neibor_id, node_id, ChannelType)

    def createNode(self, node_id, NodeType)->bool:
        if node_id not in self.nodes():
            icn_node = NodeType()  # XXX 是否需要 NodeType(node_id)
            self.addICNNode(node_id, icn_node)
            return True
        else:
            return False

    def createEdge(self, src_id, dst_id, ChannelType)->bool:
        if (src_id, dst_id) not in self.edges():
            icn_edge = ChannelType()  # XXX 是否需要 ChannelType(src_id, dst_id)
            self.addICNEdge(src_id, dst_id, icn_edge)
            return True
        else:
            return False

