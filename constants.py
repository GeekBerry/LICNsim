#!/usr/bin/python3
#coding=utf-8
import networkx


INF= 0x7FFFFFFF  # 无穷大 此处用4byte整形最大正数

# transfer_t 包发送状态
class TransferState:
    UNSEND, SENDING, ARRIVED, LOSS, DROP = 0,1,2,3,4
    TYPE_STRING= ['unsend', 'sending', 'arrived', 'loss', 'drop']


import core.policy
POLICY_LIST= list(core.policy.searchPolicyInModule(core.policy))


# ======================================================================================================================
# debug_ip=  core.packet.Packet( core.packet.Name('/DEBUG_PACKET'),   core.packet.Packet.INTEREST, size=1)
# debug_ip1= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/1'), core.packet.Packet.INTEREST, size=1 )
# debug_ip2= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/2'), core.packet.Packet.INTEREST, size=1 )
# debug_dp=  core.packet.Packet( core.packet.Name('/DEBUG_PACKET'),   core.packet.Packet.DATA, size=1 )
# debug_dp1= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/1'), core.packet.Packet.DATA, size=1 )
# debug_dp2= core.packet.Packet( core.packet.Name('/DEBUG_PACKET/2'), core.packet.Packet.DATA, size=1 )


class GraphGrid100X100:
    def __init__(self):
        self.diameter= 100
        self.center= (50,50)
        self.graph= networkx.DiGraph( networkx.grid_2d_graph(self.diameter, self.diameter) )


class GraphGrid11X11:
    def __init__(self):
        self.diameter= 11
        self.center= (5,5)
        self.graph= networkx.DiGraph( networkx.grid_2d_graph(self.diameter, self.diameter) )


class GraphBA50:
    def __init__(self):
        import core.algorithm
        self.center= 0  # FIXME networkx 构建的中心点有数据 BA网络中心点一般在0
        self.graph= networkx.DiGraph( networkx.random_graphs.barabasi_albert_graph(50, 1) )
        self.diameter= core.algorithm.graphApproximateDiameter(self.graph)


class GraphBA10000:
    def __init__(self):
        import core.algorithm
        self.center= 0  # FIXME networkx 构建的中心点有数据 BA网络中心点一般在0
        self.graph= networkx.DiGraph( networkx.random_graphs.barabasi_albert_graph(10000, 1) )
        self.diameter= core.algorithm.graphApproximateDiameter(self.graph)


class GraphTree3X8:
    def __init__(self):
        self.center= 0  # FIXME networkx 构建的中心点有数据 BA网络中心点一般在0
        self.graph= networkx.DiGraph( networkx.balanced_tree(r=3, h=8) )
        self.diameter= 8 * 2  # h*2
