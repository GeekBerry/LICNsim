from core import DataBaseTable, clock, Packet, floor
from module import ModuleBase


class DBModule(ModuleBase):
    def __init__(self, delta: int = 1):
        """
        :param delta: int 分片长, 一个delta内时间将会聚合到一个记录中
        """
        self._delta = delta
        self.db_table = DataBaseTable().create('time', 'name', 'node_id',
                                               ask=0, respond=0,
                                               hit=0, miss=0,
                                               store=0, evict=0,
                                               in_interest=0, in_data=0,
                                               out_interest=0, out_data=0,
                                               )

    def setup(self, sim):
        sim.loadNodeAnnounce('ask', self._askEvent)
        sim.loadNodeAnnounce('respond', self._respondEvent)
        sim.loadNodeAnnounce('csHit', self._hitEvent)
        sim.loadNodeAnnounce('csMiss', self._missEvent)
        sim.loadNodeAnnounce('csStore', self._storeEvent)
        sim.loadNodeAnnounce('csEvict', self._evictEvent)
        sim.loadNodeAnnounce('inPacket', self._inPacketEvent)
        sim.loadNodeAnnounce('outPacket', self._outPacketEvent)

        sim.api['DBModule.getDelta'] = lambda: self._delta
        sim.api['DBModule.getFields'] = self.db_table.getFields
        sim.api['DBModule.query'] = self.db_table.query  # FIXME 有多张表怎么办？

    def timeIndex(self):  # 将当前时间对 delta 向下取“整”
        if self._delta == 1:
            return clock.time
        else:
            return floor(clock.time, self._delta)

    def _askEvent(self, node_id, packet):
        self.db_table[self.timeIndex(), packet.name, node_id]['ask'] += 1

    def _respondEvent(self, node_id, packet):
        self.db_table[self.timeIndex(), packet.name, node_id]['respond'] += 1

    def _hitEvent(self, node_id, packet):
        record = self.db_table[self.timeIndex(), packet.name, node_id]
        record['hit'] += 1

    def _missEvent(self, node_id, packet):
        record = self.db_table[self.timeIndex(), packet.name, node_id]
        record['miss'] += 1

    def _storeEvent(self, node_id, packet):
        record = self.db_table[self.timeIndex(), packet.name, node_id]
        record['store'] += 1

    def _evictEvent(self, node_id, packet):
        record = self.db_table[self.timeIndex(), packet.name, node_id]
        record['evict'] += 1

    def _inPacketEvent(self, node_id, face_id, packet):
        record = self.db_table[self.timeIndex(), packet.name, node_id]
        if packet.type == Packet.INTEREST:
            record['in_interest'] += 1
        elif packet.type == Packet.DATA:
            record['in_data'] += 1

    def _outPacketEvent(self, node_id, face_id, packet):
        record = self.db_table[self.timeIndex(), packet.name, node_id]
        if packet.type == Packet.INTEREST:
            record['out_interest'] += 1
        elif packet.type == Packet.DATA:
            record['out_data'] += 1
