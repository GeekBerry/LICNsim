from core import DataBaseTable, clock, Packet
from module import MoudleBase


class DBMoudle(MoudleBase):
    def __init__(self):
        self.db_table = DataBaseTable().create('time', 'node_id', 'action', 'face_id', 'packet')

    def setup(self, sim):
        super().setup(sim)
        sim.api['DBMoudle.query']= self.db_table.query
        sim.loadNodeAnnounce('csStore', self.csStore)
        sim.loadNodeAnnounce('csEvict', self.csEvict)
        sim.loadNodeAnnounce('inPacket', self.inPacket)
        sim.loadNodeAnnounce('outPacket', self.outPacket)

    def csStore(self, node_id, packet):
        self.db_table[clock.time(), node_id, 'store', None, packet] ={}

    def csEvict(self, node_id, packet):
        self.db_table[clock.time(), node_id, 'evict', None, packet] ={}

    def inPacket(self, node_id, face_id, packet):
        self.db_table[clock.time(), node_id, 'in', face_id, packet] ={}

    def outPacket(self, node_id, face_id, packet):
        self.db_table[clock.time(), node_id, 'out', face_id, packet] ={}


