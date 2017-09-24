import networkx

from base.unit.face_unit import NetFace
from common import Unit


class ICNNetModule(Unit):
    def install(self, announces, api):
        """

        :param announces:
        :param api:
        :return:
        """
        super().install(announces, api)
        api['ICNNet.nodeItems']= self.nodeItems
        api['ICNNet.edgeItems']= self.edgeItems
        api['ICNNet.getNode']= self.getNode
        api['ICNNet.getEdge']= self.getEdge

        api['ICNNet.createNode']= self.createNode
        api['ICNNet.addEdge']= self.addEdge
        api['ICNNet.addNet']= self.addNet

    def getNode(self, node_id):
        graph= self.api['Topo.graph']()
        return graph.node[node_id]

    def nodeItems(self):
        graph= self.api['Topo.graph']()
        for node_id in graph:
            yield node_id, graph.node[node_id]

    def getEdge(self, src_id, dst_id):
        graph= self.api['Topo.graph']()
        return graph[src_id][dst_id]

    def edgeItems(self):
        graph= self.api['Topo.graph']()
        for src,dst in graph.edges():
            yield (src,dst), graph[src][dst]

    def createNode(self, NodeFactory):
        node_id= self.api['Topo.addNode']()
        graph= self.api['Topo.graph']()
        self._setNodes(graph, [node_id], NodeFactory)
        return node_id

    def addEdge(self, src_id, dst_id, ChannelFactory):
        edge_ids= self.api['Topo.addEdge'](src_id, dst_id)
        graph= self.api['Topo.graph']()
        self._setEdges(graph, edge_ids, ChannelFactory)
        return edge_ids

    def addNet(self, top_graph, NodeFactory, ChannelFactory):
        """
        :param top_graph:
        :param NodeFactory:
        :param ChannelFactory:
        :return: ([int,...], [ （int,int), ...], )  # 节点ID数组，边ID数组
        """
        node_ids, edge_ids= self.api['Topo.addSubGraph'](top_graph)
        graph= self.api['Topo.graph']()
        self._setNodes(graph, node_ids, NodeFactory)  # 先建立所有 Node
        self._setEdges(graph, edge_ids, ChannelFactory)  # 再建立 Channel
        return node_ids, edge_ids

    def _setNodes(self, graph, node_ids, NodeFactory):
        for node_id in node_ids:
            icn_node= NodeFactory(node_id)
            graph.node[node_id]= icn_node
            self.announces['addICNNode'](node_id, icn_node)

    def _setEdges(self, graph, edge_ids, ChannelFactory):
        for src_id, dst_id in edge_ids:
            icn_channel= ChannelFactory(src_id, dst_id)

            src_face= graph.node[src_id].api['Face.access'](dst_id, NetFace)  # FIXME FaceType
            src_face.setOutChannel(icn_channel)  # src 节点通往 dst 的信道 Channel(src -> dst)

            dst_face= graph.node[dst_id].api['Face.access'](src_id, NetFace)  # FIXME FaceType
            dst_face.setInChannel(icn_channel)  # dst 接收 src 的信道为 Channel(src -> dst)

            graph[src_id][dst_id]= icn_channel
            self.announces['addICNChannel'](src_id, dst_id, icn_channel)
