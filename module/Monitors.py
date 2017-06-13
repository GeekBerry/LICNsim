
from core.name import NameTree


class NameStateMonitor:
    """ .md
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

        def __repr__(self):
            return str(self.__dict__)

    @classmethod
    def accessRecord(cls, name_node):
        return name_node.table.setdefault( 'state_record', cls.Record())

    # =========================================================================
    def __init__(self, name_tree):
        self.__tree_ref= name_tree

    def install(self, announces, api):
        api['Hub.loadNodeAnnounce']('ask', self._askEvent)
        api['Hub.loadNodeAnnounce']('respond', self._respondEvent)
        api['Hub.loadNodeAnnounce']('csStore', self._storeEvent)
        api['Hub.loadNodeAnnounce']('csEvict', self._evictEvent)

        api['Monitor.getNameStateRecord']= self.getNameStateRecord

    def getNameStateRecord(self, name):
        name_node= self.__tree_ref.access(name)  # TODO 改为查找 NameTree
        return self.accessRecord(name_node)

    # -------------------------------------------------------------------------
    def _askEvent(self, node_id, packet):
        name_node= self.__tree_ref.access(packet.name)
        record= self.accessRecord(name_node)
        if (node_id not in record.store) and (node_id not in record.pending):
            record.pending.add(node_id)

    def _respondEvent(self, node_id, packet):
        name_node= self.__tree_ref.access(packet.name)
        record= self.accessRecord(name_node)
        record.pending.discard(node_id)

    def _storeEvent(self, node_id, packet):
        name_node= self.__tree_ref.access(packet.name)
        record= self.accessRecord(name_node)
        record.pending.discard(node_id)
        record.store.add(node_id)

    def _evictEvent(self, node_id, packet):
        name_node= self.__tree_ref.access(packet.name)
        record= self.accessRecord(name_node)
        record.store.discard(node_id)
