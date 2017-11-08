from collections import defaultdict

from module import MoudleBase


class NodeMonitor(MoudleBase):
    class Record:
        def __init__(self):
            self.hit = 0
            self.miss = 0
            # self.store = 0
            # self.evict = 0
            # self.in_packet = 0
            # self.out_packet = 0

        @property
        def hit_ratio(self):
            try:
                return self.hit / (self.hit+self.miss)
            except ZeroDivisionError:
                return 0.0

    def __init__(self):
        self.node_table= defaultdict(self.Record)

    def setup(self, sim):
        sim.loadNodeAnnounce('csHit', self._hitEvent)
        sim.loadNodeAnnounce('csMiss', self._missEvent)
        sim.api['NodeMonitor.table']= lambda :self.node_table

    def _hitEvent(self, node_id, packet):
        record= self.node_table[node_id]
        record.hit += 1

    def _missEvent(self, node_id, packet):
        record= self.node_table[node_id]
        record.miss += 1
