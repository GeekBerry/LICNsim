import networkx

from core import *
from debug import *
from module import *
from module.guide_module import GuideModule
from module.loss_module import LossMonitor
from module.db_module import DBModule
from statistics_module import StatisticsModule
from unit.node import *
from debug import prcfile

sim = Simulator()
sim.install('hub', HubModule())
sim.install('guide', GuideModule())
sim.install('loss', LossMonitor())

sim.install('name_monitor', NameMonitor())
sim.install('node_monitor', NodeMonitor())
sim.install('edge_monitor', EdgeMonitor())
sim.install('log', LogModule())
sim.install('gui', GUIModule())

sim.install('db', DBModule(10))
sim.install('statistics', StatisticsModule())


graph = networkx.grid_2d_graph(9, 9)
sim.createGraph(graph, ExampleNode, OneStepChannel)

# 设置物理位置
for node_id in sim.nodes():
    x, y = node_id
    sim.node(node_id).pos = x * 100, y * 100

sim.node((4, 4)).store(dp_A)
sim.node((0, 0)).store(dp_A1)


import math
def uniformAsk(node_ids, packet):
    if random.random() < math.exp(-clock.time()/1000):
        node_id = random.choice(node_ids)
        sim.node(node_id).ask(packet.fission())


Loop(uniformAsk, list(sim.nodes()), ip_A)
Loop(uniformAsk, list(sim.nodes()), ip_A1)


# sim.showGUI()

# prcfile('sim.show()')

for i in range(1_000):
    clock.step()
sim.plotNames(ip_A.name, ip_A1.name)
sim.plotNodes((4,3), (4,4))
sim.showPlot()



