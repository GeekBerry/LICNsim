from core import NameTable, Packet
from module import MoudleBase


class NameMonitor(MoudleBase):
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

        sim.api['NameMonitor.table'] = lambda: self.name_table

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
