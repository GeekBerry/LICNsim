from core import DataBaseTable, clock
from module import ModuleBase
from itertools import count


class LogModule(ModuleBase):
    def __init__(self):
        self.db_table = DataBaseTable().create(
            'index', time=None, node_id=None, action=None, face_id=None,
            name=None, packet_type=None, size=None, nonce=None
        )
        self.db_table.createIndexs('time', 'node_id', 'action', 'face_id', 'name', 'nonce')
        self.index_iter = count()

    def setup(self, sim):
        sim.api['LogMoudle.getFields'] = self.db_table.getFields
        sim.api['LogMoudle.query'] = self.db_table.query
        sim.loadNodeAnnounce('csStore', self.csStore)
        sim.loadNodeAnnounce('csEvict', self.csEvict)
        sim.loadNodeAnnounce('inPacket', self.inPacket)
        sim.loadNodeAnnounce('outPacket', self.outPacket)
        # TODO loss, overflow, ...

    def csStore(self, node_id, packet):
        self.db_table[next(self.index_iter)] = {
            'time': clock.time, 'node_id': node_id, 'action': 'store',
            'name': str(packet.name), 'packet_type': packet.type, 'size': packet.size, 'nonce': packet.nonce}

    def csEvict(self, node_id, packet):
        self.db_table[next(self.index_iter)] = {
            'time': clock.time, 'node_id': node_id, 'action': 'evict',
            'name': str(packet.name), 'packet_type': packet.type, 'size': packet.size, 'nonce': packet.nonce}

    def inPacket(self, node_id, face_id, packet):
        self.db_table[next(self.index_iter)] = {
            'time': clock.time, 'node_id': node_id, 'action': 'in', 'face_id': face_id,
            'name': str(packet.name), 'packet_type': packet.type, 'size': packet.size, 'nonce': packet.nonce}

    def outPacket(self, node_id, face_id, packet):
        self.db_table[next(self.index_iter)] = {
            'time': clock.time, 'node_id': node_id, 'action': 'out', 'face_id': face_id,
            'name': str(packet.name), 'packet_type': packet.type, 'size': packet.size, 'nonce': packet.nonce}


