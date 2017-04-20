#!/usr/bin/python3
#coding=utf-8


from core.clock import clock
from core.data_structure import defaultdict
from core.database import DataBaseTable
from core.icn_net import ICNNetHelper
# from core.packet import Packet
from constants import INF, TransferState

class Monitor:  # TODO 持久化
    def __init__(self, graph):
        ICNNetHelper.loadNodeAnnounce(graph, 'csStore', self._store)
        ICNNetHelper.loadNodeAnnounce(graph, 'csEvict', self._evict)
        ICNNetHelper.loadNodeAnnounce(graph, 'csHit', self._hit)
        ICNNetHelper.loadNodeAnnounce(graph, 'csMiss', self._miss)

        ICNNetHelper.loadNodeAnnounce(graph, 'inPacket', self._inPacket)
        ICNNetHelper.loadNodeAnnounce(graph, 'outPacket', self._outPacket)
        ICNNetHelper.loadNodeAnnounce(graph, 'ask', self._ask)
        ICNNetHelper.loadNodeAnnounce(graph, 'respond', self._respond)

        ICNNetHelper.loadChannelAnnounce(graph, 'begin', self._begin)
        ICNNetHelper.loadChannelAnnounce(graph, 'finish', self._finish)
        ICNNetHelper.loadChannelAnnounce(graph, 'loss', self._loss)
        ICNNetHelper.loadChannelAnnounce(graph, 'full', self._full)
        #---------------------------------------------------------------------------------------------------------------
        self.contents= defaultdict(set)  # {Name:set(NodeName), ...}
        self.packets= defaultdict(lambda:defaultdict(set))  # {Name:{type:{nonce, ...}, ...}, ...}

        # packet_name:Name包名, time:int时间  -> asking:set(NodeName), arriving :set(NodeName),  storing:set(NodeName), evicting :set(NodeName)
        self.packet_t= DataBaseTable().create('packet_name', 'time', asking=set(), arriving=set(), storing=set(), evicting=set())

        # node_name:节点名, time:int时间 -> store:int存储量, evict:int驱逐量, hit:int内容命中量, miss:int内容缺失量, recv:int接收包量, send:int发送包量
        self.node_t= DataBaseTable().create('node_name', 'time', store=0, evict=0, hit=0, miss=0, recv=0, send=0)

        # src:NodeName(源节点名), dst:NodeName(宿节点名), order:int信道处理序号 -> packet_head:PacketHead, begin:int开始时间, end:int结束时间, state:int
        self.transfer_t= DataBaseTable().create('src', 'dst', 'order', packet_head=None, begin=INF, end=INF, state= TransferState.UNSEND)
        self.transfer_t.create_index('packet_head', 'begin', 'end')

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

    def _ask(self, nodename, packet):
        self.packet_t.access( packet.name, clock.time() ).asking.add(nodename)

    def _respond(self, nodename, packet):
        self.packet_t.access( packet.name, clock.time() ).arriving.add(nodename)

    def _full(self, src, dst, order, packet):
        self.transfer_t.access(src, dst, order, packet_head= packet.head(), state=TransferState.DROP)

    def _begin(self, src, dst, order, packet):
        self.packets[packet.name][packet.type].add(packet.nonce)
        self.transfer_t.access(src, dst, order, packet_head= packet.head(), begin=clock.time(), state=TransferState.SENDING)

    def _finish(self, src, dst, order, packet):
        self.transfer_t.access(src, dst, order, packet_head= packet.head(), end=clock.time(), state=TransferState.ARRIVED)

    def _loss(self, src, dst, order, packet):
        self.transfer_t.access(src, dst, order, packet_head= packet.head(), end=clock.time(), state=TransferState.LOSS)

