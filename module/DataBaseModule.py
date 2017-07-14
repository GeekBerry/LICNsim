import itertools

from base.core import DataBaseTable
from core import clock
from common import Unit

class DataBaseModule(Unit):
    def __init__(self):
        self.data_base= dict()

        self.data_base['flow_t']= DataBaseTable().create('time', 'p_name', 'p_type', p_num=0, p_size=0)

        self.log_order= itertools.count()
        self.data_base['log_t']= DataBaseTable().create('order', 'time', 'id', 'operate', 'p_head', dst=None)
        self.log_file= open('log.txt', 'w')  # DEBUG

    def install(self, announces, api):
        api['DB.table']= lambda table_name: self.data_base.get(table_name)

        api['Hub.loadNodeAnnounce']('csStore', self._storeEvent)
        api['Hub.loadNodeAnnounce']('csEvict', self._evictEvent)
        api['Hub.loadNodeAnnounce']('csHit',   self._hitEvent)
        api['Hub.loadNodeAnnounce']('csMiss',  self._missEvent)
        api['Hub.loadNodeAnnounce']('csDrop',  self._dropEvent)

        api['Hub.loadNodeAnnounce']('inPacket', self._inPacketEvent)
        api['Hub.loadNodeAnnounce']('outPacket', self._outPacketEvent)

        api['Hub.loadChannelAnnounce']('transferStart', self._transferStartEvent)
        api['Hub.loadChannelAnnounce']('transferLoss', self._transferLossEvent)
        api['Hub.loadChannelAnnounce']('transferEnd', self._transferEndEvent)

    # ------------------------------------------------------------------------------------------------------------------
    def _inPacketEvent(self, node_id, face_id, packet):
        self.data_base['log_t'][next(self.log_order), clock.time(), node_id, 'inPacket', packet.head()]['dst']= face_id

        self.log_file.write(f'{clock.time()}\tNode{node_id}\tinPacket\tFace{face_id}\t{packet.head()}\n')
        self.log_file.flush()
        pass

    def _outPacketEvent(self, node_id, face_id, packet):
        self.data_base['log_t'][next(self.log_order), clock.time(), node_id, 'outPacket', packet.head()]['dst']= face_id

        self.log_file.write(f'{clock.time()}\tNode{node_id}\toutPacket\tFace{face_id}\t{packet.head()}\n')
        self.log_file.flush()
        pass

    def _storeEvent(self, node_id, packet):
        self.data_base['log_t'][next(self.log_order), clock.time(), node_id, 'csStore', packet.head()]= {}
        pass

    def _evictEvent(self, node_id, packet):
        self.data_base['log_t'][next(self.log_order), clock.time(), node_id, 'csEvict', packet.head()]= {}
        pass

    def _hitEvent(self, node_id, packet):
        # self.data_base['node_t'][clock.time(), node_id]['hit']+= 1
        self.data_base['log_t'][next(self.log_order), clock.time(), node_id, 'csHit', packet.head()]= {}
        pass

    def _missEvent(self, node_id, packet):
        # self.data_base['node_t'][clock.time(), node_id]['miss']+= 1
        self.data_base['log_t'][next(self.log_order), clock.time(), node_id, 'csMiss', packet.head()]= {}
        pass

    def _dropEvent(self, node_id, packet):
        self.data_base['log_t'][next(self.log_order), clock.time(), node_id, 'csDrop', packet.head()]= {}
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def _transferStartEvent(self, src_id, dst_id, packet):
        flow_record= self.data_base['flow_t'][clock.time(), packet.name, packet.type]
        flow_record['p_num'] += 1
        flow_record['p_size'] += packet.size

        self.data_base['log_t'][next(self.log_order), clock.time(), (src_id, dst_id), 'transferStart', packet.head()]['dst']= dst_id

    def _transferLossEvent(self, src_id, dst_id, packet):
        self.data_base['log_t'][next(self.log_order), clock.time(), (src_id, dst_id), 'transferLoss', packet.head()]['dst']= dst_id

    def _transferEndEvent(self, src_id, dst_id, packet):
        self.data_base['log_t'][next(self.log_order), clock.time(), (src_id, dst_id), 'transferEnd', packet.head()]['dst']= dst_id

