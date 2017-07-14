from collections import defaultdict

from base.core import Bind
from common import Unit


class HubModule(Unit):
    """
    将网络中每个 Node 或 channel 的指定 Announce 绑定上节点或信道的id, 发送到 sim 的 announces 上
    在监听到网络中有 addICNNode 和 addICNChannel 时, 自动为新增 Node 和 Channel 添加绑定

    >>> api['Hub.loadNodeAnnounce']('inPacket', print)  # Node(10).announces['inPacket'](faceid, packet) => print(10, faceid, packet)
    >>> api['Hub.loadChannelAnnounce']('sendStart', print) # Channel(10, 15).announces['sendStart'](packet) => print(10, 15, packet)
    """
    def __init__(self):
        self.node_anno_table= defaultdict(set) # {AnnounceName:set(function, ...), ...}
        self.channel_anno_table= defaultdict(set) # {AnnounceName:set(function, ...), ...}

    def install(self, announces, api):
        super().install(announces, api)
        announces['addICNNode'].append(self._addICNNodeEvent)
        announces['addICNChannel'].append(self._addICNChannelEvent)

        api['Hub.loadNodeAnnounce']= self.loadNodeAnnounce
        api['Hub.loadChannelAnnounce']= self.loadChannelAnnounce

    def loadNodeAnnounce(self, anno_name, function):
        node_items= self.api['ICNNet.nodeItems']()
        for node_id, icn_node in node_items:
            icn_node.announces[anno_name].pushHead( Bind(function, node_id) )
        self.node_anno_table[anno_name].add(function)  # 记录追踪过的AnnounceName 和对应 function

    def loadChannelAnnounce(self, anno_name, function):
        edge_items= self.api['ICNNet.edgeItems']()
        for (src_id, dst_id), icn_channel in edge_items:
            icn_channel.announces[anno_name].pushHead( Bind(function, src_id, dst_id) )
        self.channel_anno_table[anno_name].add(function)   # 记录追踪过的AnnounceName 和对应 function

    def _addICNNodeEvent(self, node_id, icn_node):
        for anno_name, functions in self.node_anno_table.items():
            for function in functions:
                icn_node.announces[anno_name].pushHead( Bind(function, node_id) )

    def _addICNChannelEvent(self, src_id, dst_id, icn_channel):
        for anno_name, functions in self.channel_anno_table.items():
            for function in functions:
                icn_channel.announces[anno_name].pushHead( Bind(function, src_id, dst_id) )


