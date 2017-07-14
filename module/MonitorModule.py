
from collections import defaultdict

from base.core import NameTree
from common import Unit


class MonitorModule(Unit):
    def __init__(self):
        self.node_table= defaultdict(dict)  # {node_id:{field:value, ...}}

    def install(self, announces, api):
        NameStoreMonitor().install(announces, api)
        NodeHitMonitor(self.node_table).install(announces, api)


# ======================================================================================================================
class NameStoreMonitor:
    """ .md 状态转换图
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

    class StoreNameTree(NameTree):
        def __init__(self, *args):
            super().__init__(*args)
            self.setValue( NameStoreMonitor.Record() )

    # =========================================================================
    def __init__(self):
        self.name_tree= self.StoreNameTree()

    def install(self, announces, api):
        api['Hub.loadNodeAnnounce']('ask', self._askEvent)
        api['Hub.loadNodeAnnounce']('respond', self._respondEvent)
        api['Hub.loadNodeAnnounce']('csStore', self._storeEvent)
        api['Hub.loadNodeAnnounce']('csEvict', self._evictEvent)

        api['Hub.loadChannelAnnounce']('sendStart', self._startEvent)
        api['Hub.loadChannelAnnounce']('sendBreak', self._endEvent)  # sendBreak 视为 End
        api['Hub.loadChannelAnnounce']('transferEnd', self._endEvent)
        api['Hub.loadChannelAnnounce']('transferLoss', self._endEvent)  # Loss 视为 End

        api['NameStoreMonitor.tree']= lambda:self.name_tree  # FIXME 用Tree还是Table ???

    # -------------------------------------------------------------------------
    def _askEvent(self, node_id, packet):
        record= self.name_tree.access(packet.name).getValue()
        if (node_id not in record.store) and (node_id not in record.pending):
            record.pending.add(node_id)

    def _respondEvent(self, node_id, packet):
        record= self.name_tree.access(packet.name).getValue()
        record.pending.discard(node_id)

    def _storeEvent(self, node_id, packet):
        record= self.name_tree.access(packet.name).getValue()
        record.pending.discard(node_id)
        record.store.add(node_id)

    def _evictEvent(self, node_id, packet):
        record= self.name_tree.access(packet.name).getValue()
        record.store.discard(node_id)

    # -------------------------------------------------------------------------
    def _startEvent(self, src_id, dst_id, packet):
        record= self.name_tree.access(packet.name).getValue()
        record.transfer.add((src_id, dst_id))

    def _endEvent(self, src_id, dst_id, packet):
        record= self.name_tree.access(packet.name).getValue()
        record.transfer.discard( (src_id, dst_id) )


# ======================================================================================================================
class NodeHitMonitor:
    RECORD_TYPE= 'HIT_RECORD'

    class Record:
        def __init__(self):
            self.hit= 0
            self.miss= 0

        @property
        def ratio(self):
            count= self.hit + self.miss
            return self.hit/count if count else None

    def __init__(self, node_table):
        self.node_table= node_table  # { node_id:{RECORD_TYPE:Record, ...}, ... }

    def install(self, announces, api):
        api['Hub.loadNodeAnnounce']('csHit', self._hitEvent)
        api['Hub.loadNodeAnnounce']('csMiss', self._missEvent)

        api['Monitor.getNodeHitRecord']= self.accessRecord  # FIXME 这是一个粗暴的方法, 将 Record 的解析交给了使用者, 违背了封装

    def accessRecord(self, node_id):
        return self.node_table[node_id].setdefault( self.RECORD_TYPE, self.Record() )

    # -------------------------------------------------------------------------
    def _hitEvent(self, node_id, packet):
        record= self.accessRecord(node_id)
        record.hit+= 1

    def _missEvent(self, node_id, packet):
        record= self.accessRecord(node_id)
        record.miss+= 1




