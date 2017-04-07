#!/usr/bin/python3
#coding=utf-8


from core.clock import clock
from core.data_structure import defaultdict, DataBaseTable
class MonitorDB:  # TODO 持久化
    def __init__(self):
        self.contents= defaultdict(set) # {Name:set(NodeName), ...}

        # packet_name:Name包名, time:int时间  -> asking:set(NodeName), arriving :set(NodeName),  storing:set(NodeName), evicting :set(NodeName)
        self.packet_t= DataBaseTable().create('packet_name', 'time', asking= set(), arriving= set(), storing= set(), evicting= set())

        # node_name:节点名, time:int时间 -> store:int存储量, evict:int驱逐量, hit:int内容命中量, miss:int内容缺失量, recv:int接收包量, send:int发送包量
        self.node_t= DataBaseTable().create('node_name', 'time', store= 0, evict= 0, hit= 0, miss= 0, recv= 0, send= 0)

        # edge_name:(NodeName, NodeName)(源节点名,宿节点名), time:int时间 -> bytes:int传送流量
        self.channel_t= DataBaseTable().create('edge_name', 'time', bytes= 0)

    def install(self, announces, api):
        announces['csStore'].append(self._store)
        announces['csEvict'].append(self._evict)
        announces['csHit'].append(self._hit)
        announces['csMiss'].append(self._miss)
        announces['inPacket'].append(self._inPacket)
        announces['outPacket'].append(self._outPacket)
        announces['transfer'].append(self._transfer)
        announces['ask'].append(self._ask)
        announces['respond'].append(self._respond)

    def _store(self, nodename, packet):
        cur_time= clock.time()
        self.contents[packet.name].add(nodename)
        self.packet_t.access(packet.name, cur_time).storing.add(nodename)
        self.node_t.access(nodename, cur_time).store += 1

    def _evict(self, nodename, packet):
        cur_time= clock.time()
        self.contents[packet.name].discard(nodename)
        self.packet_t.access(packet.name, cur_time).evicting.add(nodename)
        self.node_t.access(nodename, cur_time).evict += 1

    def _hit(self, nodename, packet):
        self.node_t.access( nodename, clock.time() ).hit += 1

    def _miss(self, nodename, packet):
        self.node_t.access( nodename, clock.time() ).miss += 1

    def _inPacket(self, nodename, faceid, packet):
        self.node_t.access( nodename, clock.time() ).recv += 1

    def _outPacket(self, nodename, faceid, packet):
        self.node_t.access( nodename, clock.time() ).send += 1

    def _transfer(self, src, dst, packet):
        self.channel_t.access( (src, dst), clock.time() ).bytes += packet.size

    def _ask(self, nodename, packet):
        self.packet_t.access( packet.name, clock.time() ).asking.add(nodename)

    def _respond(self, nodename, packet):
        self.packet_t.access( packet.name, clock.time() ).arriving.add(nodename)
