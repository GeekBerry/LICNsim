#!/usr/bin/python3
#coding=utf-8


from core.clock import clock
from core.icn_net import ICNNetHelper, AskGenerator
from core.algorithm import graphNearestPath
from core.monitor import Monitor
#-----------------------------------------------------------------------------------------------------------------------
class ExperimentMonitor(Monitor):
    def __init__(self, graph):  # 要放在ICNNet构建后执行
        super().__init__(graph)
        self.graph= graph
        self.packet_t.add_field('dist', default=[])
        self.packet_t.add_field('delay', default=[])
        ICNNetHelper.storeAPI(self.graph, 'Net::getPath', self.getPath)  # 要放在ICNNet构建后执行

    def _ask(self, nodename, packet, distance):
        super()._ask(nodename, packet)
        self.packet_t.access(packet.name, clock.time()).dist.append(distance)

    def _respond(self, nodename, packet, asktime):
        super()._respond(nodename, packet)
        self.packet_t.access(packet.name, clock.time()).delay.append(clock.time() - asktime)

    def getPath(self, nodename, packet):  # 储存位置服务提供者  FIXME 要不要分离这个功能
        return graphNearestPath(self.graph, nodename, self.contents[packet.name])

#-----------------------------------------------------------------------------------------------------------------------
import math
import numpy
from core.algorithm import graphHoops, graphNearestPath, GridPosLogic, GridPosLogicSmallGrid, GridPosLogic, GridPosLogicSmallGrid
from core.filer import FilerPlugin


class UniformityPlugin(FilerPlugin):
    """
    计算和显示图中节点分布均匀性    
    """
    def __init__(self, graph, center, packet_name):
        self.graph= graph
        self.center= center
        self.packet_name= packet_name

        if isinstance(center, (tuple, list) ):
            self.is_grid= True
            self.poslogic= GridPosLogicSmallGrid(center[0], center[1])
        else:
            self.is_grid= False

    def title(self)->list:
        return ['uniformity']

    def entry(self)->list:
        if self.is_grid:
            self.poslogic.reset()
            for node_name in self.graph:
                if self.packet_name in self.graph.node[node_name]['icn'].units['cs'].table:
                    self.poslogic.insert(node_name)
            return [ -101*math.log( numpy.var(self.poslogic.vector), 2) ]
        else:
            return ['Unknow']


