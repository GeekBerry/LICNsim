from module import MoudleBase
from algorithm.graph_algo import graphNearestPath


class StoreTrackMoudle(MoudleBase):
    def __init__(self, track_name):
        self.track_name= track_name
        self.node_set= set()

    def setup(self, sim):
        super().setup(sim)
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
        return graphNearestPath(self.sim.graph, node_id, self.node_set)








