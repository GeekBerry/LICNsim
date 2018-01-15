from collections import defaultdict
from core import Bind
from module import ModuleBase


class HubModule(ModuleBase):
    def __init__(self):
        """
        安装该模块后，模拟器具有监听网络中节点和信道的新增消息，
        并为节点和行到绑定经过 loadNodeAnnounce， loadEdgeAnnounce，setNodeAPI 等函数加载的 Announce 或 API
        """
        self.node_anno= defaultdict(set)  # {anno_name:{func,...}, ...}
        self.edge_anno= defaultdict(set)  # {anno_name:{func,...}, ...}
        self.node_api= defaultdict(set)  # {api_name:[func,...], ...}

    def setup(self, sim):
        self.sim= sim
        sim.announces['addICNNode'].append(self._bindNodeAnnounceApi)
        sim.announces['addICNEdge'].append(self._bindEdgeAnnounceApi)
        sim.loadNodeAnnounce= self.loadNodeAnnounce
        sim.loadEdgeAnnounce= self.loadEdgeAnnounce
        sim.setNodeAPI= self.setNodeAPI

    def loadNodeAnnounce(self, anno_name, func):
        self.node_anno[anno_name].add(func)
        # XXX 是否要加载现有节点？
        # for node_id in self.nodes():
        #     node= self.node(node_id)
        #     node.announces[anno_name].prepend(Bind(func, node_id))

    def loadEdgeAnnounce(self, anno_name, func):
        self.edge_anno[anno_name].add(func)
        # XXX 是否要加载现有节点 ?

    def setNodeAPI(self, api_name, func):
        self.node_api[api_name] = func
        # XXX 是否要加载现有节点 ?

    # -------------------------------------------------------------------------
    def _bindNodeAnnounceApi(self, node_id):
        icn_node= self.sim.node(node_id)
        # 设置 Announce
        for anno_name, funcs in self.node_anno.items():
            for func in funcs:
                icn_node.announces[anno_name].prepend( Bind(func, node_id) )
        # 设置 API
        for api_name, func in self.node_api.items():
            icn_node.api[api_name] = Bind(func, node_id)

    def _bindEdgeAnnounceApi(self, edge_id):
        icn_edge= self.sim.edge(edge_id)
        # 设置 Announce
        for anno_name, funcs in self.edge_anno.items():
            for func in funcs:
                icn_edge.announces[anno_name].prepend( Bind(func, edge_id) )

