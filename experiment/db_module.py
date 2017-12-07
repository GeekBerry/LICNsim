from core import DataBaseTable, clock, Packet
from module import ModuleBase


class DBModule(ModuleBase):
    def __init__(self):
        self.db_table = DataBaseTable().create('name', 'time',
                                               store_num=0, evict_num=0,
                                               ask_num=0, respond_num=0,
                                               dist_count=0,
                                               send_i_num=0, send_d_num=0,
                                               )

    def setup(self, sim):
        super().setup(sim)
        sim.loadNodeAnnounce('csStore', self.store)
        sim.loadNodeAnnounce('csEvict', self.evict)

        sim.loadNodeAnnounce('ask', self.ask)
        sim.loadNodeAnnounce('askDistance', self.askDistance)
        sim.loadNodeAnnounce('respond', self.respond)

        sim.loadEdgeAnnounce('send', self.send)

    def store(self, node_id, packet):
        record = self.db_table[packet.name, clock.time()]
        record['store_num'] += 1

    def evict(self, node_id, packet):
        record = self.db_table[packet.name, clock.time()]
        record['evict_num'] += 1

    def askDistance(self, node_id, packet, distance):
        record = self.db_table[packet.name, clock.time()]
        record['dist_count'] += distance

    def ask(self, node_id, packet):
        record = self.db_table[packet.name, clock.time()]
        record['ask_num'] += 1

    def respond(self, node_id, packet):
        record = self.db_table[packet.name, clock.time()]
        record['respond_num'] += 1

    def send(self, edge_id, packet):
        record = self.db_table[packet.name, clock.time()]

        if packet.type is Packet.INTEREST:
            record['send_i_num'] += 1
        elif packet.type is Packet.DATA:
            record['send_d_num'] += 1
        else:
            pass


