import itertools

import networkx

from common import Unit


class TopologyModule(Unit):
    def __init__(self):
        self.graph= networkx.DiGraph()
        self.node_id_iter= itertools.count(start=0, step=1)

    def install(self, announces, api):
        super().install(announces, api)
        self.api['Topo.graph']= lambda :self.graph
        self.api['Topo.nodeIds']= lambda :self.graph.nodes()
        self.api['Topo.edgeIds']= lambda :self.graph.edges()
        self.api['Topo.neiborTable']= self.neiborTable

        self.api['Topo.addNode']= self.addNode
        self.api['Topo.addEdge']= self.addEdge
        self.api['Topo.addSubGraph']= self.addSubGraph

    def neiborTable(self):  # XXX networks 的 graph 定义正好符合 neibor_table 的定义
        return self.graph

    def addNode(self):
        index= next(self.node_id_iter)
        assert index not in self.graph
        self.graph.add_node(index)
        return index

    def addEdge(self, src_id, dst_id):
        if src_id not in self.graph:
            raise KeyError(f'{src_id} not int graph')

        if dst_id not in self.graph:
            raise KeyError(f'{dst_id} not int graph')

        egde_list= []  # [edge_id, ...]

        if not self.graph.has_edge(src_id, dst_id):
            self.graph.add_edge(src_id, dst_id)
            egde_list.append( (src_id, dst_id) )

        if not self.graph.has_edge(dst_id, src_id):
            self.graph.add_edge(dst_id, src_id)
            egde_list.append( (dst_id, src_id) )

        return egde_list

    def addSubGraph(self, sub_graph):
        """
        添加一个子图
        :param sub_graph:networkx.Graph 要附加的子图
        :return: iterable(node_ids, ...), [edge_ids, ...]
        """
        node_id_map= {}  # {sub_graph.NodeName:node_id}
        egde_list= []  # [edge_id, ...]

        # 添加节点
        for node_name in sub_graph.nodes():
            index= next(self.node_id_iter)
            self.graph.add_node(index)
            node_id_map[node_name]= index

        # 添加边
        for src_name, dst_name in sub_graph.edges():
            src_id= node_id_map[src_name]
            dst_id= node_id_map[dst_name]
            egde_list.extend( self.addEdge(src_id, dst_id) )

        return node_id_map.values(), egde_list


