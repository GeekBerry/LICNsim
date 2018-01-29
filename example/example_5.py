
from core import INF, Packet, Name
from module import *
from unit.node import nodeFactory
from unit.channel import channelFactor
from module.db_module import DBModule
from statistics_module import StatisticsModule

sim = Simulator()
sim.install('hub', HubModule())
sim.install('name_monitor', NameMonitor())
sim.install('node_monitor', NodeMonitor())
sim.install('edge_monitor', EdgeMonitor())
sim.install('gui', GUIModule())
sim.install('log', LogModule())
# sim.install('db', DBModule(10))
# sim.install('statistics', StatisticsModule())


ServerNodeFactor = nodeFactory(
    node_type = "server", cs_capacity= 1000,
    replace_mode="FIFO", nonce_life_time= 10000,
    forward_rate= 1, forward_capacity= INF)

RouterNodeFactor = nodeFactory(
    node_type = "router", cs_capacity= 100,
    replace_mode="FIFO", nonce_life_time= 10000,
    forward_rate= 0.5, forward_capacity= INF)

ClientNodeFactor = nodeFactory(
    node_type = "client", nonce_life_time= 10000,
    forward_rate= 0.2, forward_capacity= INF)

WiredChannel= channelFactor(channel_type='wired', rate= 100, delay=1, loss=0)
WirelessChannel= channelFactor(channel_type='wireless', rate= 50, delay=2, loss=0.1)

sim.createGraph({'r1':['r2']}, RouterNodeFactor, WiredChannel)
sim.createGraph({'r1':['s1', 's2']}, ServerNodeFactor, WiredChannel)
sim.createGraph({'r2':['c1', 'c2']}, ClientNodeFactor, WirelessChannel)

from core import Loop

interest_a= Packet(Name('A'), Packet.INTEREST, 1)
data_a= Packet(Name('A'), Packet.DATA, 100)

interest_b= Packet(Name('B'), Packet.INTEREST, 1)
data_b= Packet(Name('B'), Packet.DATA, 100)

def askPacket(node_id, packet):
    sim.node(node_id).ask( packet.fission() )

sim.node('s1').store(data_a)
sim.node('s2').store(data_b)

Loop(askPacket, 'c1', interest_a, delta= 10)
Loop(askPacket, 'c2', interest_b, delta= 20)


if __name__ == '__main__' and 1:
    sim.showGUI()
#
#
# if __name__ == '__main__':
#     from core import clock
#     for i in range(10_000):
#         clock.step()
#
#     sim.plotNames(interest_a.name, interest_b.name)
#     sim.plotNodes('s1', 's2')
#     sim.showPlot()