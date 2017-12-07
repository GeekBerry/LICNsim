import numpy
from module import ModuleBase


class LossMonitor(ModuleBase):
    def __init__(self, lam=0.69 / 1000, alpha=10 / 1000):
        """
        因为 exp(-0.69) 约等于 0.5, lam= 0.69/1000 意味着距离为 1000 时, 非丢包率约为0.5
        alpha=10 / 1000 意味着距离为 1000 时, 延迟为 10 step
        :param lam: 丢包模型负指数函数lam值
        :param alpha: 延迟模型系数
        """
        self.lam = lam
        self.alpha = alpha

    def setup(self, sim):
        sim.announces['playSteps'].append(self.playSteps)
        self.api = sim.api

    def playSteps(self, steps):
        self.graph = self.api['Sim.graph']()

        for edge_id in self.graph.edges():
            distance = self.getDistance(*edge_id)
            loss = self.getLossRata(distance)
            delay = int(self.getDelay(distance))

            icn_edge = self.api['Sim.edge'](edge_id)
            icn_edge.delay = delay
            icn_edge.loss = loss

    def getDelay(self, distance: float):
        return distance * self.alpha

    def getLossRata(self, distance: float):
        return 1 - numpy.exp(-distance * self.lam)

    def getDistance(self, src_id, dst_id):
        src_node = self.api['Sim.node'](src_id)
        dst_node = self.api['Sim.node'](dst_id)

        src_pos = numpy.array(src_node.pos)
        dst_pos = numpy.array(dst_node.pos)
        return numpy.linalg.norm(src_pos - dst_pos)

