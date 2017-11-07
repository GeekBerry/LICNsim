from module import MoudleBase
from core import NameTable, DefaultDictDecorator


class NameMonitor(MoudleBase):
    """ 状态转换图
            |EMPTY  |PENGIND|STORED
    --------|-------|-------|-------
    EMPTY   |       |ask    |store
    PENDING |respond|       |store
    STORED  |evict  |       |
    """
    class Record:
        def __init__(self):
            self.store= set()  # set(node_id, ...)
            self.pending= set()  # set(node_id, ...)
            self.transfer= set()  # set(edge_id, ...)

        def __repr__(self):
            return str(self.__dict__)

    def __init__(self):
        self.name_table= DefaultDictDecorator(NameTable(), self.Record)

    def setup(self, sim):
        sim.loadNodeAnnounce('ask', self._askEvent)
        sim.loadNodeAnnounce('respond', self._respondEvent)
        sim.loadNodeAnnounce('csStore', self._storeEvent)
        sim.loadNodeAnnounce('csEvict', self._evictEvent)
        sim.api['NameMonitor.table']= lambda :self.name_table

    def _askEvent(self, node_id, packet):
        record= self.name_table[packet.name]
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


from collections import defaultdict


class NodeMonitor(MoudleBase):
    class Record:
        def __init__(self):
            self.hit = 0
            self.miss = 0
            self.store = 0
            self
            self.store= set()  # set(node_id, ...)
            self.pending= set()  # set(node_id, ...)
            self.transfer= set()  # set(edge_id, ...)

        def __repr__(self):
            return str(self.__dict__)

    def setup(self, sim):
        # sim.loadNodeAnnounce('ask', self._askEvent)
        # sim.loadNodeAnnounce('respond', self._respondEvent)
        # sim.loadNodeAnnounce('csStore', self._storeEvent)
        # sim.loadNodeAnnounce('csEvict', self._evictEvent)
        sim.api['NameMonitor.table']= lambda :self.name_table
