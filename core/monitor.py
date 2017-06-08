#!/usr/bin/python3
#coding=utf-8
from debug import showCall


from collections import defaultdict

from core import Bind, ScaleSeq, AccumScaleSeq
from core.name import NameTree, Name
from core.icn_net import ICNNetHelper
from constants import INF


class NodeStateRecode:
    def __init__(self):
        self.store= set()
        self.pending= set()


class NodeStateMonitor:
    class NodeStateNameTree(NameTree):
        def __init__(self, parent=None, key=None):
            super().__init__(parent, key)
            self.record= NodeStateRecode()

    def __init__(self, graph):
        ICNNetHelper.loadNodeAnnounce(graph, 'csStore', self.storeEvent)
        ICNNetHelper.loadNodeAnnounce(graph, 'csEvict', self.evictEvent)
        ICNNetHelper.loadNodeAnnounce(graph, 'ask',     self.askEvent)
        ICNNetHelper.loadNodeAnnounce(graph, 'respond', self.respondEvent)

        self.state_accum_seq= AccumScaleSeq( 1, INF, self.NodeStateNameTree() )

    def install(self, announces, api):
        api['NodeStateMonitor::getNameStates']= self.getNameStates
        api['NodeStateMonitor::getNameItems']= self.getNameItems

    # -------------------------------------------------------------------------
    def storeEvent(self, node_name, packet):
        record= self.state_accum_seq.current().access(packet.name).record
        record.pending.discard(node_name)
        record.store.add(node_name)

    def evictEvent(self, node_name, packet):
        record= self.state_accum_seq.current().access(packet.name).record
        record.store.discard(node_name)

    def askEvent(self, node_name, packet):
        record= self.state_accum_seq.current().access(packet.name).record
        if (node_name not in record.store) and (node_name not in record.pending):
            record.pending.add(node_name)

    def respondEvent(self, node_name, packet):
        record= self.state_accum_seq.current().access(packet.name).record
        record.pending.discard(node_name)

    # -------------------------------------------------------------------------
    def getNameStates(self, name):
        return self.state_accum_seq.current().access(name).record

    def getNameItems(self):
        for tree_node in self.state_accum_seq.current().access(Name('')):  # 用access(Name('')),获得Name('')前缀, 而非Name(None)前缀
            yield tree_node.name(), tree_node.record


# ======================================================================================================================
class HitRatioRecord:
    DEFAULT_RATIO= 0.0

    def __init__(self):
        self.hit= 0
        self.miss= 0

    @property
    def ratio(self):
        visits= self.hit + self.miss
        if visits:
            return self.hit/visits
        else:
            return self.DEFAULT_RATIO

    def __iadd__(self, other):
        self.hit += other.hit
        self.miss += other.miss
        return self


class NameHitRatioMonitor:
    MAX_SIZE= 100
    SCALE= 100

    class HitRatioNameTree(NameTree):
        def __init__(self, parent=None, key=None):
            super().__init__(parent, key)
            self.record= HitRatioRecord()

    @showCall
    def __init__(self, graph):
        ICNNetHelper.loadNodeAnnounce(graph, 'csHit', self.hitEvent)
        ICNNetHelper.loadNodeAnnounce(graph, 'csMiss', self.missEvent)

        self.name_segm_seq= ScaleSeq( self.MAX_SIZE, self.SCALE, self.HitRatioNameTree() )
        self.name_accum_seq= AccumScaleSeq( self.MAX_SIZE, self.SCALE, self.HitRatioNameTree() )

        self.node_accum_seq= AccumScaleSeq( 1, INF, defaultdict(HitRatioRecord) )  # DEBUG 节点只能查看总命中率

    def install(self, announces, api):
        api['NameHitRatioMonitor::nameSegmZip']= Bind(self._nameSeqZip, self.name_segm_seq)
        api['NameHitRatioMonitor::nameAccumZip']= Bind(self._nameSeqZip, self.name_accum_seq)
        api['NameHitRatioMonitor::nodeRatio']= self.nodeRatio

    def hitEvent(self, node_name, packet):
        self.name_segm_seq.current().access(packet.name).record.hit+= 1
        self.name_accum_seq.current().access(packet.name).record.hit+= 1
        self.node_accum_seq.current()[node_name].hit += 1

    def missEvent(self, node_name, packet):
        self.name_segm_seq.current().access(packet.name).record.miss+= 1
        self.name_accum_seq.current().access(packet.name).record.miss+= 1
        self.node_accum_seq.current()[node_name].miss += 1

    # -------------------------------------------------------------------------
    def nodeRatio(self, node_name):
        return self.node_accum_seq.current()[node_name].ratio

    @showCall
    def _nameSeqZip(self, scale_seq, name, max_num= None):
        if max_num is None:
            indexs= scale_seq.indexs()
        else:
            indexs= scale_seq.indexs()[-max_num:]

        values= [ self._prefixValue(scale_seq[index], name)
            for index in indexs
        ]
        return indexs, values

    def _prefixValue(self, name_tree, prefix):  # 统计所有子节点的命中次数
        record= HitRatioRecord()
        for sub_node in name_tree.access(prefix):
            record += sub_node.record
        return record.ratio


