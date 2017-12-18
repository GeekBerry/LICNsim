import numpy
from module import ModuleBase

from debug import showCall


class LossMonitor(ModuleBase):
    def setup(self, sim):
        sim.announces['playSteps'].append(self.playSteps)
        self.api = sim.api

    def playSteps(self, steps):
        self.graph = self.api['Sim.graph']()

        for edge_id in self.graph.edges():
            icn_edge = self.api['Sim.edge'](edge_id)

            if icn_edge.channel_type == 'wireless':  # 对无线信道进行变化
                distance = self.getEuclideanDistance(*edge_id)
                icn_edge.delay = self.getDelay(distance, speed= 10)  # 单位：1距离/step FIXME speed 不要写死
                icn_edge.loss = self.getLossRata(distance, half_life= 1000)  # 单位 step FIXME half_life 不要写死
            elif icn_edge.channel_type == 'wired':  # 对有线信道的变化
                distance = self.getManhattanDistance(*edge_id)
                icn_edge.delay = self.getDelay(distance, speed= 100)  # 单位： 1距离/step FIXME speed 不要写死
                icn_edge.loss = self.getLossRata(distance, half_life= 10000)  # 单位 step FIXME half_life 不要写死

    def getDelay(self, distance, speed)->int:
        return int(distance / speed)

    def getLossRata(self, distance, half_life):
        return 1 - numpy.exp(- 0.69 * distance / half_life)  # exp(-0.69) 约等于 0.5

    def getManhattanDistance(self, src_id, dst_id):  # 获得曼哈顿距离
        src_node = self.api['Sim.node'](src_id)
        dst_node = self.api['Sim.node'](dst_id)
        src_pos = numpy.array(src_node.pos)
        dst_pos = numpy.array(dst_node.pos)
        return numpy.sum(numpy.abs(src_pos - dst_pos))

    def getEuclideanDistance(self, src_id, dst_id):  # 获得欧式距离
        src_node = self.api['Sim.node'](src_id)
        dst_node = self.api['Sim.node'](dst_id)
        src_pos = numpy.array(src_node.pos)
        dst_pos = numpy.array(dst_node.pos)
        return numpy.linalg.norm(src_pos - dst_pos)
