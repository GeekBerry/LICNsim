import pandas

from core import DataBaseTable, clock, Packet
from module import ModuleBase


class DBModule(ModuleBase):
    def __init__(self, delta: int):
        """
        :param delta: int 分片长, 一个delta内时间将会聚合到一个记录中
        """
        self.delta = delta
        self.db_table = DataBaseTable().create('time', 'name', 'node_id',
                                               ask=0, respond=0,
                                               hit=0, miss=0,
                                               store=0, evict=0,
                                               in_interest=0, in_data=0,
                                               out_interest=0, out_data=0,
                                               distance=0,  # DEBUG
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

        sim.loadNodeAnnounce('distance', self._distanceEvent)  # DEBUG

        sim.api['DBModule.getFields'] = self.db_table.getFields
        sim.api['DBModule.selectWhere']= self.selectWhere

    def timeIndex(self):  # 将当前时间对 delta 向下取“整”
        return (clock.time // self.delta) * self.delta

    def selectWhere(self, *fields, **where) -> pandas.DataFrame:
        """
        :param fields:
        :param where: {field:condition, ...}
        :return: pandas.DataFrame
        """
        if not fields:
            fields = self.db_table.getFields()
        assert 'time' in fields

        init_data = {'time': range(0, clock.time, self.delta)}
        frame = pandas.DataFrame(data=init_data, columns=fields).set_index('time').fillna(0)
        records = self.db_table.query(**where)

        # 用 records 数据覆盖 fream
        for record in records:
            time = record['time']
            for field in frame.columns:
                if field not in ('name', 'node_id'):
                    frame.loc[time][field] += record[field]

        return frame

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

    def _distanceEvent(self, node_id, packet, distacne):  # DEBUG
        record = self.db_table[self.timeIndex(), packet.name, node_id]
        record['distance'] += distacne

















