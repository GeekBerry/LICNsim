from core import DataBaseTable, clock
from module import ModuleBase
from itertools import count


class LogModule(ModuleBase):
    """
    监听通告，并写入结构化日志表
    提供查询功能
    """
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

        sim.loadNodeAnnounce('csHit', self.csHit)
        sim.loadNodeAnnounce('csMiss', self.csMiss)
        sim.loadNodeAnnounce('loopPacket', self.loopPacket)
        sim.loadNodeAnnounce('overflow', self.overflow)

        sim.loadEdgeAnnounce('send', self.send)
        sim.loadEdgeAnnounce('transfer', self.transfer)
        sim.loadEdgeAnnounce('loss', self.loss)
        sim.loadEdgeAnnounce('arrive', self.arrive)
        # TODO hit, miss, overflow, ...

    def csStore(self, node_id, packet):
        self.db_table[next(self.index_iter)] = {
            'time': clock.time, 'node_id': node_id, 'action': 'store',
            'name': str(packet.name), 'packet_type': packet.type, 'size': packet.size, 'nonce': packet.nonce}

    def csEvict(self, node_id, packet):
        self.db_table[next(self.index_iter)] = {
            'time': clock.time, 'node_id': node_id, 'action': 'evict',
            'name': str(packet.name), 'packet_type': packet.type, 'size': packet.size, 'nonce': packet.nonce}

    def csHit(self, node_id, packet):
        # print(clock.time, node_id, 'csHit', packet)
        pass

    def csMiss(self, node_id, packet):
        # print(clock.time, node_id, 'csMiss', packet)
        pass

    def inPacket(self, node_id, face_id, packet):
        self.db_table[next(self.index_iter)] = {
            'time': clock.time, 'node_id': node_id, 'action': 'in', 'face_id': face_id,
            'name': str(packet.name), 'packet_type': packet.type, 'size': packet.size, 'nonce': packet.nonce}

    def outPacket(self, node_id, face_id, packet):
        self.db_table[next(self.index_iter)] = {
            'time': clock.time, 'node_id': node_id, 'action': 'out', 'face_id': face_id,
            'name': str(packet.name), 'packet_type': packet.type, 'size': packet.size, 'nonce': packet.nonce}

    def loopPacket(self, node_id, face_id, packet):
        # print(clock.time, node_id, 'loopPacket', face_id, packet)
        pass

    def overflow(self, node_id, face_id, packet):
        # print(clock.time, node_id, 'overflow', face_id, packet)
        pass

    # -------------------------------------------------------------------------
    def send(self, edge_id, packet):
        # print(clock.time, edge_id, 'send', packet)
        pass

    def transfer(self, edge_id, packet):
        # print(clock.time, edge_id, 'transfer', packet)
        pass

    def loss(self, edge_id, packet):
        # print(clock.time, edge_id, 'loss', packet)
        pass

    def arrive(self, edge_id, packet):
        # print(clock.time, edge_id, 'arrive', packet)
        pass
