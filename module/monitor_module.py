from core import clock, NameTable, Packet
from collections import defaultdict
from module import ModuleBase


class MonitorModule(ModuleBase):
    """
    提供对名字、节点、边的实时数据监控
    """
    def __init__(self):
        self.name_monitor= NameMonitor()
        self.node_monitor= NodeMonitor()
        self.edge_monitor= EdgeMonitor()

    def setup(self, sim):
        self.name_monitor.setup(sim)
        self.node_monitor.setup(sim)
        self.edge_monitor.setup(sim)


# ======================================================================================================================
class NameMonitor(ModuleBase):
    """ 状态转换图
            |EMPTY  |PENGIND|STORED
    --------|-------|-------|-------
    EMPTY   |       |ask    |store
    PENDING |respond|       |store
    STORED  |evict  |       |
    """

    class Record:  # 一个名字下的记录
        def __init__(self):
            self.store = set()  # set(node_id, ...)
            self.pending = set()  # set(node_id, ...)
            self.trans_i = set()  # set(edge_id, ...)  传输兴趣包的边
            self.trans_d = set()  # set(edge_id, ...)  传输数据包的边

    def __init__(self):
        self.name_table = NameTable(default_factory=self.Record)

    def setup(self, sim):
        sim.loadNodeAnnounce('ask', self._askEvent)
        sim.loadNodeAnnounce('respond', self._respondEvent)
        sim.loadNodeAnnounce('csStore', self._storeEvent)
        sim.loadNodeAnnounce('csEvict', self._evictEvent)

        sim.loadEdgeAnnounce('send', self._sendEvent)
        sim.loadEdgeAnnounce('loss', self._finishEvent)
        sim.loadEdgeAnnounce('arrive', self._finishEvent)

        sim.api['Monitor.getNameTable'] = lambda: self.name_table

    def _askEvent(self, node_id, packet):
        record = self.name_table[packet.name]
        if (node_id not in record.store) and (node_id not in record.pending):
            record.pending.add(node_id)

    def _respondEvent(self, node_id, packet):
        record = self.name_table[packet.name]
        record.pending.discard(node_id)

    def _storeEvent(self, node_id, packet):
        record = self.name_table[packet.name]
        record.pending.discard(node_id)
        record.store.add(node_id)

    def _evictEvent(self, node_id, packet):
        record = self.name_table[packet.name]
        record.store.discard(node_id)

    # -------------------------------------------------------------------------
    def _sendEvent(self, edge_id, packet):
        record = self.name_table[packet.name]
        if packet.type is Packet.INTEREST:
            record.trans_i.add(edge_id)
        elif packet.type is Packet.DATA:
            record.trans_d.add(edge_id)
        else:
            pass

    def _finishEvent(self, edge_id, packet):
        record = self.name_table[packet.name]
        if packet.type is Packet.INTEREST:
            record.trans_i.discard(edge_id)
        elif packet.type == Packet.DATA:
            record.trans_d.discard(edge_id)
        else:
            pass


# ----------------------------------------------------------------------------------------------------------------------
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
                occupy = self.forward_size / (clock.time * self.forward_rate)  # XXX 不能应对rate变化的情况
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
        sim.api['Monitor.getNodeTable'] = lambda: self.node_table
        self.getNodeRate = lambda node_id: sim.node(node_id).api['Face.getRate']()

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


# ----------------------------------------------------------------------------------------------------------------------
class EdgeMonitor(ModuleBase):
    class Record:
        def __init__(self):
            self.send_rate = 0
            self.send_size = 0

        def sendOccupy(self):
            try:
                occupy = self.send_size / (self.send_rate * clock.time)  # XXX 不能应对rate变化的情况
            except ZeroDivisionError:
                return 0.0
            else:
                return min(occupy, 1.0)  # 由于send_size统计全部已发送尺寸, 因此计算出occupy有可能大于1.0

    def __init__(self):
        self.edge_table = defaultdict(self.Record)

    def setup(self, sim):
        sim.loadEdgeAnnounce('send', self._sendEvent)
        sim.api['Monitor.getEdgeTable'] = lambda: self.edge_table
        self.getEdgeRate = lambda edge_id: sim.edge(edge_id).rate

    def _sendEvent(self, edge_id, packet):
        record = self.edge_table[edge_id]
        record.send_rate = self.getEdgeRate(edge_id)  # 有必要每次做更新吗
        record.send_size += packet.size
