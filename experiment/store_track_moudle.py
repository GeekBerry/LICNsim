from algorithm.graph_algo import graphNearestPath
from module import ModuleBase


class StoreTrackModule(ModuleBase):
    """
    记录某一名字在网络中的缓存情况，并能计算任一节点到最近缓存节点的路径
    """
    def __init__(self, track_name):
        self.track_name= track_name
        self.node_set= set()

    def setup(self, sim):
        self.graph= sim.graph
        sim.loadNodeAnnounce('csStore', self.store)
        sim.loadNodeAnnounce('csEvict', self.evict)
        sim.setNodeAPI('getStorePath', self.getStorePath)

    # -------------------------------------------------------------------------
    def store(self, node_id, packet):
        assert packet.name == self.track_name
        assert node_id not in self.node_set
        self.node_set.add(node_id)

    def evict(self, node_id, packet):
        assert packet.name == self.track_name
        assert node_id in self.node_set
        self.node_set.discard(node_id)

    def getStorePath(self, node_id):
        return graphNearestPath(self.graph, node_id, self.node_set)



