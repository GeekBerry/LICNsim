from collections import defaultdict

from core import clock
from module import MoudleBase


class NodeMonitor(MoudleBase):
    class Record:
        forward_rate = None

        def __init__(self):
            self.hit = 0
            self.miss = 0
            # self.store = 0
            # self.evict = 0
            self.in_packet = 0
            # self.out_packet = 0

        def forwardOccupy(self):
            if self.forward_rate is None:
                return 0.0
            if self.forward_rate == 0.0:
                return 1.0
            if clock.time() == 0:
                return 0.0

            occupy = self.in_packet / (clock.time() * self.forward_rate)
            return min(occupy, 1.0)

        def hitRatio(self):
            try:
                return self.hit / (self.hit + self.miss)
            except ZeroDivisionError:
                return 0.0

    def __init__(self):
        self.node_table = defaultdict(self.Record)

    def setup(self, sim):
        self.sim = sim
        sim.loadNodeAnnounce('csHit', self._hitEvent)
        sim.loadNodeAnnounce('csMiss', self._missEvent)
        sim.loadNodeAnnounce('inPacket', self._inPacketEvent)
        sim.api['NodeMonitor.table'] = lambda: self.node_table

    def _hitEvent(self, node_id, packet):
        record = self.node_table[node_id]
        record.hit += 1

    def _missEvent(self, node_id, packet):
        record = self.node_table[node_id]
        record.miss += 1

    def _inPacketEvent(self, node_id, face_id, packet):
        record = self.node_table[node_id]
        record.in_packet += 1  # 单位: 个包

        if record.forward_rate is None:
            record.forward_rate = self.sim.node(node_id).api['Forward.getRate']()


class EdgeMonitor(MoudleBase):
    class Record:
        send_rate = None

        def __init__(self):
            self.send_size = 0

        def sendOccupy(self):
            if self.send_rate is None:
                return 0.0
            if self.send_rate == 0.0:
                return 1.0
            if clock.time() == 0:
                return 0.0
            occupy = self.send_size / (self.send_rate * clock.time())
            return min(occupy, 1.0)  # 由于send_size统计全部已发送尺寸, 因此计算出occupy有可能大于1.0

    def __init__(self):
        self.edge_table = defaultdict(self.Record)

    def setup(self, sim):
        self.sim = sim
        sim.loadEdgeAnnounce('send', self._sendEvent)
        sim.api['EdgeMonitor.table'] = lambda: self.edge_table

    def _sendEvent(self, edge_id, packet):
        record = self.edge_table[edge_id]
        record.send_size += packet.size

        if record.send_rate is None:
            record.send_rate = self.sim.edge(edge_id).rate