# ======================================================================================================================
class FlowRecord:
    def __init__(self, num=0, size=0):
        self.num= num
        self.size= size

    def __iadd__(self, other):
        self.num += other.num
        self.size += other.size
        return self


class FlowMonitor:
    MAX_SIZE= 100
    SCALE= 100

    class FlowNameTree(NameTree):
        def __init__(self, parent=None, key=None):
            super().__init__(parent, key)
            self.record= FlowRecord()

    @showCall
    def __init__(self, graph):
        ICNNetHelper.loadNodeAnnounce(graph, 'outPacket', self.flowEvent)  # 以 outPacket 作为统计标准

        self.name_segm_seq= ScaleSeq( self.MAX_SIZE, self.SCALE, self.FlowNameTree() )
        self.name_accum_seq= AccumScaleSeq( self.MAX_SIZE, self.SCALE, self.FlowNameTree() )

    def install(self, annouces, api):
        api['FlowMonitor::nameSegmZip']= Bind(self._nameSeqZip, self.name_segm_seq)
        api['FlowMonitor::nameAccumZip']= Bind(self._nameSeqZip, self.name_accum_seq)

    def flowEvent(self, node_name, faceid, packet):
        self.name_segm_seq.current().access(packet.name).record += FlowRecord(1, len(packet))
        self.name_accum_seq.current().access(packet.name).record += FlowRecord(1, len(packet))

    # -------------------------------------------------------------------------
    @showCall
    def _nameSeqZip(self, scale_seq, name, max_num= None):
        if max_num is None:
            indexs= scale_seq.indexs()
        else:
            indexs= scale_seq.indexs()[-max_num:]

        records= [ self._prefixFlow(scale_seq[index], name)
            for index in indexs
        ]
        num_counts= [ record.num for record in records ]
        size_counts= [ record.size for record in records ]

        return indexs, num_counts, size_counts

    def _prefixFlow(self, name_tree, prefix):
        record= FlowRecord()
        for sub_node in name_tree.access(prefix):
            record += sub_node.record
        return record

# ======================================================================================================================


