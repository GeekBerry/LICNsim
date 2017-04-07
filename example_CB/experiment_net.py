#!/usr/bin/python3
#coding=utf-8


from core.clock import clock
from core.icn_net import ICNNet, AskGenerator
from core.common import graphNearestPath
from core.data_base import MonitorDB
#-----------------------------------------------------------------------------------------------------------------------
class ExperimentMonitorDB(MonitorDB):
    def __init__(self, graph):
        self.graph= graph
        super().__init__()
        self.packet_t.add_field('dist', default=[])
        self.packet_t.add_field('delay', default=[])

    def install(self, announces, api):
        super().install(announces, api)
        api['ICNNet::storeAPI']('Net::getPath', self.getPath)

    def _ask(self, nodename, packet, distance):
        super()._ask(nodename, packet)
        self.packet_t.access(packet.name, clock.time()).dist.append(distance)

    def _respond(self, nodename, packet, asktime):
        super()._respond(nodename, packet)
        self.packet_t.access( packet.name, clock.time() ).delay.append( clock.time() - asktime )

    def getPath(self, nodename, packet):  # 储存位置服务提供者  FIXME 要不要分离这个功能
        return graphNearestPath(self.graph, nodename, self.contents[packet.name])

#-----------------------------------------------------------------------------------------------------------------------
import math
import numpy
from core.common import GridPosLogic, graphHoops, GridPosLogicSmallGrid
from core.filer import FilerPlugin
class UniformityPlugin(FilerPlugin):
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
                if self.packet_name in self.graph.node[node_name]['icn'].cs.table:
                    self.poslogic.insert(node_name)
            return [ -101*math.log( numpy.var(self.poslogic.vector), 2) ]
        else:
            return ['Unknow']


