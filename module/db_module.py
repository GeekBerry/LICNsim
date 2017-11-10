from core import DataBaseTable, clock, Packet
from module import MoudleBase
from itertools import count


class DBMoudle(MoudleBase):
    def __init__(self):
        self.db_table = DataBaseTable().create('index', time=None, node_id=None, action=None, face_id=None, packet=None)
        self.db_table.createIndexs('time', 'node_id', 'action', 'face_id', 'packet')
        self.index_iter= count()

    def setup(self, sim):
        super().setup(sim)
        sim.api['DBMoudle.getFields'] = self.db_table.getFields
        sim.api['DBMoudle.query']= self.db_table.query
        sim.loadNodeAnnounce('csStore', self.csStore)
        sim.loadNodeAnnounce('csEvict', self.csEvict)
        sim.loadNodeAnnounce('inPacket', self.inPacket)
        sim.loadNodeAnnounce('outPacket', self.outPacket)

    def csStore(self, node_id, packet):
        self.db_table[ next(self.index_iter) ] = \
            {'time':clock.time(), 'node_id':node_id, 'action':'store', 'packet':packet}

    def csEvict(self, node_id, packet):
        self.db_table[ next(self.index_iter) ] = \
            {'time':clock.time(), 'node_id':node_id, 'action':'evict', 'packet':packet}

    def inPacket(self, node_id, face_id, packet):
        self.db_table[ next(self.index_iter) ] = \
            {'time':clock.time(), 'node_id':node_id, 'action':'in', 'face_id':face_id, 'packet':packet}

    def outPacket(self, node_id, face_id, packet):
        self.db_table[ next(self.index_iter) ] = \
            {'time':clock.time(), 'node_id':node_id, 'action':'out', 'face_id':face_id, 'packet':packet}
