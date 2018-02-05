import numpy
from collections import defaultdict

from algorithm.graph_algo import graphNearestPath, graphHoops
from module import ModuleBase


class StoreTrackModule(ModuleBase):
    """
    该模块效率低下, 仅适合小规模网络或调试使用
    """

    def __init__(self):
        self.table = defaultdict(set)  # {name:set(node_id), ...}

    def setup(self, sim):
        self.graph = sim.graph
        sim.loadNodeAnnounce('csStore', self._storeEvent)
        sim.loadNodeAnnounce('csEvict', self._evictEvent)
        sim.setNodeAPI('Track.getForwardPath', self.getForwardPath)
        sim.setNodeAPI('Track.getForwardFace', self.getForwardFace)
        sim.api['Track.getDisperse']= self.getDisperse

    def _storeEvent(self, node_id, packet):
        self.table[packet.name].add(node_id)

    def _evictEvent(self, node_id, packet):
        self.table[packet.name].discard(node_id)
        if len(self.table[packet.name]) == 0:
            del self.table[packet.name]

    def getDisperse(self, center, name):
        disperse= []
        for hoop in graphHoops(self.graph, center):
            store= len(set(hoop) & self.table[name])
            count= len(hoop)
            disperse.append(store/count)
        return numpy.var(disperse), numpy.mean(disperse)

    def getForwardPath(self, node_id, name):
        path = graphNearestPath(self.graph, node_id, self.table[name])

        if path is None:  # 不存在这样的路径
            return None
        else:  # 返回之后要经过的节点
            return path[1:]

    def getForwardFace(self, node_id, name):
        """
        根据节点和兴趣包,给出通往数据包的下一跳节点
        :param node_id: 节点ID
        :param name: 要查找名字
        :return: 下一跳节点ID
        """
        path = self.getForwardPath(node_id, name)
        if (path is None) or len(path) == 0:  # 不存在这样的路径 or 自身就是目标节点
            return None
        else:
            return path[0]
