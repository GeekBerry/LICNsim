from collections import defaultdict

from core import clock
from module import ModuleBase


class NodeMonitor(ModuleBase):
    class Record:
        def __init__(self):
            self.hit = 0
            self.miss = 0
            self.forward_rate = 0
            self.forward_size = 0

        def hitRatio(self):
            try:
                return self.hit / (self.hit + self.miss)
            except ZeroDivisionError:
                return 0.0

        def forwardOccupy(self):
            try:
                occupy= self.forward_size / (clock.time * self.forward_rate)  # XXX 不能应对rate变化的情况
            except ZeroDivisionError:
                return 0.0
            else:
                return min(occupy, 1.0)

    def __init__(self):
        self.node_table = defaultdict(self.Record)

    def setup(self, sim):
        sim.loadNodeAnnounce('csHit', self._hitEvent)
        sim.loadNodeAnnounce('csMiss', self._missEvent)
        sim.loadNodeAnnounce('inPacket', self._inPacketEvent)
        sim.api['NodeMonitor.table'] = lambda: self.node_table
        self.getNodeRate= lambda node_id: sim.node(node_id).api['Forward.getRate']()

    def _hitEvent(self, node_id, packet):
        record = self.node_table[node_id]
        record.hit += 1  # 单位: 个包

    def _missEvent(self, node_id, packet):
        record = self.node_table[node_id]
        record.miss += 1  # 单位: 个包

    def _inPacketEvent(self, node_id, face_id, packet):
        record = self.node_table[node_id]
        record.forward_rate += self.getNodeRate(node_id)  # 有必要每次做更新吗
        record.forward_size += 1  # 单位: 个包



