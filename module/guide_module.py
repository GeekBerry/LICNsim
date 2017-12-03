from collections import defaultdict

from algorithm.graph_algo import graphNearestPath
from module import MoudleBase


class GuideMoudle(MoudleBase):
    """
    该模块效率低下, 仅适合小规模网络或调试使用
    """
    def __init__(self):
        self.table= defaultdict(set)  # {name:set(node_id), ...}
        pass

    def setup(self, sim):
        self.graph= sim.graph
        sim.loadNodeAnnounce('csStore', self._storeEvent)
        sim.loadNodeAnnounce('csEvict', self._evictEvent)
        sim.setNodeAPI('getNextNode', self.getNextNode)

    def _storeEvent(self, node_id, packet):
        self.table[packet.name].add(node_id)

    def _evictEvent(self, node_id, packet):
        self.table[packet.name].discard(node_id)
        if len(self.table[packet.name]) == 0:
            del self.table[packet.name]

    def getNextNode(self, node_id, packet):
        """
        根据节点和兴趣包,给出通往数据包的下一跳节点
        :param node_id: 节点ID
        :param packet: 兴趣包
        :return: 下一跳节点ID
        """
        path= graphNearestPath(self.graph, node_id, self.table[packet.name])
        if (path is None) or len(path)<=1:  # 不存在这样的路径 or 自身就是目标节点
            return None
        else:
            return path[1]  # 返回路径中的下一跳节点