import random

from core import Timer, top


class DebugUniformAsker:
    def __init__(self, node_ids, packet, delta, delay=0):
        self.node_ids= node_ids
        self.packet= packet

        self.delta= delta
        self.timer= Timer(self._ask)
        self.timer.timing(delay)

    def install(self, announces, api):
        self.api= api

    def _ask(self):
        print('_ask')
        node_ids= random.sample(self.node_ids, 1)
        self.api['ICNNet.getNode'](node_ids[0]).api['APP.ask']( self.packet.fission() )
        self.timer.timing(self.delta)


if __name__ == '__main__':
    from core import Packet, Name
    ip_A=  Packet(Name.fromStr('A'), Packet.INTEREST, 1)
    ip_A1= Packet(Name.fromStr('A/1'), Packet.INTEREST, 1)
    ip_A2= Packet(Name.fromStr('A/2'), Packet.INTEREST, 1)
    dp_A= Packet(Name.fromStr('A'), Packet.DATA, 500)
    dp_A1= Packet(Name.fromStr('A/1'), Packet.DATA, 500)
    dp_A2= Packet(Name.fromStr('A/2'), Packet.DATA, 500)

    from debug import *
    import networkx
    from example_0.node import RouterNode
    from example_0.sim import Simulator
    from example_0.channel import ChannelType1

    sim= Simulator()
    node_ids, edge_ids= sim.api['ICNNet.addNet'](networkx.grid_2d_graph(5,5), RouterNode, ChannelType1)
    node_ids2, edge_ids2= sim.api['ICNNet.addNet'](networkx.grid_2d_graph(5,5), RouterNode, ChannelType1)
    sim.api['ICNNet.addEdge']( top(node_ids), top(node_ids2), ChannelType1 )

    # ------------------------------------------------
    sim.api['ICNNet.getNode'](0).api['CS.store'](dp_A1)
    sim.api['ICNNet.getNode'](49).api['CS.store'](dp_A2)

    DebugUniformAsker( sim.api['Topo.nodeIds'](), ip_A1, delta=11 ).install(None, sim.api)
    DebugUniformAsker( sim.api['Topo.nodeIds'](), ip_A2, delta=15 ).install(None, sim.api)

    def main():
        sim.api['Gui.start']()
    timeProfile('main()')















