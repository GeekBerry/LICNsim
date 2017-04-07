#!/usr/bin/python3
#coding=utf-8

INF= 0x7FFFFFFF  #无穷大 此处用4byte整形最大正数

import core.packet
debug_ip=  core.packet.Packet( core.packet.Name('/DEBUG_PACKET'),   core.packet.Packet.TYPE.INTEREST )
debug_ip1= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/1'), core.packet.Packet.TYPE.INTEREST )
debug_ip2= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/2'), core.packet.Packet.TYPE.INTEREST )
debug_dp=  core.packet.Packet( core.packet.Name('/DEBUG_PACKET'),   core.packet.Packet.TYPE.DATA )
debug_dp1= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/1'), core.packet.Packet.TYPE.DATA )
debug_dp2= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/2'), core.packet.Packet.TYPE.DATA )


import networkx
import core.common
class GraphGrid100X100:
    def __init__(self):
        self.diameter= 100
        self.center= (50,50)
        self.graph= networkx.grid_2d_graph(self.diameter, self.diameter)


class GraphBA10000:
    def __init__(self):
        self.center= 0  # FIXME networkx 构建的中心点有数据 BA网络中心点一般在0
        self.graph= networkx.random_graphs.barabasi_albert_graph(10000, 1)
        self.diameter= core.common.graphApproximateDiameter(self.graph)


class GraphTree3X8:
    def __init__(self):
        self.center= 0  # FIXME networkx 构建的中心点有数据 BA网络中心点一般在0
        self.graph= networkx.balanced_tree(r=3, h=8)
        self.diameter= 8 * 2  # h*2