class Monitor:  # TODO 持久化
    def __init__(self, graph):
        # ICNNetHelper.loadNodeAnnounce(graph, 'csStore', self._store)
        # ICNNetHelper.loadNodeAnnounce(graph, 'csEvict', self._evict)
        # ICNNetHelper.loadNodeAnnounce(graph, 'csHit', self._hit)
        # ICNNetHelper.loadNodeAnnounce(graph, 'csMiss', self._miss)
        #
        # ICNNetHelper.loadNodeAnnounce(graph, 'inPacket', self._inPacket)
        # ICNNetHelper.loadNodeAnnounce(graph, 'outPacket', self._outPacket)
        # ICNNetHelper.loadNodeAnnounce(graph, 'ask', self._ask)
        # ICNNetHelper.loadNodeAnnounce(graph, 'respond', self._respond)
        #
        # ICNNetHelper.loadChannelAnnounce(graph, 'queue', self._queue)
        # ICNNetHelper.loadChannelAnnounce(graph, 'full', self._full)
        # ICNNetHelper.loadChannelAnnounce(graph, 'begin', self._begin)
        # ICNNetHelper.loadChannelAnnounce(graph, 'end', self._end)
        # ICNNetHelper.loadChannelAnnounce(graph, 'arrived', self._arrived)
        # ICNNetHelper.loadChannelAnnounce(graph, 'loss', self._loss)

        # --------------------------------------------------------------------------------------------------------------
        self.monitors= []

        self.monitors.append( NodeStateMonitor(graph) )
        self.monitors.append( NameHitRatioMonitor(graph) )
        self.monitors.append( FlowMonitor(graph) )

        # self.packets= defaultdict(lambda:defaultdict(set))  # {Name:{type:{nonce, ...}, ...}, ...}

        # packet_name:Name包名, time:int时间  -> asking:set(NodeName), arriving :set(NodeName),  storing:set(NodeName), evicting :set(NodeName)
        # self.packet_t= DataBaseTable().create('packet_name', 'time', asking=set(), arriving=set(), storing=set(), evicting=set())

        # node_name:节点名, time:int时间 -> store:int存储量, evict:int驱逐量, hit:int内容命中量, miss:int内容缺失量, recv:int接收包量, send:int发送包量
        # self.node_t= DataBaseTable().create('node_name', 'time', store=0, evict=0, hit=0, miss=0, recv=0, send=0)

        # src:NodeName(源节点名), dst:NodeName(宿节点名), order:int信道处理序号 -> packet_head:PacketHead, begin:int开始时间, end:int结束时间, state:int
        # self.transfer_t= DataBaseTable().create('src', 'dst', 'order', packet_head=PacketHead(), begin=INF, end=INF, arrived= INF, state= TransferState.UNSEND)
        # self.transfer_t.create_index('packet_head', 'begin', 'end')

    def install(self, announces, api):
        for monitor in self.monitors:
            monitor.install(announces, api)

        # self.hit_ratio_monitor.install(announces, api)

    # Node
    # def _store(self, nodename, packet):
    #     cur_time= clock.time()
    #     self.packet_t.access(packet.name, cur_time).storing.add(nodename)
    #     self.node_t.access(nodename, cur_time).store += 1
    #
    # def _evict(self, nodename, packet):
    #     cur_time= clock.time()
    #     self.packet_t.access(packet.name, cur_time).evicting.add(nodename)
    #     self.node_t.access(nodename, cur_time).evict += 1
    #
    # def _hit(self, nodename, packet):
    #     self.node_t.access( nodename, clock.time() ).hit += 1
    #
    # def _miss(self, nodename, packet):
    #     self.node_t.access( nodename, clock.time() ).miss += 1
    #
    # def _inPacket(self, nodename, faceid, packet):
    #     self.node_t.access( nodename, clock.time() ).recv += 1
    #
    # def _outPacket(self, nodename, faceid, packet):
    #     self.node_t.access( nodename, clock.time() ).send += 1
    #
    # def _ask(self, nodename, packet):
    #     self.packet_t.access( packet.name, clock.time() ).asking.add(nodename)
    #
    # def _respond(self, nodename, packet):
    #     self.packet_t.access( packet.name, clock.time() ).arriving.add(nodename)
    #
    # # Channel
    # def _queue(self, src, dst, order, packet):
    #     self.transfer_t.access(src, dst, order, packet_head= packet.head(), state=TransferState.UNSEND)
    #
    # def _full(self, src, dst, order, packet):
    #     self.transfer_t.access(src, dst, order, state=TransferState.DROP)
    #
    # def _begin(self, src, dst, order, packet):
    #     self.transfer_t.access(src, dst, order, begin=clock.time(), state=TransferState.SENDING)
    #
    # def _end(self, src, dst, order, packet):
    #     self.transfer_t.access(src, dst, order, end=clock.time() )
    #
    # def _arrived(self, src, dst, order, packet):
    #     self.transfer_t.access(src, dst, order, arrived= clock.time(), state=TransferState.ARRIVED)
    #
    # def _loss(self, src, dst, order, packet):
    #     self.transfer_t.access(src, dst, order, state=TransferState.LOSS)

# ======================================================================================================================



























